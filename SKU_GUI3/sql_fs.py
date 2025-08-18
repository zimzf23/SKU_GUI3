from dependencies import *
from state import state
import state
CHUNK_SIZE = 2 * 1024 * 1024  # 2 MiB chunks (tune as you like)

def create_folder(folder_name, parent_name=None, ensure_parent=True):
    # Connect
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    # Table metadata
    database = state.database
    table_cfg = config["tables"]["documents"]
    tbl_name  = table_cfg["name"]    # FileTable name, e.g., 'ArticleDocuments'
    schema    = table_cfg["schema"]  # e.g., 'dbo'

    # Ensure DB context for FileTableRootPath(...)
    cursor.execute(f"USE [{database}]")

    root_expr = f"GetPathLocator(FileTableRootPath('{schema}.{tbl_name}'))"

    def _exists_under(parent_locator_str, name):
        """Return child's locator string if it exists (None=root), else None."""
        if parent_locator_str is None:
            # ROOT: match both NULL and explicit root locator
            cursor.execute(f"""
                SELECT path_locator.ToString()
                FROM [{schema}].[{tbl_name}]
                WHERE is_directory = 1 AND name = ?
                  AND (parent_path_locator IS NULL OR parent_path_locator = {root_expr});
            """, name)
        else:
            cursor.execute(f"""
                SELECT path_locator.ToString()
                FROM [{schema}].[{tbl_name}]
                WHERE is_directory = 1 AND name = ?
                  AND parent_path_locator = hierarchyid::Parse(?);
            """, (name, parent_locator_str))
        row = cursor.fetchone()
        return row[0] if row else None

    def _insert_under(parent_locator_str, name):
        """Create folder under given parent (None=root); return locator string."""
        if parent_locator_str is None:
            # ROOT insert
            cursor.execute(f"""
                DECLARE @parent hierarchyid = hierarchyid::GetRoot();
                DECLARE @lastChild hierarchyid =
                    (SELECT MAX(path_locator)
                     FROM [{schema}].[{tbl_name}]
                     WHERE parent_path_locator = @parent OR parent_path_locator IS NULL);

                DECLARE @new hierarchyid = @parent.GetDescendant(@lastChild, NULL);

                INSERT INTO [{schema}].[{tbl_name}] (name, is_directory, file_stream, path_locator)
                OUTPUT inserted.path_locator.ToString()
                VALUES (?, 1, NULL, @new);
            """, name)
        else:
            # Non-root insert
            cursor.execute(f"""
                DECLARE @parent hierarchyid = hierarchyid::Parse(?);
                DECLARE @lastChild hierarchyid =
                    (SELECT MAX(path_locator)
                     FROM [{schema}].[{tbl_name}]
                     WHERE parent_path_locator = @parent);

                DECLARE @new hierarchyid = @parent.GetDescendant(@lastChild, NULL);

                INSERT INTO [{schema}].[{tbl_name}] (name, is_directory, file_stream, path_locator)
                OUTPUT inserted.path_locator.ToString()
                VALUES (?, 1, NULL, @new);
            """, (parent_locator_str, name))
        row = cursor.fetchone()
        return row[0] if row else None

    # -------- ensure parent (get locator string) --------
    if parent_name is None:
        parent_loc_str = None  # root
    else:
        parent_loc_str = _exists_under(None, parent_name)
        if not parent_loc_str:
            if not ensure_parent:
                cursor.close(); conn.close()
                raise ValueError(f"Parent folder '{parent_name}' not found at root.")
            parent_loc_str = _insert_under(None, parent_name)

    # -------- ensure child under parent --------
    child_loc_str = _exists_under(parent_loc_str, folder_name)
    if not child_loc_str:
        child_loc_str = _insert_under(parent_loc_str, folder_name)

    conn.commit()
    cursor.close()
    conn.close()




def insert_to_folder(upload_event, code: str, forced_name: str | None = None):
    """
    Insert an uploaded file into FileTable path: SKUs/<code>.
    Uses state.sku_conn_string. Overwrites an existing file with the same name.

    forced_name behavior:
      - None  -> keep uploaded name.
      - No extension -> use 'forced_name.<upload_ext>' if the upload has one.
      - With extension -> use as-is.
    Returns: stream_id (GUID as str)
    """
    # --- derive final filename ---
    upload_ext = Path(upload_event.name).suffix.lstrip('.').lower()
    if forced_name is None:
        final_name = upload_event.name
    else:
        fext = Path(forced_name).suffix.lstrip('.').lower()
        final_name = forced_name if fext else (f"{forced_name}.{upload_ext}" if upload_ext else forced_name)

    # read entire content (FILESTREAM requires full-value set, not .WRITE)
    content_bytes = upload_event.content.read()

    # --- connect ---
    conn = pyodbc.connect(state.sku_conn_string)
    cur  = conn.cursor()

    # table metadata
    database = state.database
    table_cfg = config["tables"]["documents"]
    tbl_name  = table_cfg["name"]     # FileTable name
    schema    = table_cfg["schema"]   # e.g. 'dbo'

    # ensure DB context (for FileTableRootPath)
    cur.execute(f"USE [{database}]")
    root_expr = f"GetPathLocator(FileTableRootPath('{schema}.{tbl_name}'))"

    # ---------- helpers ----------
    def _ensure_folder_under(parent_loc_str, name: str) -> str:
        """Return folder locator string (hierarchyid.ToString()); create if missing."""
        if parent_loc_str is None:
            # root: check both NULL and explicit root
            cur.execute(f"""
                SELECT path_locator.ToString()
                FROM [{schema}].[{tbl_name}]
                WHERE is_directory = 1 AND name = ?
                  AND (parent_path_locator IS NULL OR parent_path_locator = {root_expr});
            """, name)
            row = cur.fetchone()
            if row:
                return row[0]
            # create at root
            cur.execute(f"""
                DECLARE @parent hierarchyid = hierarchyid::GetRoot();
                DECLARE @last hierarchyid =
                    (SELECT MAX(path_locator)
                     FROM [{schema}].[{tbl_name}]
                     WHERE parent_path_locator = @parent OR parent_path_locator IS NULL);
                DECLARE @new hierarchyid = @parent.GetDescendant(@last, NULL);

                INSERT INTO [{schema}].[{tbl_name}] (name, is_directory, file_stream, path_locator)
                OUTPUT inserted.path_locator.ToString()
                VALUES (?, 1, 0x, @new);
            """, name)
            return cur.fetchone()[0]
        else:
            # under explicit parent
            cur.execute(f"""
                SELECT path_locator.ToString()
                FROM [{schema}].[{tbl_name}]
                WHERE is_directory = 1 AND name = ?
                  AND parent_path_locator = hierarchyid::Parse(?);
            """, (name, parent_loc_str))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(f"""
                DECLARE @parent hierarchyid = hierarchyid::Parse(?);
                DECLARE @last hierarchyid =
                    (SELECT MAX(path_locator)
                     FROM [{schema}].[{tbl_name}]
                     WHERE parent_path_locator = @parent);
                DECLARE @new hierarchyid = @parent.GetDescendant(@last, NULL);

                INSERT INTO [{schema}].[{tbl_name}] (name, is_directory, file_stream, path_locator)
                OUTPUT inserted.path_locator.ToString()
                VALUES (?, 1, 0x, @new);
            """, (parent_loc_str, name))
            return cur.fetchone()[0]

    # ---------- ensure SKUs/<code> exists ----------
    skus_loc = _ensure_folder_under(None, "SKUs")
    code_loc = _ensure_folder_under(skus_loc, code)

    # ---------- overwrite same-name file if present ----------
    cur.execute(f"""
        SELECT stream_id
        FROM [{schema}].[{tbl_name}]
        WHERE is_directory = 0
          AND name = ?
          AND parent_path_locator = hierarchyid::Parse(?);
    """, (final_name, code_loc))
    row = cur.fetchone()

    if row:
        # update: set full FILESTREAM value in one shot
        stream_id = str(row[0])
        cur.setinputsizes([(pyodbc.SQL_VARBINARY, 0, 0), (pyodbc.SQL_GUID, 0, 0)])
        cur.execute(f"""
            UPDATE [{schema}].[{tbl_name}]
            SET file_stream = ?
            WHERE stream_id = ?;
        """, (pyodbc.Binary(content_bytes), stream_id))
    else:
        # insert: create node and set file_stream with single value
        cur.execute(f"""
            DECLARE @parent hierarchyid = hierarchyid::Parse(?);
            DECLARE @last hierarchyid =
                (SELECT MAX(path_locator)
                 FROM [{schema}].[{tbl_name}]
                 WHERE parent_path_locator = @parent);
            DECLARE @new hierarchyid = @parent.GetDescendant(@last, NULL);

            INSERT INTO [{schema}].[{tbl_name}] (name, is_directory, file_stream, path_locator)
            OUTPUT inserted.stream_id
            VALUES (?, 0, ?, @new);
        """, (code_loc, final_name, pyodbc.Binary(content_bytes)))
        stream_id = str(cur.fetchone()[0])

    conn.commit()
    cur.close()
    conn.close()
    return stream_id