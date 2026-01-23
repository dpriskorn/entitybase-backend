"""Unit tests for SitelinksHashes model."""

from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.data.infrastructure.s3.sitelink_data import S3SitelinkData


class TestSitelinksHashes:
    """Unit tests for SitelinksHashes."""

    def test_sitelinks_hashes_creation(self):
        """Test creating SitelinksHashes with S3SitelinkData."""
        data = {
            "enwiki": S3SitelinkData(title_hash=123, badges=["featured"]),
            "dewiki": S3SitelinkData(title_hash=456, badges=[])
        }
        hashes = SitelinksHashes(root=data)
        assert hashes.root == data
        assert hashes.root["enwiki"].title_hash == 123
        assert hashes.root["enwiki"].badges == ["featured"]

    def test_sitelinks_hashes_empty(self):
        """Test SitelinksHashes with empty dict."""
        hashes = SitelinksHashes(root={})
        assert hashes.root == {}