"""Unit tests for settings."""

import os

from models.config.settings import Settings


class TestSettings:
    """Test settings initialization from environment variables."""

    def test_env_vars_override_defaults(self):
        """Test that environment variables override default values."""
        os.environ["S3_ENDPOINT"] = "custom-endpoint:9000"
        settings_instance = Settings()
        assert settings_instance.s3_endpoint == "custom-endpoint:9000"
        del os.environ["S3_ENDPOINT"]

    def test_string_bool_converts_to_bool(self):
        """Test that string 'false'/'true' converts to boolean."""
        os.environ["STREAMING_ENABLED"] = "true"
        settings_instance = Settings()
        assert settings_instance.streaming_enabled is True
        del os.environ["STREAMING_ENABLED"]

    def test_defaults_when_env_not_set(self):
        """Test that defaults are used when env vars not set."""
        settings_instance = Settings()
        assert settings_instance.s3_endpoint == "http://minio:9000"
