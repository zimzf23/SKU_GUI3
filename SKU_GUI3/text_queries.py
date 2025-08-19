from dependencies import *
from state import state
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

def search(ref_value):
    # Connect
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    # Grab the level‑table metadata
    database = state.database
    table_cfg = config["tables"]["main"]
    tbl_name  = table_cfg["name"]     # "Main"
    schema    = table_cfg["schema"]   # "dbo"
    fields    = table_cfg["fields"]   # ["Code","Title","Description","Class","Type"]

    code_col  = fields[0]  # "Code"
    title_col = fields[1]  # "Title"
    description_col = fields[2]  # "Description"
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
    tbl_name  = table_cfg["name"]     # "Categories"
    schema    = table_cfg["schema"]   # "dbo"
    fields    = table_cfg["fields"]   # ["Type","Catno","Subcatno","Text"]

    type_col  = fields[0]  # "Type"
    catno_col = fields[1]  # "Catno"
    subcatno_col  = fields[2]  # "Subcatno"
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

def get_available_data(ref_val, item):
    conn = pyodbc.connect(state.sku_conn_string)
    cursor = conn.cursor()

    try:
        # Query ArticleIndex for most flags
        table_cfg = config["tables"]["Article_index"]
        tbl_name = table_cfg["name"]
        schema = table_cfg["schema"]
        code_col = table_cfg["fields"][0]
        fields = table_cfg["fields"][1:]  # Mechanical_Props, Electrical_Props, etc.
        query = f"""
            SELECT {', '.join([f'[{f}]' for f in fields])}
            FROM [{state.database}].[{schema}].[{tbl_name}]
            WHERE [{code_col}] = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.available.mechanical = row[0] or 0
            item.available.electrical = row[1] or 0
            item.available.shipping = row[2] or 0
            item.available.supplier = row[3] or 0
            item.available.finance = row[4] or 0
            item.available.certs = row[5] or 0
            item.available.enviromental = row[6] or 0  # Spelling as per data.toml

        # Query ExternalManufacturerData for external flag (as count of rows)
        ext_table_cfg = config["tables"]["ExternalManufacturer_data"]
        ext_tbl_name = ext_table_cfg["name"]
        ext_schema = ext_table_cfg["schema"]
        ext_code_col = "Code"  # From fields
        ext_query = f"""
            SELECT COUNT(*)
            FROM [{state.database}].[{ext_schema}].[{ext_tbl_name}]
            WHERE [{ext_code_col}] = ?
        """
        cursor.execute(ext_query, ref_val)
        ext_count = cursor.fetchone()[0]
        item.available.external = ext_count

        # Fetch data for each available section
        if item.available.external > 0:
            get_external_data(ref_val, item, cursor, conn)
        if item.available.mechanical > 0:
            get_mechanical_data(ref_val, item, cursor, conn)
        if item.available.electrical > 0:
            get_electrical_data(ref_val, item, cursor, conn)
        #if item.available.shipping > 0:
        #    get_shipping_data(ref_val, item, cursor, conn)
        #if item.available.supplier > 0:
        #    get_supplier_data(ref_val, item, cursor, conn)
        #if item.available.finance > 0:
        #    get_finance_data(ref_val, item, cursor, conn)
        #if item.available.certs > 0:
        #    get_certs_data(ref_val, item, cursor, conn)
        #if item.available.enviromental > 0:
        #    get_enviromental_data(ref_val, item, cursor, conn)
    except pyodbc.Error as e:
        print(f"Error fetching available data: {e}")
    finally:
        cursor.close()
        conn.close()

# Data fetching functions for each section (reusing cursor/conn where possible)

def get_external_data(ref_val, item, cursor, conn):
    try:
        table_cfg = config["tables"]["ExternalManufacturer_data"]
        tbl_name = table_cfg["name"]
        schema = table_cfg["schema"]
        code_col = table_cfg["fields"][-1]  # "Code" is last in fields
        query = f"""
            SELECT Manufacturer, Name, Number, Description, Ean
            FROM [{state.database}].[{schema}].[{tbl_name}]
            WHERE [{code_col}] = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.external_manufacturer.manufacturer = row[0] or ''
            item.external_manufacturer.name = row[1] or ''
            item.external_manufacturer.number = row[2] or ''
            item.external_manufacturer.description = row[3] or ''
            item.external_manufacturer.ean = row[4] or 0
    except pyodbc.Error as e:
        print(f"Error fetching external data: {e}")

def get_mechanical_data(ref_val, item, cursor, conn):
    try:
        table_cfg = config["tables"]["Mechanical_data"]
        tbl_name = table_cfg["name"]
        schema = table_cfg["schema"]
        code_col = "Code"  # Assuming Code links to ref_val (not in fields, add if needed)
        query = f"""
            SELECT Material, Treatment, Hardness
            FROM [{state.database}].[{schema}].[{tbl_name}]
            WHERE [{code_col}] = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.mechanical.material = row[0] or ''
            # Assuming Treatment is finish or similar
            item.mechanical.finish = row[1] or ''
            # Hardness might map to a custom field; adjust as needed
            # For other fields like weight, dimensions, color, shape, size: If not in table, set defaults or query another table
            # Example: item.mechanical.weight = 0.0  # If no data
    except pyodbc.Error as e:
        print(f"Error fetching mechanical data: {e}")

def get_electrical_data(ref_val, item, cursor, conn):
    try:
        table_cfg = config["tables"]["Electrical_data"]
        tbl_name = table_cfg["name"] 
        schema = table_cfg["schema"]
        code_col = "Code"  # Assume Code
        query = f"""
            SELECT Voltage, Intensity, Frequency
            FROM [{state.database}].[{schema}].[{tbl_name}]
            WHERE [{code_col}] = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.electrical.voltage = row[0] or 0.0
            item.electrical.current = row[1] or 0.0  # Intensity = current
            item.electrical.frequency = row[2] or 0.0
            # For power, phase, protection, efficiency: Set defaults or query elsewhere
    except pyodbc.Error as e:
        print(f"Error fetching electrical data: {e}")

def get_shipping_data(ref_val, item, cursor, conn):
    try:
        table_cfg = config["tables"]["Shipping_data"]
        tbl_name = table_cfg["name"]  # Note: config has "MechanicalData" – fix if typo
        schema = table_cfg["schema"]
        code_col = table_cfg["fields"][0]  # "Code"
        query = f"""
            SELECT Length, Width, Height, Country, HS
            FROM [{state.database}].[{schema}].[{tbl_name}]
            WHERE [{code_col}] = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            # Map to shipping_dimensions (e.g., "Length x Width x Height")
            item.shipping.shipping_dimensions = f"{row[0]} x {row[1]} x {row[2]}" or ''
            # shipping_method could map to Country or HS
            item.shipping.shipping_method = row[3] or ''
            # shipping_cost, shipping_weight: Set defaults or query elsewhere
    except pyodbc.Error as e:
        print(f"Error fetching shipping data: {e}")

def get_supplier_data(ref_val, item, cursor, conn):
    try:
        # Assuming supplier data is in a table like "SupplierData" – not in config, so placeholder
        # Adjust query based on actual table; for now, set defaults if no table
        # Example placeholder query (replace with real table/fields)
        query = f"""
            SELECT SupplierName, Contact, Phone, Email, Address
            FROM [YourDatabase].[dbo].[SupplierData]  # Replace with actual
            WHERE Code = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.supplier.supplier = row[0] or ''
            item.supplier.contact = row[1] or ''
            item.supplier.phone = row[2] or ''
            item.supplier.email = row[3] or ''
            item.supplier.address = row[4] or ''
    except pyodbc.Error as e:
        print(f"Error fetching supplier data: {e}")

def get_finance_data(ref_val, item, cursor, conn):
    try:
        # Placeholder for finance table (not in config)
        query = f"""
            SELECT Cost, Price, Margin, Currency, PaymentTerms
            FROM [YourDatabase].[dbo].[FinanceData]  # Replace with actual
            WHERE Code = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.finance.cost = row[0] or 0.0
            item.finance.price = row[1] or 0.0
            item.finance.margin = row[2] or 0.0
            item.finance.currency = row[3] or ''
            item.finance.payment_terms = row[4] or ''
    except pyodbc.Error as e:
        print(f"Error fetching finance data: {e}")

def get_certs_data(ref_val, item, cursor, conn):
    try:
        # Placeholder for certs table
        query = f"""
            SELECT Certifications, Compliance, Standards
            FROM [YourDatabase].[dbo].[CertificationsData]  # Replace with actual
            WHERE Code = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.certs.certifications = row[0] or ''
            item.certs.compliance = row[1] or ''
            item.certs.standards = row[2] or ''
    except pyodbc.Error as e:
        print(f"Error fetching certs data: {e}")

def get_enviromental_data(ref_val, item, cursor, conn):
    try:
        # Placeholder for enviromental table
        query = f"""
            SELECT CO2, Recyclable, Hazardous, DisposalInstructions
            FROM [YourDatabase].[dbo].[EnviromentalData]  # Replace with actual
            WHERE Code = ?
        """
        cursor.execute(query, ref_val)
        row = cursor.fetchone()
        if row:
            item.enviromental.CO2 = row[0] or 0
            item.enviromental.recyclable = row[1] or False
            item.enviromental.hazardous = row[2] or False
            item.enviromental.disposal_instructions = row[3] or ''
    except pyodbc.Error as e:
        print(f"Error fetching enviromental data: {e}")