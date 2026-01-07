import logging
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    s3_endpoint: str = "http://minio:9000"
    s3_access_key: str = "fakekey"
    s3_secret_key: str = "fakesecret"
    s3_bucket: str = "testbucket"
    vitess_host: str = "vitess"
    vitess_port: int = 15309
    vitess_database: str = "wikibase"
    vitess_user: str = "root"
    vitess_password: str = ""
    s3_revision_schema_version: str = "1.2.0"
    wikibase_repository_name: str = "wikidata"
    property_registry_path: str = "properties"
    log_level: str = "INFO"
    test_log_level: str = "INFO"
    test_log_http_requests: bool = False
    test_show_progress: bool = True

    def get_log_level(self) -> int:
        if os.getenv("TEST_LOG_LEVEL"):
            return getattr(logging, self.test_log_level.upper(), logging.INFO)
        return getattr(logging, self.log_level.upper(), logging.INFO)

    def to_s3_config(self) -> Any:
        from models.infrastructure.s3_client import S3Config

        return S3Config(
            endpoint_url=self.s3_endpoint,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            bucket=self.s3_bucket,
        )

    def to_vitess_config(self) -> Any:
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
