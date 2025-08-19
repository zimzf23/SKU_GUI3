from dependencies import *
from state import state

def get_thumbnail(ref_val):
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    database = state.database
    table_cfg = config["tables"]["documents"]   # FILETABLE
    tbl_name  = table_cfg["name"]
    schema    = table_cfg["schema"]

    cursor.execute(f"USE [{database}]")

    cursor.execute(f"""
        WITH roots AS (
          SELECT hierarchyid::GetRoot() AS root
        ),
        skus AS (
          SELECT t.path_locator
          FROM [{schema}].[{tbl_name}] t, roots
          WHERE t.is_directory=1 AND t.name='SKUs'
            AND (t.parent_path_locator IS NULL OR t.parent_path_locator = roots.root)
        ),
        code AS (
          SELECT t.path_locator
          FROM [{schema}].[{tbl_name}] t, skus
          WHERE t.is_directory=1 AND t.name=?
            AND t.parent_path_locator = skus.path_locator
        )
        SELECT TOP 1 file_stream, RIGHT(t.name, LEN(t.name)-CHARINDEX('.', t.name))
        FROM [{schema}].[{tbl_name}] t, code
        WHERE t.parent_path_locator = code.path_locator
          AND t.is_directory=0
          AND t.name LIKE 'Thumbnail.%';
    """, ref_val)

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        blob, ext = row
        return blob, ext.lower()
    else:
        return None, None
