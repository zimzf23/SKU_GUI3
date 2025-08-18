from dependencies import *
import state

def get_level_options():
    """Return {label: value} for NiceGUI where value is Level number."""
    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        tcfg = config["tables"]["level"]
        schema, table = tcfg["schema"], tcfg["name"]
        key_col, text_col = tcfg["fields"]

        q = f"""
            SELECT [{key_col}], [{text_col}]
            FROM [{state.database}].[{schema}].[{table}]
            WHERE [{text_col}] IS NOT NULL
              AND [{text_col}] <> ''
            ORDER BY [{key_col}]
        """
        cur.execute(q)
        rows = cur.fetchall()
        # Flip order so NiceGUI shows text, returns number
        return {row[0]: row[1] for row in rows}

    finally:
        cur.close()
        conn.close()

def get_type_options():
    """
    Return {value -> label} for NiceGUI.
    value = Type (number)
    label = Text
    """
    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        tcfg = config["tables"]["categories"]
        schema, table = tcfg["schema"], tcfg["name"]
        type_col, catno_col, subcatno_col, text_col = tcfg["fields"]

        q = f"""
            SELECT [{type_col}], [{text_col}]
            FROM [{state.database}].[{schema}].[{table}]
            WHERE [{catno_col}] = 0
              AND [{subcatno_col}] = 0
              AND [{text_col}] IS NOT NULL
              AND [{text_col}] <> ''
            ORDER BY [{type_col}]
        """
        cur.execute(q)
        rows = cur.fetchall()

        # NiceGUI expects {value -> label}
        return {row[0]: row[1] for row in rows}
    finally:
        cur.close()
        conn.close()

def get_cat_options(Type):
    """
    Return {value -> label} for NiceGUI.
    value = Type (number)
    label = Text
    """
    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        tcfg = config["tables"]["categories"]
        schema, table = tcfg["schema"], tcfg["name"]
        type_col, catno_col, subcatno_col, text_col = tcfg["fields"]

        q = f"""
            SELECT [{catno_col}], [{text_col}]
            FROM [{state.database}].[{schema}].[{table}]
            WHERE [{type_col}] = ?
              AND [{catno_col}] <> 0
              AND [{subcatno_col}] = 0
              AND [{text_col}] IS NOT NULL
              AND [{text_col}] <> 'Vacío'
            ORDER BY [{catno_col}]
        """

        params =(Type)
        cur.execute(q,params)
        rows = cur.fetchall()

        # NiceGUI expects {value -> label}
        return {row[0]: row[1] for row in rows}
    finally:
        cur.close()
        conn.close()

def get_subcat_options(Type,Cat):
    """
    Return {value -> label} for NiceGUI.
    value = Type (number)
    label = Text
    """
    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        tcfg = config["tables"]["categories"]
        schema, table = tcfg["schema"], tcfg["name"]
        type_col, catno_col, subcatno_col, text_col = tcfg["fields"]

        q = f"""
            SELECT [{subcatno_col}], [{text_col}]
            FROM [{state.database}].[{schema}].[{table}]
            WHERE [{type_col}] = ?
              AND [{catno_col}] = ?
              AND [{subcatno_col}] <> '0'
              AND [{text_col}] IS NOT NULL
              AND [{text_col}] <> 'Vacío'
            ORDER BY [{subcatno_col}]
        """

        params =(Type,Cat)
        cur.execute(q,params)
        rows = cur.fetchall()

        # NiceGUI expects {value -> label}
        return {row[0]: row[1] for row in rows}
    finally:
        cur.close()
        conn.close()

def get_next_code_number(prefix: str):
    """
    Given a prefix like 'W-0M12-', find the highest 4-digit suffix in Code
    and return the next available number (int).
    Returns 0 if none found.
    """
    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        database = state.database
        tcfg = config["tables"]["main"]
        schema, table = tcfg["schema"], tcfg["name"]
        code_col = tcfg["fields"][0]  # Code column

        query = f"""
            SELECT MAX(CAST(RIGHT([{code_col}], 4) AS INT))
            FROM [{database}].[{schema}].[{table}]
            WHERE [{code_col}] LIKE ?
        """
        cur.execute(query, (prefix + '%',))
        row = cur.fetchone()
        max_number = row[0] if row and row[0] is not None else 0
        next_num = max_number + 1
        return f'{next_num:04d}'
    finally:
        cur.close()
        conn.close()

def insert_new(code: str, title: str, desc: str, clase: int, tipo: int):
    """
    Insert a new row into dbo.Main and return the inserted ID.
    Expects config["tables"]["main"]["fields"] == [Code, Title, Description, Class, Type]
    """
    conn = pyodbc.connect(state.sku_conn_string)
    cur = conn.cursor()
    try:
        database = state.database
        tcfg = config["tables"]["main"]
        schema, table = tcfg["schema"], tcfg["name"]
        code_col, title_col, desc_col, class_col, type_col = tcfg["fields"]

        # (Optional) guard against duplicates by Code
        cur.execute(f"""
            SELECT 1
            FROM [{database}].[{schema}].[{table}]
            WHERE [{code_col}] = ?
        """, (code,))
        if cur.fetchone():
            raise ValueError(f"Code already exists: {code}")

        # Insert and return new ID (assumes 'id' is IDENTITY)
        cur.execute(f"""
            INSERT INTO [{database}].[{schema}].[{table}]
                ([{code_col}], [{title_col}], [{desc_col}], [{class_col}], [{type_col}])
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?)
        """, (code, title, desc, clase, tipo))

        new_id = cur.fetchone()[0]  # may be None if OUTPUT not supported
        conn.commit()
        return new_id
    finally:
        cur.close()
        conn.close()


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
