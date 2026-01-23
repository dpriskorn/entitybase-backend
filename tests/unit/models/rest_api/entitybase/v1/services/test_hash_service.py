"""Unit tests for HashService."""

from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.data.infrastructure.s3.sitelink_data import S3SitelinkData
from models.rest_api.entitybase.v1.services.hash_service import HashService


class TestHashService:
    """Unit tests for HashService."""

    def test_hash_sitelinks(self):
        """Test hashing sitelinks with badges."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        service = HashService(state=state)

        sitelinks = {
            "enwiki": {"title": "Test Page", "badges": ["featured"]},
            "dewiki": {"title": "Test Seite", "badges": []}
        }

        # Mock hash_string
        with patch('models.internal_representation.metadata_extractor.MetadataExtractor.hash_string', side_effect=lambda x: hash(x)):
            result = service.hash_sitelinks(sitelinks)

            assert isinstance(result, SitelinksHashes)
            assert "enwiki" in result.root
            assert isinstance(result.root["enwiki"], S3SitelinkData)
            assert result.root["enwiki"].title_hash == hash("Test Page")
            assert result.root["enwiki"].badges == ["featured"]
            assert result.root["dewiki"].title_hash == hash("Test Seite")
            assert result.root["dewiki"].badges == []

            # Verify S3 calls
            s3_client.store_sitelink_metadata.assert_any_call("Test Page", hash("Test Page"))
            s3_client.store_sitelink_metadata.assert_any_call("Test Seite", hash("Test Seite"))

    def test_hash_sitelinks_no_title(self):
        """Test hashing sitelinks skips entries without title."""
        state = MagicMock()
        s3_client = MagicMock()
        state.s3_client = s3_client
        service = HashService(state=state)

        sitelinks = {
            "enwiki": {"badges": ["featured"]},  # No title
            "dewiki": {"title": "Test Seite", "badges": []}
        }

        with patch('models.internal_representation.metadata_extractor.MetadataExtractor.hash_string', side_effect=lambda x: hash(x)):
            result = service.hash_sitelinks(sitelinks)

            assert "enwiki" not in result.root
            assert "dewiki" in result.root
            assert result.root["dewiki"].title_hash == hash("Test Seite")