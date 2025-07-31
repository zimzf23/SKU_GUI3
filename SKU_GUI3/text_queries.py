from dependencies import *
import state
from data import catalog

def search(ref_value):
    # Connect
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    # Grab the level‑table metadata
    database = state.database
    table_cfg = config["tables"]["main"]
    tbl_name  = table_cfg["name"]     # "Level"
    schema    = table_cfg["schema"]   # "dbo"
    fields    = table_cfg["fields"]   # ["Level","Text"]

    code_col  = fields[0]  # "Level"
    title_col = fields[1]  # "Text"
    description_col = fields[2]  # "Text"
    class_col = fields[3]  # "Class"
    type_col  = fields[4]  # "Type"
    # Query
    query = f"""
        SELECT TOP 1
            [{code_col}],
            [{title_col}],
            [{description_col}],
            [{class_col}],
            [{type_col}]
        FROM [{database}].[{schema}].[{tbl_name}]
        WHERE [{code_col}] = ?
    """
    # Execute
    cursor.execute(query, ref_value)
    row = cursor.fetchone()
    # capture the column names **before** closing
    #columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()

    if row:
        # Create or update the item in the catalog
        item = catalog.get_or_create(ref_value)
        # Populate the basic data
        item.basic.ref          = row[0] or ''
        item.basic.name         = row[1] or ''
        item.basic.description  = row[2] or ''
        item.basic.cls          = row[3] or 0
        item.basic.type         = row[4] or 0