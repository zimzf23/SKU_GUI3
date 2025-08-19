from dependencies import *
from state import state
from data import catalog

def get_current_item():
    ref = (state.current_ref or "").strip()
    if not ref:
        return None
    return catalog.get_or_create(ref)

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
    """Ensure <root>/SKUs/<parent_name>/<folder_name> exists in the FileTable."""
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()
    try:
        database = state.database
        table_cfg = config["tables"]["documents"]
        tbl_name  = table_cfg["name"]
        schema    = table_cfg["schema"]

        cursor.execute(f"USE [{database}]")

        # Get FileTable root path_locator as string (fix -151 HY106)
        cursor.execute(
            f"SELECT CAST(GetPathLocator(FileTableRootPath('{schema}.{tbl_name}')).ToString() AS NVARCHAR(4000))"
        )
        root_loc = cursor.fetchone()[0]

        def exists_under(parent_loc_str, name):
            if parent_loc_str is None:  # root case
                cursor.execute(f"""
                    SELECT path_locator.ToString()
                    FROM [{schema}].[{tbl_name}]
                    WHERE is_directory = 1 AND name = ?
                      AND (parent_path_locator IS NULL OR parent_path_locator = hierarchyid::GetRoot());
                """, (name,))
            else:
                cursor.execute(f"""
                    SELECT path_locator.ToString()
                    FROM [{schema}].[{tbl_name}]
                    WHERE is_directory = 1 AND name = ?
                      AND parent_path_locator = hierarchyid::Parse(?);
                """, (name, parent_loc_str))
            row = cursor.fetchone()
            return row[0] if row else None


        def insert_under(parent_loc_str, name):
            parent = root_loc if parent_loc_str is None else parent_loc_str
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
            """, (parent, name))
            return cursor.fetchone()[0]

        # Chain: SKUs → parent_name (e.g. Code) → folder_name (Datos Externos)
        current = None
        for segment in ('SKUs', parent_name, folder_name):
            loc = exists_under(current, segment)
            if not loc:
                loc = insert_under(current, segment)
            current = loc

        conn.commit()
        return current

    finally:
        try:
            cursor.close(); conn.close()
        except:
            pass


def upsert_external(item):
    """Update existing row by Code; insert if it doesn't exist."""
    # Connect
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    try:
        table_cfg = config["tables"]["ExternalManufacturer_data"]
        tbl_name = table_cfg["name"]
        schema   = table_cfg["schema"]
        cols     = table_cfg["fields"]          # ["Manufacturer","Name","Number","Description","Ean","Code"]
        code_col = cols[-1]
        set_cols = [c for c in cols if c != code_col]

        man = (item.external_manufacturer.manufacturer or '').strip() or None
        name = (item.external_manufacturer.name or '').strip() or None
        number = (item.external_manufacturer.number or '').strip() or None
        desc = (item.external_manufacturer.description or '').strip() or None
        ref_val = (state.current_ref or "").strip()
        ean_raw = item.external_manufacturer.ean
        try:
            ean = int(ean_raw) if str(ean_raw).strip() != '' else None
        except (TypeError, ValueError):
            ean = None

        values_by_col = {
            "Manufacturer": man,
            "Name": name,
            "Number": number,
            "Description": desc,
            "Ean": ean,
            code_col: ref_val,
        }

        # 1) Try UPDATE
        upd_sql = (
            f"UPDATE [{state.database}].[{schema}].[{tbl_name}] SET "
            + ", ".join(f"[{c}] = ?" for c in set_cols)
            + f" WHERE [{code_col}] = ?"
        )
        upd_params = [values_by_col[c] for c in set_cols] + [ref_val]
        cursor.execute(upd_sql, upd_params)

        # 2) If no row updated, INSERT
        if cursor.rowcount == 0:
            col_list = ", ".join(f"[{c}]" for c in cols)
            placeholders = ", ".join("?" for _ in cols)
            ins_sql = f"INSERT INTO [{state.database}].[{schema}].[{tbl_name}] ({col_list}) VALUES ({placeholders})"
            ins_params = [values_by_col[c] for c in cols]
            cursor.execute(ins_sql, ins_params)

        conn.commit()
        return True

    except pyodbc.Error as e:
        conn.rollback()
        print(f"Error upserting external data: {e}")
        return False