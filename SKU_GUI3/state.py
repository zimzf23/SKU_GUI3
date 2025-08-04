from dependencies import *

# Reactive state holder
class State:
    def __init__(self, ref: str = "W-0X00-0000"):
        self._current_ref = ref
        self._subs: list[callable] = []
        
        # Visibility flags for content cards (reactive)
        self._external_visible = True
        self._mechanical_visible = True
        self._electrical_visible = True
        self._shipping_visible = True
        self._supplier_visible = True
        self._finance_visible = True
        self._certs_visible = True
        self._enviromental_visible = True  # Note: Consistent spelling as 'enviromental' from data.toml

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

    # Visibility properties
    @property
    def external_visible(self):
        return self._external_visible

    @external_visible.setter
    def external_visible(self, v: bool):
        self._external_visible = v
        ui.update()

    @property
    def mechanical_visible(self):
        return self._mechanical_visible

    @mechanical_visible.setter
    def mechanical_visible(self, v: bool):
        self._mechanical_visible = v
        ui.update()

    @property
    def electrical_visible(self):
        return self._electrical_visible

    @electrical_visible.setter
    def electrical_visible(self, v: bool):
        self._electrical_visible = v
        ui.update()

    @property
    def shipping_visible(self):
        return self._shipping_visible

    @shipping_visible.setter
    def shipping_visible(self, v: bool):
        self._shipping_visible = v
        ui.update()

    @property
    def supplier_visible(self):
        return self._supplier_visible

    @supplier_visible.setter
    def supplier_visible(self, v: bool):
        self._supplier_visible = v
        ui.update()

    @property
    def finance_visible(self):
        return self._finance_visible

    @finance_visible.setter
    def finance_visible(self, v: bool):
        self._finance_visible = v
        ui.update()

    @property
    def certs_visible(self):
        return self._certs_visible

    @certs_visible.setter
    def certs_visible(self, v: bool):
        self._certs_visible = v
        ui.update()

    @property
    def enviromental_visible(self):
        return self._enviromental_visible

    @enviromental_visible.setter
    def enviromental_visible(self, v: bool):
        self._enviromental_visible = v
        ui.update()

state = State()

# Global results

# Configuration
server_config = config['server']

server        = server_config['host'] + ',' + server_config['port']
database      = config['tables']['main_db']
username      = server_config['username']
password      = server_config['password']

sku_conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'