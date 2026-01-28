"""REST API service clients container."""

import logging
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from models.common import raise_validation_error
from models.config.settings import Settings
from models.data.config.s3 import S3Config
from models.data.config.stream import StreamConfig
from models.data.config.vitess import VitessConfig
from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess.client import VitessClient
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rest_api.entitybase.v1.services.enumeration_service import (
    EnumerationService,
)
from models.validation.json_schema_validator import JsonSchemaValidator

logger = logging.getLogger(__name__)


class StateHandler(BaseModel):
    """State model that helps instantiate clients as needed"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    settings: Settings

    def start(self):
        logger.info("Initializing clients...")
        logger.debug(f"S3 config: {self.settings.get_s3_config}")
        logger.debug(f"Vitess config: {self.settings.get_vitess_config}")
        logger.debug(
            f"Kafka config: brokers={self.settings.kafka_brokers}, topic={self.settings.kafka_entity_change_topic}"
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
    def entity_diff_stream_config(self) -> StreamConfig:
        return self.settings.get_entity_diff_stream_config

    @property
    def entity_change_stream_config(self) -> StreamConfig:
        return self.settings.get_entity_change_stream_config

    @property
    def s3_config(self) -> S3Config:
        return self.settings.get_s3_config

    @property
    def vitess_config(self) -> VitessConfig:
        return self.settings.get_vitess_config

    @property
    def vitess_client(self) -> "VitessClient":
        """Get a fully ready client"""
        logger.debug("vitess_client: Running")
        from models.infrastructure.vitess.client import VitessClient

        if self.vitess_config is None:
            raise_validation_error(message="No vitess config provided")
        return VitessClient(config=self.vitess_config)

    @property
    def s3_client(self) -> "MyS3Client":
        """Get a fully ready client"""
        from models.infrastructure.s3.client import MyS3Client
        return MyS3Client(config=self.s3_config, vitess_client=self.vitess_client)

    @property
    def entity_change_stream_producer(self) -> StreamProducerClient | None:
        """Get a fully ready client"""
        if (
            self.settings.streaming_enabled
            and self.settings.kafka_brokers
            and self.settings.kafka_entitychange_topic
        ):
            return StreamProducerClient(config=self.entity_change_stream_config)
        else:
            message = "No kafka broker and rdf topic provided"
            logger.info(message)
            # raise_validation_error(message="No kafka broker and topic provided")
            return None

    @property
    def entitydiff_stream_producer(self) -> StreamProducerClient | None:
        """Get a fully ready client"""
        if (
            self.streaming_enabled
            and self.kafka_brokers
            and self.kafka_entitydiff_topic
        ):
            return StreamProducerClient(config=self.entity_diff_stream_config)
        else:
            message = "No kafka broker and rdf topic provided"
            logger.info(message)
            # raise_validation_error()
            return None

    @property
    def property_registry(self) -> PropertyRegistry | None:
        if self.property_registry_path is not None:
            return load_property_registry(self.settings.property_registry_path)
        else:
            raise_validation_error(message="No property registry path provided")

    @property
    def enumeration_service(self):
        return EnumerationService(
            worker_id="rest-api", vitess_client=self.vitess_client
        )

    @property
    def redirect_service(self):
        from models.rest_api.entitybase.v1.services.redirects import RedirectService
        return RedirectService(state=self)

    @property
    def validator(self):
        return JsonSchemaValidator(
            s3_revision_version=self.settings.s3_schema_revision_version,
            s3_statement_version=self.settings.s3_statement_version,
            entity_change_version=self.settings.streaming_entity_change_version,
        )

    @property
    def property_registry_path(self) -> Path | None:
        path_ = (
            Path("test_data/properties")
            if Path("test_data/properties").exists()
            else None
        )
        logger.debug(f"Property registry path: {path_}")
        return path_
