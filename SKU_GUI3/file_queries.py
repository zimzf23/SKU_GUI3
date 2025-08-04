from dependencies import *
from state import state

def find_files(ref_value,fcat,fsubcat):
    conn = pyodbc.connect(state.connection_string)
    cursor = conn.cursor() 

    # Grab the level‑table metadata
    database = state.database
    table_cfg = config["tables"]["file_index"]
    tbl_name  = table_cfg["name"]     # "ArticleFiles"
    schema    = table_cfg["schema"]   # "dbo"
    fields    = table_cfg["fields"]

    code_col  = fields[0]  # "Code"
    fcat_col = fields[1]  # "Fcat"
    fsubcat_col = fields[2]  # "Fsubcat"
    streamid_col = fields[3]  # "streamid"

    # Query
    query = f"""
        SELECT [{streamid_col}]
        FROM [{database}].[{schema}].[{tbl_name}]
        WHERE [{code_col}] = ?
        AND [{fcat_col}]   = ?
        AND [{fsubcat_col}]= ?
    """
    # Use clear keys in your dict:
    params = (
        ref_value,
        fcat,
        fsubcat
    )
    # Execute
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result if result else None
