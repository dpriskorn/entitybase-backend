"""Application configuration and settings management."""

import logging
import os
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from models.infrastructure.s3.s3_client import S3Config
    from models.infrastructure.vitess_client import VitessConfig


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(env_file=".env")

    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "fakekey"
    s3_secret_key: str = "fakesecret"
    s3_bucket: str = "testbucket"
    s3_references_bucket: str = "testbucket-references"
    s3_qualifiers_bucket: str = "testbucket-qualifiers"
    vitess_host: str = "vitess"
    vitess_port: int = 15309
    vitess_database: str = "entitybase"
    vitess_user: str = "root"
    vitess_password: str = ""
    s3_revision_version: str = "latest"
    s3_statement_version: str = "latest"
    wmf_recentchange_version: str = "latest"
    wikibase_repository_name: str = "wikidata"
    property_registry_path: str = "properties"
    log_level: str = "INFO"
    test_log_level: str = "INFO"
    test_log_http_requests: bool = False
    test_show_progress: bool = True
    expose_original_exceptions: bool = False
    enable_streaming: bool = False
    kafka_brokers: str = ""
    kafka_topic: str = "wikibase.entity_change"
    kafka_rdf_topic: str = "wikibase.entity_diff"
    backlink_stats_enabled: bool = True
    backlink_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backlink_stats_top_limit: int = 100
    user_stats_enabled: bool = True
    user_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM
    general_stats_enabled: bool = True
    general_stats_schedule: str = "0 2 * * *"  # Daily at 2 AM

    def get_log_level(self) -> int:
        """Get the appropriate logging level based on configuration.

        Returns:
            The logging level as an integer.
        """
        if os.getenv("TEST_LOG_LEVEL"):
            return getattr(logging, self.test_log_level.upper(), logging.INFO)
        return getattr(logging, self.log_level.upper(), logging.INFO)

    def to_s3_config(self) -> "S3Config":
        """Convert settings to S3 configuration object.

        Returns:
            S3Config object with the settings.
        """
        from models.infrastructure.s3.s3_client import S3Config

        return S3Config(
            endpoint_url=self.s3_endpoint,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            bucket=self.s3_bucket,
        )

    def to_vitess_config(self) -> "VitessConfig":
        """Convert settings to Vitess configuration object.

        Returns:
            VitessConfig object with the settings.
        """
        from models.infrastructure.vitess_client import VitessConfig

        return VitessConfig(
            host=self.vitess_host,
            port=self.vitess_port,
            database=self.vitess_database,
            user=self.vitess_user,
            password=self.vitess_password,
        )


# noinspection PyArgumentList
settings = Settings()
