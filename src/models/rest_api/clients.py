"""REST API service clients container."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from models.infrastructure.s3.s3_client import S3Config
    from models.infrastructure.vitess.vitess_client import VitessClient, VitessConfig


class Clients(BaseModel):
    """Container for all service clients."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    s3: MyS3Client
    vitess: "VitessClient"
    property_registry: PropertyRegistry | None = Field(default=None)
    stream_producer: StreamProducerClient | None = Field(default=None)
    rdf_stream_producer: StreamProducerClient | None = Field(default=None)

    def __init__(
        self,
        s3: "S3Config",
        vitess: "VitessConfig",
        enable_streaming: bool = False,
        kafka_brokers: str = "",
        kafka_topic: str = "",
        kafka_rdf_topic: str = "",
        property_registry_path: Path | None = None,
        **kwargs: str,
    ) -> None:
        from models.infrastructure.vitess.vitess_client import VitessClient

        super().__init__(
            s3=MyS3Client(config=s3),
            vitess=VitessClient(config=vitess),
            stream_producer=(
                StreamProducerClient(
                    bootstrap_servers=kafka_brokers,
                    topic=kafka_topic,
                )
                if enable_streaming and kafka_brokers and kafka_topic
                else None
            ),
            rdf_stream_producer=(
                StreamProducerClient(
                    bootstrap_servers=kafka_brokers,
                    topic=kafka_rdf_topic,
                )
                if enable_streaming and kafka_brokers and kafka_rdf_topic
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
