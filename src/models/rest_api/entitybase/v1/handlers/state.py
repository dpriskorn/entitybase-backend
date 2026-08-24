"""REST API service clients container."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from models.rest_api.utils import raise_validation_error
from models.config.settings import Settings
from models.data.config.s3 import S3Config
from models.data.config.sqlite import SqliteConfig
from models.data.config.stream import StreamConfig
from models.data.config.mysql import MysqlConfig
from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.db.client import MysqlClient
from models.infrastructure.db.repositories.revision_data import RevisionDataRepository
from models.infrastructure.db.repositories.revision import RevisionRepository
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rest_api.entitybase.v1.services.enumeration_service import (
    EnumerationService,
)
from models.validation.json_schema_validator import JsonSchemaValidator

if TYPE_CHECKING:
    from models.rest_api.entitybase.v1.services.redirects import RedirectService

logger = logging.getLogger(__name__)


class StateHandler(BaseModel):
    """State model that helps instantiate clients as needed"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    settings: Settings
    cached_db_client: MysqlClient | None = Field(default=None, exclude=True)
    cached_s3_client: MyS3Client | None = Field(default=None, exclude=True)
    cached_enumeration_service: EnumerationService | None = Field(
        default=None, exclude=True
    )
    cached_property_registry: PropertyRegistry | None = Field(
        default=None, exclude=True
    )
    cached_entity_change_stream_producer: StreamProducerClient | None = Field(
        default=None, exclude=True
    )
    cached_entitydiff_stream_producer: StreamProducerClient | None = Field(
        default=None, exclude=True
    )
    cached_user_change_stream_producer: StreamProducerClient | None = Field(
        default=None, exclude=True
    )

    def start(self) -> None:
        logger.info("=== StateHandler.start() START ===")
        logger.info("Initializing clients...")
        logger.debug(f"S3 config: {self.settings.get_s3_config}")
        logger.debug(f"MySQL config: {self.settings.get_mysql_config}")
        logger.debug(
            f"Kafka config: brokers={self.settings.kafka_bootstrap_servers}, topic={self.settings.kafka_entitychange_json_topic}"
        )
        if not self.settings.streaming_enabled:
            logger.info("Streaming is disabled")
        logger.info("=== StateHandler.start() END ===")

    def health_check(self) -> None:
        """Check if clients work"""
        logger.debug("=== health_check() START ===")
        logger.debug("Checking MySQL connection...")
        if self.mysql_config and self.db_client.healthy_connection:
            logger.debug("MySQL client connected successfully")
        else:
            logger.warning("MySQL client connection failed")
        logger.debug("Clients initialized successfully")
        logger.debug("=== health_check() END ===")

    @property
    def entity_diff_stream_config(self) -> StreamConfig:
        return self.settings.get_entity_diff_stream_config

    @property
    def entity_change_stream_config(self) -> StreamConfig:
        return self.settings.get_entity_change_stream_config

    @property
    def user_change_stream_config(self) -> StreamConfig:
        return self.settings.get_user_change_stream_config

    @property
    def s3_config(self) -> S3Config:
        return self.settings.get_s3_config

    @property
    def mysql_config(self) -> MysqlConfig:
        return self.settings.get_mysql_config

    @property
    def db_client(self) -> "MysqlClient":
        """Get or create a cached database client.

        Returns a SqliteClient or MysqlClient depending on DB_TYPE setting.
        """
        if self.cached_db_client is None:
            if self.settings.db_type == "sqlite":
                logger.debug(
                    "=== db_client property: Creating new SqliteClient instance ==="
                )
                from models.infrastructure.sqlite.client import SqliteClient

                self.cached_db_client = SqliteClient(
                    config=self.settings.get_db_config
                )
            else:
                logger.debug(
                    "=== db_client property: Creating new MysqlClient instance ==="
                )
                from models.infrastructure.db.client import MysqlClient

                if self.mysql_config is None:
                    raise_validation_error(message="No MySQL config provided")
                logger.debug("Instantiating MysqlClient...")
                self.cached_db_client = MysqlClient(config=self.mysql_config)
            logger.debug("=== db_client property: Database client created ===")
        return self.cached_db_client

    @property
    def s3_client(self) -> "MyS3Client":
        """Get or create a cached MyS3Client."""
        if self.cached_s3_client is None:
            logger.debug("=== s3_client property: Creating new MyS3Client instance ===")
            from models.infrastructure.s3.client import MyS3Client

            logger.debug("Creating MyS3Client with db_client dependency...")
            self.cached_s3_client = MyS3Client(
                config=self.s3_config, db_client=self.db_client
            )
            logger.debug("=== s3_client property: MyS3Client created ===")
        return self.cached_s3_client

    def read_revision_data(self, entity_id: str, revision_id: int) -> Any:
        """Read revision data from MariaDB.

        Resolves entity_id to internal_id, looks up content_hash from
        entity_revisions, then loads the full revision JSON from
        entity_revision_data.
        """
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.rest_api.utils import raise_validation_error

        internal_id = self.db_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise_validation_error("Entity not found", status_code=404)

        revision_repo = RevisionRepository(db_client=self.db_client)
        content_hash = revision_repo.get_content_hash(internal_id, revision_id)
        if content_hash == 0:
            raise_validation_error("Revision not found", status_code=404)

        revision_data_repo = RevisionDataRepository(db_client=self.db_client)
        data = revision_data_repo.load(content_hash)
        if data is None:
            raise_validation_error("Revision data not found", status_code=404)

        return S3RevisionData.model_validate(data)

    @property
    def entity_change_stream_producer(self) -> StreamProducerClient | None:
        """Get or create a cached Kafka producer for entity changes."""
        if (
            self.settings.streaming_enabled
            and self.settings.kafka_bootstrap_servers
            and self.settings.kafka_entitychange_json_topic
        ):
            if self.cached_entity_change_stream_producer is None:
                logger.debug(
                    "=== entity_change_stream_producer property: Creating new StreamProducerClient ==="
                )
                self.cached_entity_change_stream_producer = StreamProducerClient(
                    config=self.entity_change_stream_config
                )
                logger.info(
                    f"Created entity change stream producer for topic {self.settings.kafka_entitychange_json_topic}"
                )
            return self.cached_entity_change_stream_producer
        else:
            message = "Streaming disabled or Kafka config missing"
            logger.info(message)
            return None

    @property
    def entitydiff_stream_producer(self) -> StreamProducerClient | None:
        """Get or create a cached Kafka producer for entity diffs."""
        if (
            self.settings.streaming_enabled
            and self.settings.kafka_bootstrap_servers
            and self.settings.kafka_entity_diff_topic
        ):
            if self.cached_entitydiff_stream_producer is None:
                logger.debug(
                    "=== entitydiff_stream_producer property: Creating new StreamProducerClient ==="
                )
                self.cached_entitydiff_stream_producer = StreamProducerClient(
                    config=self.entity_diff_stream_config
                )
                logger.info(
                    f"Created entity diff stream producer for topic {self.settings.kafka_entity_diff_topic}"
                )
            return self.cached_entitydiff_stream_producer
        else:
            message = "Streaming disabled or Kafka config missing"
            logger.info(message)
            return None

    @property
    def user_change_stream_producer(self) -> StreamProducerClient | None:
        """Get or create a cached Kafka producer for user changes."""
        if (
            self.settings.streaming_enabled
            and self.settings.kafka_bootstrap_servers
            and self.settings.kafka_userchange_json_topic
        ):
            if self.cached_user_change_stream_producer is None:
                logger.debug(
                    "=== user_change_stream_producer property: Creating new StreamProducerClient ==="
                )
                self.cached_user_change_stream_producer = StreamProducerClient(
                    config=self.user_change_stream_config
                )
                logger.info(
                    f"Created user change stream producer for topic {self.settings.kafka_userchange_json_topic}"
                )
            return self.cached_user_change_stream_producer
        else:
            message = "Streaming disabled or Kafka config missing"
            logger.info(message)
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
                worker_id="rest-api", db_client=self.db_client
            )
        return self.cached_enumeration_service

    def disconnect(self) -> None:
        """Disconnect all clients and release resources."""
        if self.cached_db_client is not None:
            self.cached_db_client.disconnect()
            self.cached_db_client = None
            logger.info("MysqlClient disconnected")

        if self.cached_s3_client is not None:
            self.cached_s3_client.disconnect()
            self.cached_s3_client = None
            logger.info("S3Client disconnected")

    async def async_shutdown(self) -> None:
        """Async shutdown for Kafka producers."""
        if self.cached_entity_change_stream_producer is not None:
            await self.cached_entity_change_stream_producer.stop()
            self.cached_entity_change_stream_producer = None
            logger.info("Entity change stream producer stopped")

        if self.cached_entitydiff_stream_producer is not None:
            await self.cached_entitydiff_stream_producer.stop()
            self.cached_entitydiff_stream_producer = None
            logger.info("Entity diff stream producer stopped")

        if self.cached_user_change_stream_producer is not None:
            await self.cached_user_change_stream_producer.stop()
            self.cached_user_change_stream_producer = None
            logger.info("User change stream producer stopped")

    @property
    def redirect_service(self) -> "RedirectService":
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
