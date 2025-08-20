from dependencies import *
from state import state

DOCS   = config["tables"]["documents"]
SCHEMA = DOCS["schema"]          # 'dbo'
TABLE  = DOCS["name"]            # 'ArticleDocuments'
F      = DOCS["fields"]

COL_NAME  = F[2]   # name
COL_PL    = F[3]   # path_locator (hierarchyid)
COL_PPL   = F[4]   # parent_path_locator (computed)
COL_FILE  = F[1]   # file_stream
COL_ISDIR = F[10]  # is_directory


def _folder_locator_under(conn, parent_pl_bin: bytes | None, child_name: str) -> bytes | None:
    """Return child's path_locator (VARBINARY) under parent (None => root)."""
    cur = conn.cursor()
    if parent_pl_bin is None:
        sql = f"""
            SELECT CONVERT(varbinary(892), [{COL_PL}])
            FROM [{SCHEMA}].[{TABLE}]
            WHERE [{COL_NAME}] = ? AND [{COL_ISDIR}] = 1 AND [{COL_PPL}] IS NULL
        """
        row = cur.execute(sql, (child_name,)).fetchone()
    else:
        sql = f"""
            SELECT CONVERT(varbinary(892), [{COL_PL}])
            FROM [{SCHEMA}].[{TABLE}]
            WHERE [{COL_NAME}] = ?
              AND [{COL_ISDIR}] = 1
              AND [{COL_PPL}] = CAST(CAST(? AS varbinary(max)) AS hierarchyid)
        """
        row = cur.execute(sql, (child_name, pyodbc.Binary(parent_pl_bin))).fetchone()
    cur.close()
    return row[0] if row else None

def _ensure_folder_under(conn, parent_pl_bin: bytes | None, folder_name: str) -> bytes:
    """Ensure a folder exists with given name under parent; create if missing."""
    existing = _folder_locator_under(conn, parent_pl_bin, folder_name)
    if existing:
        return existing

    cur = conn.cursor()
    if parent_pl_bin is None:
        sql = f"""
                DECLARE @parent hierarchyid = hierarchyid::GetRoot();
                DECLARE @new    hierarchyid = @parent.GetDescendant(
                  (SELECT MAX([{COL_PL}]) FROM [{SCHEMA}].[{TABLE}] WHERE [{COL_PPL}] = @parent),
                  NULL
                );
                INSERT INTO [{SCHEMA}].[{TABLE}] ([{COL_NAME}], [{COL_ISDIR}], [{COL_FILE}], [{COL_PL}])
                OUTPUT CONVERT(varbinary(892), inserted.[{COL_PL}])
                VALUES (?, 1, NULL, @new);
                """
        row = cur.execute(sql, (folder_name,)).fetchone()
    else:
        sql = f"""
                DECLARE @parent hierarchyid = CAST(CAST(? AS varbinary(max)) AS hierarchyid);
                DECLARE @new    hierarchyid = @parent.GetDescendant(
                  (SELECT MAX([{COL_PL}]) FROM [{SCHEMA}].[{TABLE}] WHERE [{COL_PPL}] = @parent),
                  NULL
                );
                INSERT INTO [{SCHEMA}].[{TABLE}] ([{COL_NAME}], [{COL_ISDIR}], [{COL_FILE}], [{COL_PL}])
                OUTPUT CONVERT(varbinary(892), inserted.[{COL_PL}])
                VALUES (?, 1, NULL, @new);
                """
        row = cur.execute(sql, (pyodbc.Binary(parent_pl_bin), folder_name)).fetchone()

    pl_bin = row[0]
    cur.close()
    conn.commit()
    return pl_bin

def insert_file_under_code(
    conn_string: str,
    code: str,
    file_name: str,
    data: bytes,
    folder: str | None = None,
    overwrite: bool = False,
):
    """
    Insert a file into \\SKUs\\<code>\\[<folder>].

    - If folder is None or "", the file is placed directly under \\SKUs\\<code>\\.
    - Ensures <code> (and <folder>, if given) exist. SKUs is assumed to exist at root.
    - If overwrite=True and a file with the same name exists, it is removed first.
    """
    conn = pyodbc.connect(conn_string)
    try:
        # 1) SKUs under root
        skus_pl = _folder_locator_under(conn, None, "SKUs")
        if not skus_pl:
            raise FileNotFoundError(r"Missing folder: \\SKUs\\")

        # 2) ensure <code>
        code_pl = _ensure_folder_under(conn, skus_pl, code)

        # 3) resolve target (code folder or subfolder)
        target_pl = code_pl
        if folder and folder.strip():
            target_pl = _ensure_folder_under(conn, code_pl, folder.strip())

        cur = conn.cursor()

        # 4) if overwrite: delete existing file with same name under target folder
        if overwrite:
            sql_del = f"""
                        DELETE FROM [{SCHEMA}].[{TABLE}]
                        WHERE [{COL_NAME}] = ?
                          AND [{COL_ISDIR}] = 0
                          AND [{COL_PPL}] = CAST(CAST(? AS varbinary(max)) AS hierarchyid);
                        """
            cur.execute(sql_del, (file_name, pyodbc.Binary(target_pl)))
            conn.commit()

        # 5) insert file
        sql_ins = f"""
                    DECLARE @parent hierarchyid = CAST(CAST(? AS varbinary(max)) AS hierarchyid);
                    DECLARE @new    hierarchyid = @parent.GetDescendant(
                      (SELECT MAX([{COL_PL}]) FROM [{SCHEMA}].[{TABLE}] WHERE [{COL_PPL}] = @parent),
                      NULL
                    );
                    INSERT INTO [{SCHEMA}].[{TABLE}] ([{COL_NAME}], [{COL_FILE}], [{COL_ISDIR}], [{COL_PL}])
                    VALUES (?, ?, 0, @new);
                    """
        cur.execute(sql_ins, (pyodbc.Binary(target_pl), file_name, pyodbc.Binary(data)))
        conn.commit()
        cur.close()
    finally:
        conn.close()