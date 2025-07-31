# catalog.py
from dependencies import *

# --- schema-driven dynamic class builder ---
TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}

def build_section_classes(schema_path: str | Path = "data.toml"):
    with open(schema_path, "rb") as f:
        schema = tomllib.load(f)

    section_defs = schema.get("sections", {})
    created_classes: dict[str, Any] = {}

    for section_name, fields_spec in section_defs.items():
        annotations = []
        for field_name, meta in fields_spec.items():
            tname = meta.get("type")
            if tname not in TYPE_MAP:
                raise ValueError(f"Unknown type '{tname}' for field '{field_name}' in section '{section_name}'")
            py_type = TYPE_MAP[tname]
            default = meta.get("default", ...)
            if default is ...:
                annotations.append((field_name, py_type))
            else:
                annotations.append((field_name, py_type, field(default=default)))
        cls_name = section_name.capitalize() if section_name.isidentifier() else section_name
        cls = make_dataclass(cls_name, annotations)
        created_classes[section_name] = cls

    # aggregate FullItem
    fullitem_fields = []
    for name, cls in created_classes.items():
        fullitem_fields.append((
            name,
            cls,
            field(default_factory=cls)
        ))
    FullItem = make_dataclass("FullItem", fullitem_fields)
    return created_classes, FullItem

# build once (module-level)
sections, FullItem = build_section_classes("data.toml")

# --- Catalog implementation ---
class Catalog:
    def __init__(self):
        self.items: dict[str, Any] = {}  # ref -> FullItem

    def get_or_create(self, ref: str, **basic_kwargs) -> Any:
        if ref not in self.items:
            item = FullItem()
            # set basic.ref if present
            if hasattr(item, "basic"):
                setattr(item.basic, "ref", ref)
                for k, v in basic_kwargs.items():
                    if hasattr(item.basic, k):
                        setattr(item.basic, k, v)
            self.items[ref] = item
        return self.items[ref]

    def all(self) -> list[Any]:
        return list(self.items.values())

    def to_dict(self) -> dict:
        return {ref: asdict(item) for ref, item in self.items.items()}

    def from_dict(self, data: dict):
        self.items.clear()
        for ref, item_data in data.items():
            item = FullItem()
            if hasattr(item, "basic"):
                setattr(item.basic, "ref", ref)
            for section_name, section_vals in item_data.items():
                section_obj = getattr(item, section_name, None)
                if section_obj is not None:
                    for field_name, value in section_vals.items():
                        if hasattr(section_obj, field_name):
                            setattr(section_obj, field_name, value)
            self.items[ref] = item

# shared singleton
catalog = Catalog()
