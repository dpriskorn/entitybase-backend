"""Unit tests for SitelinkHashes model."""

from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes
from models.data.infrastructure.s3.sitelink_data import S3SitelinkData


class TestSitelinkHashes:
    """Unit tests for SitelinkHashes."""

    def test_sitelink_hashes_creation(self):
        """Test creating SitelinkHashes with S3SitelinkData."""
        data = {
            "enwiki": S3SitelinkData(title_hash=123, badges=["featured"]),
            "dewiki": S3SitelinkData(title_hash=456, badges=[])
        }
        # noinspection PyArgumentList
        hashes = SitelinkHashes(root=data)
        assert hashes.root == data
        assert hashes.root["enwiki"].title_hash == 123
        assert hashes.root["enwiki"].badges == ["featured"]

    def test_sitelink_hashes_empty(self):
        """Test SitelinkHashes with empty dict."""
        # noinspection PyArgumentList
        hashes = SitelinkHashes(root={})
        assert hashes.root == {}