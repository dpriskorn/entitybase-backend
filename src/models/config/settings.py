"""Application configuration and settings management."""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from models.data.config.stream import StreamConfig
from models.config.version import ENTITYBASE_VERSION

if TYPE_CHECKING:
    from models.data.config.s3 import S3Config
    from models.data.config.vitess import VitessConfig

logger = logging.getLogger(__name__)


class Settings(BaseModel):
    """Application settings with environment variable support."""

    model_config = {"extra": "ignore"}

    # s3
    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "fakekey"
    s3_secret_key: str = "fakesecret"

    # buckets
    s3_revisions_bucket: str = "revisions"

    # S3 versions
    s3_snak_version: str = "1.0.0"
    s3_sitelink_version: str = "1.0.0"
    s3_qualifier_version: str = "1.0.0"
    s3_reference_version: str = "1.0.0"
    s3_statement_version: str = "1.0.0"
    s3_schema_revision_version: str = "4.0.0"

    # vitess
    vitess_host: str = ""
    vitess_port: int = 0
    vitess_database: str = ""
    vitess_user: str = ""
    vitess_password: str = ""
    vitess_pool_size: int = 20
    vitess_max_overflow: int = 20
    vitess_pool_timeout: int = 30

    # rdf
    wikibase_repository_name: str = "wikidata"
    property_registry_path: Path = Path("properties")

    # logging
    log_level: str = "INFO"

    # streaming
    _streaming_enabled: bool = False
    streaming_backend: str = "redpanda"
    kafka_bootstrap_servers: str = ""
    kafka_entitychange_json_topic: str = ""
    kafka_entity_diff_topic: str = ""
    kafka_userchange_json_topic: str = ""
    kafka_incremental_rdf_topic: str = ""
    streaming_entity_change_version: str = "1.0.0"
    streaming_endorsechange_version: str = "1.0.0"
    streaming_newthank_version: str = "1.0.0"
    streaming_entity_diff_version: str = "2.0.0"
    streaming_user_change_version: str = "1.0.0"

    # entity version
    entity_version: str = ENTITYBASE_VERSION

    # entity dangling detection
    dangling_property_id: str = "P6104"

    # API configuration
    api_prefix: str = "/v1"

    # other
    user_agent: str = f"Entitybase/{ENTITYBASE_VERSION} User:So9q"
    api_description: str = ""

    # workers
    backlink_stats_worker_enabled: bool = True
    backlink_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backlink_stats_top_limit: int = 100
    user_stats_worker_enabled: bool = True
    user_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM
    general_stats_worker_enabled: bool = True
    general_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM

    # JSON dump worker
    json_worker_enabled: bool = True
    json_dump_schedule: str = "0 2 * * 0"  # Sunday 2AM UTC
    s3_dump_bucket: str = "entitybase-dumps"
    json_dump_batch_size: int = 1000
    json_dump_parallel_workers: int = 50
    json_dump_generate_checksums: bool = True

    # TTL dump worker
    ttl_worker_enabled: bool = True
    ttl_dump_schedule: str = "0 3 * * 0"  # Sunday 3AM UTC (after JSON dump)
    ttl_dump_batch_size: int = 1000
    ttl_dump_parallel_workers: int = 50
    ttl_dump_compression: bool = True
    ttl_dump_generate_checksums: bool = True

    # ID worker
    id_worker_enabled: bool = True

    # Incremental RDF worker
    incremental_rdf_enabled: bool = False
    incremental_rdf_consumer_group: str = "incremental-rdf-worker"

    # Elasticsearch worker
    elasticsearch_enabled: bool = False
    elasticsearch_host: str = "localhost"
    elasticsearch_port: int = 9200
    elasticsearch_index: str = "entitybase"
    elasticsearch_username: str = ""
    elasticsearch_password: str = ""
    elasticsearch_use_ssl: bool = True
    elasticsearch_verify_certs: bool = True
    elasticsearch_consumer_group: str = "entitybase-elasticsearch-indexer"

    # Meilisearch worker
    meilisearch_enabled: bool = False
    meilisearch_host: str = "localhost"
    meilisearch_port: int = 7700
    meilisearch_api_key: str = ""
    meilisearch_index: str = "entitybase"
    meilisearch_consumer_group: str = "entitybase-meilisearch-indexer"

    # Purge worker
    purge_worker_enabled: bool = True
    purge_schedule: str = "0 0 * * *"  # Daily at midnight UTC
    purge_batch_size: int = 100

    def model_post_init(self, context: Any) -> None:
        """Initialize all fields from environment variables.

        This method runs after the model is created to fetch values
        from environment variables, overriding any default values.
        """
        self._load_s3_config()
        self._load_vitess_config()
        self._load_entity_config()
        self._load_streaming_config()
        self._load_other_config()
        self._load_rdf_config()
        self._load_workers_config()

    def _load_s3_config(self) -> None:
        """Load S3 configuration from environment variables."""
        logger.debug("Loading S3 configuration from environment variables")
        self.s3_endpoint = os.getenv("S3_ENDPOINT", self.s3_endpoint)
        self.s3_access_key = os.getenv("S3_ACCESS_KEY", self.s3_access_key)
        self.s3_secret_key = os.getenv("S3_SECRET_KEY", self.s3_secret_key)

        self.s3_revisions_bucket = os.getenv(
            "S3_REVISIONS_BUCKET", self.s3_revisions_bucket
        )

        self.s3_snak_version = os.getenv("S3_SNAK_VERSION", self.s3_snak_version)
        self.s3_sitelink_version = os.getenv(
            "S3_SITELINK_VERSION", self.s3_sitelink_version
        )
        self.s3_qualifier_version = os.getenv(
            "S3_QUALIFIER_VERSION", self.s3_qualifier_version
        )
        self.s3_reference_version = os.getenv(
            "S3_REFERENCE_VERSION", self.s3_reference_version
        )
        self.s3_statement_version = os.getenv(
            "S3_STATEMENT_VERSION", self.s3_statement_version
        )
        self.s3_schema_revision_version = os.getenv(
            "S3_REVISION_VERSION", self.s3_schema_revision_version
        )

    def _load_vitess_config(self) -> None:
        """Load Vitess configuration from environment variables."""
        self.vitess_host = os.getenv("VITESS_HOST", self.vitess_host)
        logger.debug(f"self.vitess_host: {self.vitess_host}")
        self.vitess_port = int(os.getenv("VITESS_PORT", str(self.vitess_port)))
        self.vitess_database = os.getenv("VITESS_DATABASE", self.vitess_database)
        self.vitess_user = os.getenv("VITESS_USER", self.vitess_user)
        self.vitess_password = os.getenv("VITESS_PASSWORD", self.vitess_password)

    def _load_entity_config(self) -> None:
        """Load entity version and API config from environment variables."""
        self.entity_version = os.getenv("ENTITY_VERSION", self.entity_version)
        self.api_prefix = os.getenv("API_PREFIX", self.api_prefix)
        self.dangling_property_id = os.getenv(
            "DANGLING_PROPERTY_ID", self.dangling_property_id
        )

    def _load_streaming_config(self) -> None:
        """Load streaming configuration from environment variables."""
        logger.debug("Loading streaming configuration from environment variables")
        self.streaming_backend = os.getenv("STREAMING_BACKEND", self.streaming_backend)
        self.kafka_bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", self.kafka_bootstrap_servers
        )
        self.kafka_entitychange_json_topic = os.getenv(
            "KAFKA_ENTITYCHANGE_JSON_TOPIC", self.kafka_entitychange_json_topic
        )
        self.kafka_entity_diff_topic = os.getenv(
            "KAFKA_ENTITY_DIFF_TOPIC", self.kafka_entity_diff_topic
        )
        self.kafka_userchange_json_topic = os.getenv(
            "KAFKA_USERCHANGE_JSON_TOPIC", self.kafka_userchange_json_topic
        )
        self.kafka_incremental_rdf_topic = os.getenv(
            "KAFKA_INCREMENTAL_RDF_TOPIC", self.kafka_incremental_rdf_topic
        )
        self.streaming_entity_change_version = os.getenv(
            "STREAMING_ENTITY_CHANGE_VERSION", self.streaming_entity_change_version
        )
        self.streaming_endorsechange_version = os.getenv(
            "STREAMING_ENDORSECHANGE_VERSION", self.streaming_endorsechange_version
        )
        self.streaming_newthank_version = os.getenv(
            "STREAMING_NEWTHANK_VERSION", self.streaming_newthank_version
        )
        self.streaming_entity_diff_version = os.getenv(
            "STREAMING_ENTITY_DIFF_VERSION", self.streaming_entity_diff_version
        )
        self.streaming_user_change_version = os.getenv(
            "STREAMING_USER_CHANGE_VERSION", self.streaming_user_change_version
        )

    @property
    def streaming_enabled(self) -> bool:
        """Check if streaming is enabled via environment variable."""
        return os.getenv("STREAMING_ENABLED", "false").lower() == "true"

    def _load_other_config(self) -> None:
        """Load other configuration from environment variables."""
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.user_agent = os.getenv("USER_AGENT", self.user_agent)
        self.api_description = os.getenv("API_DESCRIPTION", self.api_description)

    def _load_rdf_config(self) -> None:
        """Load RDF configuration from environment variables."""
        self.wikibase_repository_name = os.getenv(
            "WIKIBASE_REPOSITORY_NAME", self.wikibase_repository_name
        )
        self.property_registry_path = Path(
            os.getenv("PROPERTY_REGISTRY_PATH", self.property_registry_path)
        )

    def _load_workers_config(self) -> None:
        """Load workers configuration from environment variables."""
        logger.debug("Loading workers configuration from environment variables")

        # Stats worker (enables/disables all stats workers at once)
        stats_worker_enabled = (
            os.getenv("STATS_WORKER_ENABLED", "false").lower() == "true"
        )

        if os.getenv("STATS_WORKER_ENABLED"):
            # If STATS_WORKER_ENABLED is explicitly set, use it for all
            self.backlink_stats_worker_enabled = stats_worker_enabled
            self.user_stats_worker_enabled = stats_worker_enabled
            self.general_stats_worker_enabled = stats_worker_enabled
        else:
            # Otherwise load individual settings
            self.backlink_stats_worker_enabled = (
                os.getenv(
                    "BACKLINK_STATS_WORKER_ENABLED",
                    str(self.backlink_stats_worker_enabled),
                ).lower()
                == "true"
            )
            self.user_stats_worker_enabled = (
                os.getenv(
                    "USER_STATS_WORKER_ENABLED", str(self.user_stats_worker_enabled)
                ).lower()
                == "true"
            )
            self.general_stats_worker_enabled = (
                os.getenv(
                    "GENERAL_STATS_WORKER_ENABLED",
                    str(self.general_stats_worker_enabled),
                ).lower()
                == "true"
            )
        self.json_worker_enabled = (
            os.getenv("JSON_WORKER_ENABLED", str(self.json_worker_enabled)).lower()
            == "true"
        )
        self.json_dump_schedule = os.getenv(
            "JSON_DUMP_SCHEDULE", self.json_dump_schedule
        )
        self.s3_dump_bucket = os.getenv("S3_DUMP_BUCKET", self.s3_dump_bucket)
        self.json_dump_batch_size = int(
            os.getenv("JSON_DUMP_BATCH_SIZE", str(self.json_dump_batch_size))
        )
        self.json_dump_parallel_workers = int(
            os.getenv(
                "JSON_DUMP_PARALLEL_WORKERS", str(self.json_dump_parallel_workers)
            )
        )
        self.json_dump_generate_checksums = (
            os.getenv(
                "JSON_DUMP_GENERATE_CHECKSUMS", str(self.json_dump_generate_checksums)
            ).lower()
            == "true"
        )
        self.ttl_worker_enabled = (
            os.getenv("TTL_WORKER_ENABLED", str(self.ttl_worker_enabled)).lower()
            == "true"
        )
        self.ttl_dump_schedule = os.getenv("TTL_DUMP_SCHEDULE", self.ttl_dump_schedule)
        self.ttl_dump_batch_size = int(
            os.getenv("TTL_DUMP_BATCH_SIZE", str(self.ttl_dump_batch_size))
        )
        logger.debug("Workers configuration loaded successfully")
        self.ttl_dump_parallel_workers = int(
            os.getenv("TTL_DUMP_PARALLEL_WORKERS", str(self.ttl_dump_parallel_workers))
        )
        self.ttl_dump_compression = (
            os.getenv("TTL_DUMP_COMPRESSION", str(self.ttl_dump_compression)).lower()
            == "true"
        )
        self.ttl_dump_generate_checksums = (
            os.getenv(
                "TTL_DUMP_GENERATE_CHECKSUMS", str(self.ttl_dump_generate_checksums)
            ).lower()
            == "true"
        )
        self.id_worker_enabled = (
            os.getenv("ID_WORKER_ENABLED", str(self.id_worker_enabled)).lower()
            == "true"
        )
        self.incremental_rdf_enabled = (
            os.getenv("INCREMENTAL_RDF_ENABLED", str(self.incremental_rdf_enabled)).lower()
            == "true"
        )
        self.incremental_rdf_consumer_group = os.getenv(
            "INCREMENTAL_RDF_CONSUMER_GROUP", self.incremental_rdf_consumer_group
        )
        self.purge_worker_enabled = (
            os.getenv("PURGE_WORKER_ENABLED", str(self.purge_worker_enabled)).lower()
            == "true"
        )
        self.elasticsearch_enabled = (
            os.getenv("ELASTICSEARCH_ENABLED", str(self.elasticsearch_enabled)).lower()
            == "true"
        )
        self.elasticsearch_host = os.getenv(
            "ELASTICSEARCH_HOST", self.elasticsearch_host
        )
        self.elasticsearch_port = int(
            os.getenv("ELASTICSEARCH_PORT", str(self.elasticsearch_port))
        )
        self.elasticsearch_index = os.getenv(
            "ELASTICSEARCH_INDEX", self.elasticsearch_index
        )
        self.elasticsearch_username = os.getenv(
            "ELASTICSEARCH_USERNAME", self.elasticsearch_username
        )
        self.elasticsearch_password = os.getenv(
            "ELASTICSEARCH_PASSWORD", self.elasticsearch_password
        )
        self.elasticsearch_use_ssl = (
            os.getenv("ELASTICSEARCH_USE_SSL", str(self.elasticsearch_use_ssl)).lower()
            == "true"
        )
        self.elasticsearch_verify_certs = (
            os.getenv(
                "ELASTICSEARCH_VERIFY_CERTS", str(self.elasticsearch_verify_certs)
            ).lower()
            == "true"
        )
        self.elasticsearch_consumer_group = os.getenv(
            "ELASTICSEARCH_CONSUMER_GROUP", self.elasticsearch_consumer_group
        )
        self.meilisearch_enabled = (
            os.getenv("MEILISEARCH_ENABLED", str(self.meilisearch_enabled)).lower()
            == "true"
        )
        self.meilisearch_host = os.getenv("MEILISEARCH_HOST", self.meilisearch_host)
        self.meilisearch_port = int(
            os.getenv("MEILISEARCH_PORT", str(self.meilisearch_port))
        )
        self.meilisearch_api_key = os.getenv(
            "MEILISEARCH_API_KEY", self.meilisearch_api_key
        )
        self.meilisearch_index = os.getenv("MEILISEARCH_INDEX", self.meilisearch_index)
        self.meilisearch_consumer_group = os.getenv(
            "MEILISEARCH_CONSUMER_GROUP", self.meilisearch_consumer_group
        )
        self.purge_worker_enabled = (
            os.getenv("PURGE_ENABLED", str(self.purge_worker_enabled)).lower() == "true"
        )
        self.purge_schedule = os.getenv("PURGE_SCHEDULE", self.purge_schedule)
        self.purge_batch_size = int(
            os.getenv("PURGE_BATCH_SIZE", str(self.purge_batch_size))
        )
        logger.debug(
            f"Workers config loaded: backlink_stats_worker_enabled={self.backlink_stats_worker_enabled}, "
            f"user_stats_worker_enabled={self.user_stats_worker_enabled}, json_worker_enabled={self.json_worker_enabled}"
        )

    def get_log_level(self) -> int:
        """Get the appropriate logging level based on configuration."""
        if self.log_level == "DEBUG":
            return logging.DEBUG
        elif self.log_level == "INFO":
            return logging.INFO
        elif self.log_level == "WARNING":
            return logging.WARNING
        else:
            logger.info(
                "No LOG_LEVEL set or it could not be parsed, defaulting to ERROR"
            )
            return logging.ERROR

    @property
    def get_s3_config(self) -> "S3Config":
        """Convert settings to S3 configuration object.

        Returns:
            S3Config object with the settings.
        """
        from models.data.config.s3 import S3Config

        return S3Config(
            endpoint_url=self.s3_endpoint,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            bucket=self.s3_revisions_bucket,
            region="us-east-1",
        )

    @property
    def get_vitess_config(self) -> "VitessConfig":
        """Convert settings to Vitess configuration object.

        Returns:
            VitessConfig object with the settings.
        """
        from models.data.config.vitess import VitessConfig

        return VitessConfig(
            host=self.vitess_host,
            port=self.vitess_port,
            database=self.vitess_database,
            user=self.vitess_user,
            password=self.vitess_password,
            pool_size=self.vitess_pool_size,
            max_overflow=self.vitess_max_overflow,
            pool_timeout=self.vitess_pool_timeout,
        )

    @property
    def get_entity_change_stream_config(self) -> "StreamConfig":
        """Convert settings to Streaming configuration object."""
        from models.data.config.stream import StreamConfig

        return StreamConfig(
            bootstrap_servers=self.kafka_bootstrap_servers
            if isinstance(self.kafka_bootstrap_servers, list)
            else [self.kafka_bootstrap_servers],
            topic=self.kafka_entitychange_json_topic,
        )

    @property
    def get_entity_diff_stream_config(self) -> "StreamConfig":
        """Convert settings to Streaming configuration object."""
        from models.data.config.stream import StreamConfig

        return StreamConfig(
            bootstrap_servers=self.kafka_bootstrap_servers
            if isinstance(self.kafka_bootstrap_servers, list)
            else [self.kafka_bootstrap_servers],
            topic=self.kafka_entity_diff_topic,
        )

    @property
    def get_incremental_rdf_stream_config(self) -> "StreamConfig":
        """Convert settings to Streaming configuration object for incremental RDF."""
        from models.data.config.stream import StreamConfig

        return StreamConfig(
            bootstrap_servers=self.kafka_bootstrap_servers
            if isinstance(self.kafka_bootstrap_servers, list)
            else [self.kafka_bootstrap_servers],
            topic=self.kafka_incremental_rdf_topic,
        )

    @property
    def get_user_change_stream_config(self) -> "StreamConfig":
        """Convert settings to Streaming configuration object."""
        from models.data.config.stream import StreamConfig

        return StreamConfig(
            bootstrap_servers=self.kafka_bootstrap_servers
            if isinstance(self.kafka_bootstrap_servers, list)
            else [self.kafka_bootstrap_servers],
            topic=self.kafka_userchange_json_topic,
        )


# noinspection PyArgumentList
settings = Settings()
