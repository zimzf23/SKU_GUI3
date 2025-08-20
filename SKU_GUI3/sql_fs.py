from dependencies import *
from state import state
CHUNK_SIZE = 2 * 1024 * 1024  # 2 MiB chunks (tune as you like)

def _use_db(cur) -> None:
    cur.execute(f"USE [{state.database}]")

def _get_filetable_root(cur, schema: str, tbl: str) -> str:
    """Return FileTable root locator as string (hierarchyid.ToString())."""
    cur.execute(
        f"SELECT CAST(GetPathLocator(FileTableRootPath('{schema}.{tbl}')).ToString() AS NVARCHAR(4000))"
    )
    return cur.fetchone()[0]  # e.g. '/1/'

def _ensure_folder_under(cur, schema: str, tbl: str, parent_loc: str, name: str) -> str:
    """
    Ensure a directory named `name` exists directly under `parent_loc` (hierarchyid string).
    Returns child's locator string.
    """
    # Exists?
    cur.execute(f"""
        SELECT path_locator.ToString()
        FROM [{schema}].[{tbl}]
        WHERE is_directory = 1
          AND name = ?
          AND parent_path_locator = hierarchyid::Parse(?);
    """, (name, parent_loc))
    row = cur.fetchone()
    if row:
        return row[0]

    # Create
    cur.execute(f"""
        DECLARE @parent hierarchyid = hierarchyid::Parse(?);
        DECLARE @last   hierarchyid =
            (SELECT MAX(path_locator) FROM [{schema}].[{tbl}] WHERE parent_path_locator = @parent);
        DECLARE @new    hierarchyid = @parent.GetDescendant(@last, NULL);

        INSERT INTO [{schema}].[{tbl}] (name, is_directory, file_stream, path_locator)
        OUTPUT inserted.path_locator.ToString()
        VALUES (?, 1, 0x, @new);
    """, (parent_loc, name))
    return cur.fetchone()[0]

def _ensure_path(cur, schema: str, tbl: str, segments: List[str]) -> str:
    """
    Ensure nested folders under FileTable root given by `segments`.
    segments[0] is created under FileTable root; subsequent segments under their parent.
    Returns locator string of the deepest segment.
    """
    root = _get_filetable_root(cur, schema, tbl)
    parent = root
    for seg in segments:
        parent = _ensure_folder_under(cur, schema, tbl, parent, seg)
    return parent  # locator of deepest folder

def _iter_files(e) -> List[Any]:
    files = getattr(e, "files", None)
    return list(files) if files is not None else [e]

def cache_upload(e, *, kind: str = "external") -> None:
    staged: Dict[str, List[Any]] = getattr(state, "pending_uploads", {})
    files = _iter_files(e)
    if kind == "thumbnail":
        last = files[-1]
        staged[kind] = [last]
        ui.notify(f"Staged {kind}: {last.name}", type="positive")
    else:
        bucket = staged.setdefault(kind, [])
        bucket.extend(files)
        ui.notify(f"Staged {kind}: {', '.join(f.name for f in files)}", type="positive")
    state.pending_uploads = staged

def commit_uploads(*,
                   kind: str = "external",
                   forced_name: Optional[str] = None,
                   subfolder: Optional[str] = None) -> tuple[int, int]:
    """
    Commit staged uploads for `kind`.
    Returns (successes, failures).
    """
    staged: Dict[str, List[Any]] = getattr(state, "pending_uploads", {})
    files = staged.get(kind, [])
    if not files:
        return (0, 0)

    successes = 0
    failures = 0

    for ev in files:
        try:
            fn = forced_name
            if forced_name and "." not in forced_name:
                _, ext = os.path.splitext(ev.name)
                ext = ext.lstrip(".").lower() or "jpg"
                fn = f"{forced_name}.{ext}"
            insert_to_folder(ev, code=state.current_ref, forced_name=fn, subfolder=subfolder)
            successes += 1
        except Exception as ex:
            failures += 1
            try:
                ui.notify(f"Failed {kind}: {ev.name} → {ex}", type="negative")
            except:
                pass

    staged[kind] = []
    state.pending_uploads = staged
    return (successes, failures)

def create_folder(*segments: str) -> str:
    """
    Ensure a nested path exists under the FileTable root.
    Example:
        create_folder("SKUs", "W-0E21-0002", "Datos Externos")
    Will ensure:
        <FileTableRoot>/SKUs/W-0E21-0002/Datos Externos
    Returns locator string of the deepest folder.
    """
    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        _use_db(cur)  # switch to correct DB
        tbl_cfg = config["tables"]["documents"]
        schema  = tbl_cfg["schema"]
        tbl     = tbl_cfg["name"]

        return _ensure_path(cur, schema, tbl, list(segments))
    finally:
        try: cur.close(); conn.close()
        except: pass

def insert_to_folder(upload_event,
                     code: str,
                     forced_name: Optional[str] = None,
                     subfolder: Optional[str] = None) -> str:
    """
    Write file to <FileTableRoot> / SKUs / <code> [/ <subfolder>] / <final_name>.
    Overwrites if a file with the same name exists.
    Returns stream_id (as string).
    """
    upload_ext = Path(upload_event.name).suffix.lstrip('.').lower()
    if forced_name is None:
        final_name = upload_event.name
    else:
        fext = Path(forced_name).suffix.lstrip('.').lower()
        final_name = forced_name if fext else (f"{forced_name}.{upload_ext}" if upload_ext else forced_name)

    content_bytes = upload_event.content.read()

    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        _use_db(cur)
        tbl_cfg = config["tables"]["documents"]
        schema  = tbl_cfg["schema"]
        tbl     = tbl_cfg["name"]

        # Ensure path: SKUs / code [/ subfolder]
        path_segments = ["SKUs", code] + ([subfolder] if subfolder else [])
        parent_loc = _ensure_path(cur, schema, tbl, path_segments)

        # If a FOLDER with same name exists under parent → error out clearly
        cur.execute(f"""
            SELECT is_directory
            FROM [{schema}].[{tbl}]
            WHERE name = ? AND parent_path_locator = hierarchyid::Parse(?);
        """, (final_name, parent_loc))
        r = cur.fetchone()
        if r and r[0] == 1:
            raise ValueError(f"'{final_name}' already exists as a folder under the target path.")

        # Overwrite if file exists
        cur.execute(f"""
            SELECT stream_id
            FROM [{schema}].[{tbl}]
            WHERE is_directory = 0
              AND name = ?
              AND parent_path_locator = hierarchyid::Parse(?);
        """, (final_name, parent_loc))
        row = cur.fetchone()

        if row:
            stream_id = str(row[0])
            cur.setinputsizes([(pyodbc.SQL_VARBINARY, 0, 0), (pyodbc.SQL_GUID, 0, 0)])
            cur.execute(f"""
                UPDATE [{schema}].[{tbl}]
                SET file_stream = ?
                WHERE stream_id = ?;
            """, (pyodbc.Binary(content_bytes), stream_id))
        else:
            # New file under parent
            cur.execute(f"""
                DECLARE @parent hierarchyid = hierarchyid::Parse(?);
                DECLARE @last   hierarchyid =
                    (SELECT MAX(path_locator)
                       FROM [{schema}].[{tbl}]
                      WHERE parent_path_locator = @parent);
                DECLARE @new    hierarchyid = @parent.GetDescendant(@last, NULL);

                INSERT INTO [{schema}].[{tbl}] (name, is_directory, file_stream, path_locator)
                OUTPUT inserted.stream_id
                VALUES (?, 0, ?, @new);
            """, (parent_loc, final_name, pyodbc.Binary(content_bytes)))
            stream_id = str(cur.fetchone()[0])

        conn.commit()
        return stream_id
    finally:
        try: cur.close(); conn.close()
        except: pass
