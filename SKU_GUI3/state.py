from dependencies import *

# Reactive state holder

class State:
    def __init__(self, ref: str = "W-0X00-0000"):
        self._current_ref = ref
        self._subs: list[callable] = []

    @property
    def current_ref(self):
        return self._current_ref

    @current_ref.setter
    def current_ref(self, v: str):
        self._current_ref = v
        ui.update()
        for fn in self._subs:
            try:
                fn(v)
            except Exception:
                pass

    def subscribe(self, fn: callable):
        self._subs.append(fn)

    def set_ref(self, v: str):
        self.current_ref = v

state = State()


# Global results

# Configuration
server_config = config['server']

server        = server_config['host'] + ',' + server_config['port']
database      = config['tables']['main_db']
username      = server_config['username']
password      = server_config['password']

sku_conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
