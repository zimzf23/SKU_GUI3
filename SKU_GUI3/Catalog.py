import tomllib
from dataclasses import make_dataclass, field
from typing import get_origin, get_args

# map string names to actual Python types
TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}

def build_section_classes(schema_path: str):
    with open(schema_path, "rb") as f:
        schema = tomllib.load(f)

    section_defs = schema.get("sections", {})
    created_classes = {}

    for section_name, fields_spec in section_defs.items():
        annotations = []
        defaults = []
        for field_name, meta in fields_spec.items():
            tname = meta.get("type")
            if tname not in TYPE_MAP:
                raise ValueError(f"Unknown type '{tname}' for field '{field_name}' in section '{section_name}'")
            py_type = TYPE_MAP[tname]
            default = meta.get("default", ...)
            if default is ...:
                # required positional
                annotations.append((field_name, py_type))
            else:
                annotations.append((field_name, py_type, field(default=default)))
        cls = make_dataclass(
            section_name.capitalize() if section_name.isidentifier() else section_name,
            annotations
        )
        created_classes[section_name] = cls

    # Build aggregate FullItem with all sections as fields
    fullitem_fields = []
    for name, cls in created_classes.items():
        # default_factory to create nested subobject
        fullitem_fields.append((
            name,
            cls,
            field(default_factory=cls)
        ))
    FullItem = make_dataclass("FullItem", fullitem_fields)
    return created_classes, FullItem
