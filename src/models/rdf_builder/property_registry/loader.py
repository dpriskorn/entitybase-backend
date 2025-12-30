import json
from pathlib import Path

from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.ontology.datatypes import shape_from_datatype


def load_property_registry(path: Path) -> PropertyRegistry:
    shapes = {}

    for file in path.glob("P*.json"):
        data = json.loads(file.read_text())

        pid = data["id"]
        datatype = data["datatype"]

        shapes[pid] = shape_from_datatype(pid, datatype)

    return PropertyRegistry(shapes=shapes)
