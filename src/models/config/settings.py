"""Application configuration and settings management."""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from models.data.config.stream import StreamConfig

if TYPE_CHECKING:
    from models.data.config.s3 import S3Config
    from models.data.config.vitess import VitessConfig

logger = logging.getLogger(__name__)


class Settings(BaseModel):
    """Application settings with environment variable support."""

    # s3
    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "fakekey"
    s3_secret_key: str = "fakesecret"

    # buckets
    s3_references_bucket: str = "references"
    s3_qualifiers_bucket: str = "qualifiers"
    s3_sitelinks_bucket: str = "sitelinks"
    s3_snaks_bucket: str = "snaks"
    s3_statements_bucket: str = "statements"
    s3_terms_bucket: str = "terms"
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

    # rdf
    wikibase_repository_name: str = "wikidata"
    property_registry_path: Path = Path("properties")

    # logging
    log_level: str = "INFO"
    # test_log_level: str = "INFO"
    test_log_http_requests: bool = False
    test_show_progress: bool = True

    # streaming
    streaming_enabled: bool = False
    kafka_bootstrap_servers: str = ""
    kafka_entitychange_json_topic: str = "entitybase.entity_change"
    kafka_entity_diff_topic: str = "wikibase.entity_diff"
    streaming_entity_change_version: str = "1.0.0"
    streaming_endorsechange_version: str = "1.0.0"
    streaming_newthank_version: str = "1.0.0"
    streaming_entity_diff_version: str = "2.0.0"

    # entity version
    entity_version: str = "2.0.0"

    # API configuration
    api_prefix: str = "/v1/entitybase"

    # other
    environment: str = "prod"
    user_agent: str = "Entitybase/1.0 User:So9q"

    # workers
    backlink_stats_enabled: bool = True
    backlink_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backlink_stats_top_limit: int = 100
    user_stats_enabled: bool = True
    user_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM
    general_stats_enabled: bool = True
    general_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM

    # JSON dump worker
    json_dump_enabled: bool = True
    json_dump_schedule: str = "0 2 * * 0"  # Sunday 2AM UTC
    s3_dump_bucket: str = "wikibase-dumps"
    json_dump_batch_size: int = 1000
    json_dump_parallel_workers: int = 50
    json_dump_compression: bool = True
    json_dump_generate_checksums: bool = True

    # TTL dump worker
    ttl_dump_enabled: bool = True
    ttl_dump_schedule: str = "0 3 * * 0"  # Sunday 3AM UTC (after JSON dump)
    ttl_dump_batch_size: int = 1000
    ttl_dump_parallel_workers: int = 50
    ttl_dump_compression: bool = True
    ttl_dump_generate_checksums: bool = True

    def model_post_init(self, context: Any) -> None:
        """Initialize all fields from environment variables.

        This method runs after the model is created to fetch values
        from environment variables, overriding any default values.
        """
        # S3
        self.s3_endpoint = os.getenv("S3_ENDPOINT", self.s3_endpoint)
        self.s3_access_key = os.getenv("S3_ACCESS_KEY", self.s3_access_key)
        self.s3_secret_key = os.getenv("S3_SECRET_KEY", self.s3_secret_key)

        # Vitess
        self.vitess_host = os.getenv("VITESS_HOST", self.vitess_host)
        # if not self.vitess_host:
        #     raise_validation_error("No VITESS_HOST enviroment variable found")
        logger.debug(f"self.vitess_host: {self.vitess_host}")
        self.vitess_port = int(os.getenv("VITESS_PORT", str(self.vitess_port)))
        self.vitess_database = os.getenv("VITESS_DATABASE", self.vitess_database)
        self.vitess_user = os.getenv("VITESS_USER", self.vitess_user)
        self.vitess_password = os.getenv("VITESS_PASSWORD", self.vitess_password)

        # S3 Buckets
        self.s3_references_bucket = os.getenv(
            "S3_REFERENCES_BUCKET", self.s3_references_bucket
        )
        self.s3_qualifiers_bucket = os.getenv(
            "S3_QUALIFIERS_BUCKET", self.s3_qualifiers_bucket
        )
        self.s3_sitelinks_bucket = os.getenv(
            "S3_SITELINKS_BUCKET", self.s3_sitelinks_bucket
        )
        self.s3_snaks_bucket = os.getenv("S3_SNAKS_BUCKET", self.s3_snaks_bucket)
        self.s3_statements_bucket = os.getenv(
            "S3_STATEMENTS_BUCKET", self.s3_statements_bucket
        )
        self.s3_terms_bucket = os.getenv("S3_TERMS_BUCKET", self.s3_terms_bucket)
        self.s3_revisions_bucket = os.getenv(
            "S3_REVISIONS_BUCKET", self.s3_revisions_bucket
        )

        # S3 Versions
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

        # Entity Version
        self.entity_version = os.getenv("ENTITY_VERSION", self.entity_version)

        # API Configuration
        self.api_prefix = os.getenv("API_PREFIX", self.api_prefix)

        # Streaming Versions
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

        # Streaming Config
        self.streaming_enabled = (
            os.getenv("STREAMING_ENABLED", "false").lower() == "true"
        )
        self.kafka_bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", self.kafka_bootstrap_servers
        )
        self.kafka_entitychange_json_topic = os.getenv(
            "KAFKA_ENTITY_CHANGE_TOPIC", self.kafka_entitychange_json_topic
        )
        self.kafka_entity_diff_topic = os.getenv(
            "KAFKA_ENTITY_DIFF_TOPIC", self.kafka_entity_diff_topic
        )

        # Other
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.environment = os.getenv("ENVIRONMENT", self.environment)
        self.user_agent = os.getenv("USER_AGENT", self.user_agent)

        # RDF
        self.wikibase_repository_name = os.getenv(
            "WIKIBASE_REPOSITORY_NAME", self.wikibase_repository_name
        )
        self.property_registry_path = Path(
            os.getenv("PROPERTY_REGISTRY_PATH", self.property_registry_path)
        )

        # Workers
        self.backlink_stats_enabled = (
            os.getenv(
                "BACKLINK_STATS_ENABLED", str(self.backlink_stats_enabled)
            ).lower()
            == "true"
        )
        self.user_stats_enabled = (
            os.getenv("USER_STATS_ENABLED", str(self.user_stats_enabled)).lower()
            == "true"
        )
        self.general_stats_enabled = (
            os.getenv("GENERAL_STATS_ENABLED", str(self.general_stats_enabled)).lower()
            == "true"
        )
        self.json_dump_enabled = (
            os.getenv("JSON_DUMP_ENABLED", str(self.json_dump_enabled)).lower()
            == "true"
        )
        self.json_dump_schedule = os.getenv("JSON_DUMP_SCHEDULE", self.json_dump_schedule)
        self.s3_dump_bucket = os.getenv("S3_DUMP_BUCKET", self.s3_dump_bucket)
        self.json_dump_batch_size = int(
            os.getenv("JSON_DUMP_BATCH_SIZE", str(self.json_dump_batch_size))
        )
        self.json_dump_parallel_workers = int(
            os.getenv("JSON_DUMP_PARALLEL_WORKERS", str(self.json_dump_parallel_workers))
        )
        self.json_dump_compression = (
            os.getenv("JSON_DUMP_COMPRESSION", str(self.json_dump_compression)).lower()
            == "true"
        )
        self.json_dump_generate_checksums = (
            os.getenv("JSON_DUMP_GENERATE_CHECKSUMS", str(self.json_dump_generate_checksums)).lower()
            == "true"
        )
        self.ttl_dump_enabled = (
            os.getenv("TTL_DUMP_ENABLED", str(self.ttl_dump_enabled)).lower()
            == "true"
        )
        self.ttl_dump_schedule = os.getenv("TTL_DUMP_SCHEDULE", self.ttl_dump_schedule)
        self.ttl_dump_batch_size = int(
            os.getenv("TTL_DUMP_BATCH_SIZE", str(self.ttl_dump_batch_size))
        )
        self.ttl_dump_parallel_workers = int(
            os.getenv("TTL_DUMP_PARALLEL_WORKERS", str(self.ttl_dump_parallel_workers))
        )
        self.ttl_dump_compression = (
            os.getenv("TTL_DUMP_COMPRESSION", str(self.ttl_dump_compression)).lower()
            == "true"
        )
        self.ttl_dump_generate_checksums = (
            os.getenv("TTL_DUMP_GENERATE_CHECKSUMS", str(self.ttl_dump_generate_checksums)).lower()
            == "true"
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


# noinspection PyArgumentList
settings = Settings()
