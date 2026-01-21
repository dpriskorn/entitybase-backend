"""REST API service clients container."""

import logging
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from models.common import raise_validation_error
from models.infrastructure.s3.client import S3Config, MyS3Client
from models.infrastructure.stream.config import StreamConfig
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess.client import VitessClient
from models.infrastructure.vitess.config import VitessConfig
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rest_api.entitybase.v1.services.enumeration_service import (
    EnumerationService,
)

logger = logging.getLogger(__name__)


class State(BaseModel):
    """State model that helps instantiate clients as needed"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    vitess_config: VitessConfig
    s3_config: S3Config
    entity_change_stream_config: StreamConfig
    entity_diff_stream_config: StreamConfig

    kafka_brokers: str = Field(default_factory=str)
    kafka_entitychange_topic: str = Field(default_factory=str)
    kafka_entitydiff_topic: str = Field(default_factory=str)
    property_registry_path: Path | None = Field(default=None)
    streaming_enabled: bool = False

    def start(self):
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
        # todo create healthy_connection method
        # if self.streaming_enabled and self.entitychange_stream_producer.healthy_connection:
        #     logger.debug("Kafka entitychange client connected successfully")
        # else:
        #     logger.warning("Kafka entitychange connection failed")
        # if self.streaming_enabled and self.entitydiff_stream_producer.healthy_connection:
        #     logger.debug("Kafka entitydiff client connected successfully")
        # else:
        #     logger.warning("Kafka entitydiff connection failed")

        logger.debug("Clients initialized successfully")

    @property
    def vitess_client(self) -> "VitessClient":
        """Get a fully ready client"""
        from models.infrastructure.vitess.client import VitessClient

        if self.vitess_config is None:
            raise_validation_error(message="No vitess config provided")
        return VitessClient(config=self.vitess_config)

    @property
    def s3_client(self) -> "MyS3Client":
        """Get a fully ready client"""
        from models.infrastructure.s3.client import MyS3Client

        assert isinstance(self.s3_config, S3Config)
        return MyS3Client(config=self.s3_config)

    @property
    def entitychange_stream_producer(self) -> StreamProducerClient:
        """Get a fully ready client"""
        if (
            self.streaming_enabled
            and self.kafka_brokers
            and self.kafka_entitychange_topic
        ):
            return StreamProducerClient(config=self.stream_config)
        else:
            raise_validation_error(message="No kafka broker and topic provided")

    @property
    def entitydiff_stream_producer(self) -> StreamProducerClient:
        """Get a fully ready client"""
        if (
            self.streaming_enabled
            and self.kafka_brokers
            and self.kafka_entitydiff_topic
        ):
            return StreamProducerClient(config=self.stream_config)
        else:
            raise_validation_error(message="No kafka broker and rdf topic provided")

    @property
    def property_registry(self) -> PropertyRegistry | None:
        if self.property_registry_path is not None:
            return load_property_registry(self.property_registry_path)
        else:
            raise_validation_error(message="No property registry path provided")

    @property
    def enumeration_service(self):
        return EnumerationService(
            worker_id="rest-api", vitess_client=self.vitess_client
        )
