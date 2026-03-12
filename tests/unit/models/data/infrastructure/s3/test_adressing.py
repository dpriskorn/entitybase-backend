"""Unit tests for S3 addressing model."""

import pytest

from models.data.infrastructure.s3.adressing import S3Adressing


class TestS3Adressing:
    """Unit tests for S3Adressing model."""

    def test_default_addressing_style(self):
        """Test default addressing style is path."""
        addressing = S3Adressing()
        assert addressing.addressing_style == "path"

    def test_custom_addressing_style(self):
        """Test custom addressing style."""
        addressing = S3Adressing(addressing_style="virtual")
        assert addressing.addressing_style == "virtual"

    def test_model_dump(self):
        """Test model_dump()."""
        addressing = S3Adressing(addressing_style="virtual")
        dumped = addressing.model_dump()
        assert dumped == {"addressing_style": "virtual"}

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        addressing = S3Adressing()
        json_str = addressing.model_dump_json()
        assert "path" in json_str
