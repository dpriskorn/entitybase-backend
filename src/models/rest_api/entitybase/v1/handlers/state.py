"""REST API service clients container."""

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from models.rest_api.utils import raise_validation_error
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
    cached_vitess_client: VitessClient | None = Field(default=None, exclude=True)
    cached_s3_client: MyS3Client | None = Field(default=None, exclude=True)
    cached_enumeration_service: EnumerationService | None = Field(
        default=None, exclude=True
    )
    cached_property_registry: PropertyRegistry | None = Field(
        default=None, exclude=True
    )

    def start(self) -> None:
        logger.info("=== StateHandler.start() START ===")
        logger.info("Initializing clients...")
        logger.debug(f"S3 config: {self.settings.get_s3_config}")
        logger.debug(f"Vitess config: {self.settings.get_vitess_config}")
        logger.debug(
            f"Kafka config: brokers={self.settings.kafka_bootstrap_servers}, topic={self.settings.kafka_entitychange_json_topic}"
        )
        if not self.settings.streaming_enabled:
            logger.info("Streaming is disabled")
        logger.debug("Calling health_check()...")
        self.health_check()
        logger.info("=== StateHandler.start() END ===")

    def health_check(self) -> None:
        """Check if clients work"""
        logger.debug("=== health_check() START ===")
        logger.debug("Checking S3 connection...")
        if self.s3_config and self.s3_client.healthy_connection:
            logger.debug("S3 client connected successfully")
        else:
            logger.warning("S3 client connection failed")
        logger.debug("Checking Vitess connection...")
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
        logger.debug("=== health_check() END ===")

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
        """Get or create a cached VitessClient."""
        if self.cached_vitess_client is None:
            logger.debug(
                "=== vitess_client property: Creating new VitessClient instance ==="
            )
            from models.infrastructure.vitess.client import VitessClient

            if self.vitess_config is None:
                raise_validation_error(message="No vitess config provided")
            logger.debug("Instantiating VitessClient...")
            self.cached_vitess_client = VitessClient(config=self.vitess_config)
            logger.debug("=== vitess_client property: VitessClient created ===")
        return self.cached_vitess_client

    @property
    def s3_client(self) -> "MyS3Client":
        """Get or create a cached MyS3Client."""
        if self.cached_s3_client is None:
            logger.debug("=== s3_client property: Creating new MyS3Client instance ===")
            from models.infrastructure.s3.client import MyS3Client

            logger.debug("Creating MyS3Client with vitess_client dependency...")
            self.cached_s3_client = MyS3Client(
                config=self.s3_config, vitess_client=self.vitess_client
            )
            logger.debug("=== s3_client property: MyS3Client created ===")
        return self.cached_s3_client

    @property
    def entity_change_stream_producer(self) -> StreamProducerClient | None:
        """Get a fully ready client"""
        if (
            self.settings.streaming_enabled
            and self.settings.kafka_bootstrap_servers
            and self.settings.kafka_entitychange_json_topic
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
            self.settings.streaming_enabled
            and self.settings.kafka_bootstrap_servers
            and self.settings.kafka_entity_diff_topic
        ):
            return StreamProducerClient(config=self.entity_diff_stream_config)
        else:
            message = "No kafka broker and rdf topic provided"
            logger.info(message)
            # raise_validation_error()
            return None

    @property
    def property_registry(self) -> PropertyRegistry | None:
        if self.cached_property_registry is None:
            if self.property_registry_path is not None:
                self.cached_property_registry = load_property_registry(
                    self.settings.property_registry_path
                )
            else:
                raise_validation_error(message="No property registry path provided")
        return self.cached_property_registry

    @property
    def enumeration_service(self) -> EnumerationService:
        if self.cached_enumeration_service is None:
            self.cached_enumeration_service = EnumerationService(
                worker_id="rest-api", vitess_client=self.vitess_client
            )
        return self.cached_enumeration_service

    def disconnect(self) -> None:
        """Disconnect all clients and release resources."""
        if self.cached_vitess_client is not None:
            self.cached_vitess_client.disconnect()
            self.cached_vitess_client = None
            logger.info("VitessClient disconnected")

        if self.cached_s3_client is not None:
            self.cached_s3_client.disconnect()
            self.cached_s3_client = None
            logger.info("S3Client disconnected")

    @property
    def redirect_service(self) -> Any:
        from models.rest_api.entitybase.v1.services.redirects import RedirectService

        return RedirectService(state=self)

    @property
    def validator(self) -> JsonSchemaValidator:
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
