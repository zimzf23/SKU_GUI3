from dependencies import *
from sql_fs import insert_file_under_code
from state import state

class UploadCache:
    #Temporarily store uploaded files before writing them to the FileTable
    def __init__(self):
        # key: (code, folder or None) -> list of dicts {name, data}
        self._cache: dict[tuple[str, str | None], list[dict]] = {}

    def add_file(self, code: str, file_name: str, data: bytes, folder: str | None = None):
        self._cache.setdefault((code, folder), []).append(
            {"name": file_name, "data": data}
        )

    def list(self, code: str) -> list[tuple[str, str | None, str, int]]:
        out = []
        for (c, folder), files in self._cache.items():
            if c == code:
                for f in files:
                    out.append((f["name"], folder,f["name"], len(f["data"])))
        return out

    def clear_code(self, code: str):
        to_del = [k for k in self._cache if k[0] == code]
        for k in to_del:
            self._cache.pop(k, None)

    def flush(self, conn_string: str, overwrite: bool = True):
        #Write all cached files to the FileTable and return (success_names, failures[(name, exc), ...])
        successes = []
        failures = []

        for (code, folder), files in list(self._cache.items()):
            for f in files:
                try:
                    insert_file_under_code(
                        conn_string=conn_string,
                        code=code,
                        file_name=f["name"],     # no rename anymore
                        data=f["data"],
                        folder=folder,
                        overwrite=overwrite,
                    )
                    successes.append(f["name"])
                except Exception as ex:
                    failures.append((f["name"], ex))
        self._cache.clear()
        return successes, failures

    def clear(self) -> None:
        self._cache.clear()

cache = UploadCache()
