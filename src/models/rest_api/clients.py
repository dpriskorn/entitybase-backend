import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from models.infrastructure.s3.s3_client import S3Config
    from models.infrastructure.vitess_client import VitessConfig


class Clients(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    s3: S3Client | None = None
    vitess: VitessClient | None = None
    property_registry: PropertyRegistry | None = None
    stream_producer: StreamProducerClient | None = None

    def __init__(
        self,
        s3: "S3Config",
        vitess: "VitessConfig",
        enable_streaming: bool = False,
        kafka_brokers: str | None = None,
        kafka_topic: str | None = None,
        property_registry_path: Path | None = None,
        **kwargs: str,
    ) -> None:
        super().__init__(
            s3=S3Client(config=s3),
            vitess=VitessClient(config=vitess),
            stream_producer=(
                StreamProducerClient(
                    bootstrap_servers=kafka_brokers,
                    topic=kafka_topic,
                )
                if enable_streaming and kafka_brokers and kafka_topic
                else None
            ),
            property_registry=(
                load_property_registry(property_registry_path)
                if property_registry_path
                else None
            ),
            **kwargs,
        )
        if not enable_streaming:
            logger.info("Streaming is disabled")
