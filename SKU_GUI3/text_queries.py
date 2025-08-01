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

def get_cat_text(dec_vals):
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    # Grab the level‑table metadata
    database = state.database
    table_cfg = config["tables"]["categories"]
    tbl_name  = table_cfg["name"]     # "Level"
    schema    = table_cfg["schema"]   # "dbo"
    fields    = table_cfg["fields"]   # ["Level","Text"]

    type_col  = fields[0]  # "Level"
    catno_col = fields[1]  # "Text"
    subcatno_col  = fields[2]  # "Level"
    text_col = fields[3]  # "Text"

    # Build the SQL dynamically
    query = f"""
        SELECT TOP 1
            [{text_col}]
        FROM [{database}].[{schema}].[{tbl_name}]
        WHERE [{type_col}]    = ?
        AND [{catno_col}]   = ?
        AND [{subcatno_col}]= ?
    """
    # Use clear keys in your dict:
    params = (
        dec_vals['Type'],
        dec_vals['Cat'],
        dec_vals['Subcat']
    )
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    # row will be None if no match; otherwise row[0] is your [Text]
    #print(str(result[0]))
    return result[0] if result[0] else None

def get_level_text(dec_vals):
    # Connect
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    # Grab the level‑table metadata
    database = state.database
    table_cfg = config["tables"]["level"]
    tbl_name  = table_cfg["name"]     # "Level"
    schema    = table_cfg["schema"]   # "dbo"
    fields    = table_cfg["fields"]   # ["Level","Text"]
    key_col  = fields[0]  # "Level"
    text_col = fields[1]  # "Text"

    # Query
    query = f"""
        SELECT TOP 1
            [{text_col}]
        FROM [{database}].[{schema}].[{tbl_name}]
        WHERE [{key_col}] = ?
    """
    # Execute
    params = (dec_vals['Level'])
    cursor.execute(query, params)
    # Fetch and close
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result[0] is None: return None
    #print(str(result[0]))
    return result[0]