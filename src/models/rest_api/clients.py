from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry

if TYPE_CHECKING:
    from models.infrastructure.s3.s3_client import S3Config
    from models.infrastructure.vitess_client import VitessConfig


class Clients(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    s3: S3Client | None = None
    vitess: VitessClient | None = None
    property_registry: PropertyRegistry | None = None

    def __init__(
        self,
        s3: "S3Config",
        vitess: "VitessConfig",
        property_registry_path: Path | None = None,
        **kwargs: str,
    ) -> None:
        super().__init__(
            s3=S3Client(s3),
            vitess=VitessClient(vitess),
            property_registry=(
                load_property_registry(property_registry_path)
                if property_registry_path
                else None
            ),
            **kwargs,
        )
