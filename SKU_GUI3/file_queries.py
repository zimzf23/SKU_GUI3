from dependencies import *
import state

def find_files(ref_value,fcat,fsubcat):
    conn = pyodbc.connect(state.sku_conn_string)
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

def get_thumbnail(stream_id):
    # Connect
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor() 

    # Grab the level‑table metadata
    database = state.database
    table_cfg = config["tables"]["documents"]
    tbl_name  = table_cfg["name"]     # "ArticleDocuments"
    schema    = table_cfg["schema"]   # "dbo"
    fields    = table_cfg["fields"]   # ["a fuckton of fields"]

    streamid  = fields[0]  # "streamid"
    filestream  = fields[1]  # "streamid"
    
    # Query
    cursor.execute( f"""
        SELECT
            CAST([{filestream}] AS VARBINARY(MAX)) AS blobdata
        FROM [{database}].[{schema}].[{tbl_name}]
        WHERE [{streamid}] = ?
    """,stream_id)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None