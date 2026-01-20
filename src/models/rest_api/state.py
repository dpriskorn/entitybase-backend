"""REST API service clients container."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from models.common import raise_validation_error
from models.infrastructure.stream.producer import StreamProducerClient
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from models.infrastructure.s3.client import S3Config
    from models.infrastructure.vitess.client import VitessClient
    from models.infrastructure.vitess.config import VitessConfig


class State(BaseModel):
    """State model that helps instantiate clients as needed"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    vitess_config: "VitessConfig | None" = Field(default=None)
    s3_config: "S3Config | None" = Field(default=None)

    kafka_brokers: str = "",
    kafka_entitychange_topic: str = "",
    kafka_rdf_topic: str = "",
    property_registry_path: Path | None = None,
    streaming_enabled: bool = False,

    def __init__(
        self,
        **kwargs,
    ) -> None:
        super().__init__(
            **kwargs,
        )
        if not self.streaming_enabled:
            logger.info("Streaming is disabled")
        self.health_check()

    def health_check(self) -> None:
        """Check if clients work"""
        if self.s3_config and self.s3_client.healthy_connection:
            logger.debug("S3 client connected successfully")
        else:
            logger.warning("S3 client connection failed")
        if self.vitess_config and self.vitess_client.healthy_connection:
            logger.debug("Vitess client connected successfully")
        else:
            logger.warning("Vitess client connection failed")
        if self.streaming_enabled and self.entitychange_stream_producer.healthy_connection:
            logger.debug("Vitess client connected successfully")
        else:
            logger.warning("Vitess client connection failed")

        logger.debug("Clients initialized successfully")

    @property
    def vitess_client(self):
        """Get a fully ready client"""
        from models.infrastructure.vitess.client import VitessClient
        return VitessClient(config=self.vitess_config)

    @property
    def s3_client(self):
        """Get a fully ready client"""
        from models.infrastructure.vitess.client import VitessClient
        return VitessClient(config=self.vitess_config)

    @property
    def entitychange_stream_producer(self) -> StreamProducerClient:
        """Get a fully ready client"""
        if self.streaming_enabled and self.kafka_brokers and self.kafka_entitychange_topic:
            return StreamProducerClient(
                bootstrap_servers=self.kafka_brokers,
                topic=self.kafka_entitychange_topic,
            )
        else:
            raise_validation_error(message="No kafka broker and topic provided")

    @property
    def rdfdiff_stream_producer(self) -> StreamProducerClient:
        """Get a fully ready client"""
        if self.streaming_enabled and self.kafka_brokers and self.kafka_rdf_topic:
            return StreamProducerClient(
                bootstrap_servers=self.kafka_brokers,
                topic=self.kafka_rdf_topic,
            )
        else:
            raise_validation_error(message="No kafka broker and rdf topic provided")

    @property
    def property_registry(self) -> PropertyRegistry | None:
        if self.property_registry_path:
            return load_property_registry(self.property_registry_path)
        else:
            raise_validation_error(message="No property registry path provided")
