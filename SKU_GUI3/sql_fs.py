from dependencies import *
from state import state

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