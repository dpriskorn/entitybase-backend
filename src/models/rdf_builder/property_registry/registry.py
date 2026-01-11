"""Property registry for RDF building."""

from pydantic import BaseModel, ConfigDict

from models.rdf_builder.property_registry.models import PropertyShape


class PropertyRegistry(BaseModel):
    properties: dict[str, PropertyShape]

    model_config = ConfigDict(frozen=True)

    def shape(self, pid: str) -> PropertyShape:
        try:
            return self.properties[pid]
        except KeyError:
            raise KeyError(f"Property {pid} not in registry")
