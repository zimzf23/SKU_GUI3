from dependencies import *

# Global variables

# Global results

# Configuration
server_config = config['server']

server        = server_config['host'] + ',' + server_config['port']
database      = config['tables']['main_db']
username      = server_config['username']
password      = server_config['password']

sku_conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'