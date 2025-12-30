import json
from pathlib import Path

from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.ontology.datatypes import property_shape



def load_property_registry(path: Path) -> PropertyRegistry:
    shapes = {}

    for file in path.glob("P*.json"):
        data = json.loads(file.read_text())

        pid = data["id"]
        datatype = data["datatype"]

        shapes[pid] = property_shape(pid, datatype)

    return PropertyRegistry(properties=shapes)
