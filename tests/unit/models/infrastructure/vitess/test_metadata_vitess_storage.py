"""Unit tests for MetadataVitessStorage and SitelinkVitessStorage."""

from unittest.mock import MagicMock

import pytest

from models.infrastructure.vitess.storage.metadata_storage import (
    MetadataVitessStorage,
    SitelinkVitessStorage,
)


class TestMetadataVitessStorage:
    """Unit tests for MetadataVitessStorage class."""

    @pytest.fixture
    def mock_vitess_client(self):
        """Create a mock vitess client."""
        client = MagicMock()
        cursor = MagicMock()
        client.cursor.__enter__ = MagicMock(return_value=cursor)
        client.cursor.__exit__ = MagicMock(return_value=False)
        return client

    def test_store_metadata(self, mock_vitess_client):
        """Test storing metadata."""
        storage = MetadataVitessStorage(vitess_client=mock_vitess_client)

        result = storage.store_metadata(12345, "label", "Test Label")

        assert result.success is True
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.assert_called_once()

    def test_store_metadata_error(self, mock_vitess_client):
        """Test storing metadata with error."""
        storage = MetadataVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        result = storage.store_metadata(12345, "label", "Test Label")

        assert result.success is False
        assert "Database error" in result.error

    def test_load_metadata_found(self, mock_vitess_client):
        """Test loading metadata that exists."""
        storage = MetadataVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = ("Test Label",)

        result = storage.load_metadata(12345, "label")

        assert result == "Test Label"

    def test_load_metadata_not_found(self, mock_vitess_client):
        """Test loading metadata that doesn't exist."""
        storage = MetadataVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_metadata(99999, "label")

        assert result is None

    def test_load_metadata_error(self, mock_vitess_client):
        """Test loading metadata with error."""
        storage = MetadataVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        result = storage.load_metadata(12345, "label")

        assert result is None

    def test_delete_metadata(self, mock_vitess_client):
        """Test deleting metadata."""
        storage = MetadataVitessStorage(vitess_client=mock_vitess_client)

        result = storage.delete_metadata(12345, "label")

        assert result.success is True
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        assert mock_cursor.execute.call_count == 2

    def test_delete_metadata_error(self, mock_vitess_client):
        """Test deleting metadata with error."""
        storage = MetadataVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        result = storage.delete_metadata(12345, "label")

        assert result.success is False


class TestSitelinkVitessStorage:
    """Unit tests for SitelinkVitessStorage class."""

    @pytest.fixture
    def mock_vitess_client(self):
        """Create a mock vitess client."""
        client = MagicMock()
        cursor = MagicMock()
        client.cursor.__enter__ = MagicMock(return_value=cursor)
        client.cursor.__exit__ = MagicMock(return_value=False)
        return client

    def test_store_sitelink(self, mock_vitess_client):
        """Test storing sitelink."""
        storage = SitelinkVitessStorage(vitess_client=mock_vitess_client)

        result = storage.store_sitelink(12345, "Main_Page")

        assert result.success is True
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.assert_called_once()

    def test_store_sitelink_error(self, mock_vitess_client):
        """Test storing sitelink with error."""
        storage = SitelinkVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        result = storage.store_sitelink(12345, "Main_Page")

        assert result.success is False
        assert "Database error" in result.error

    def test_load_sitelink_found(self, mock_vitess_client):
        """Test loading sitelink that exists."""
        storage = SitelinkVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = ("Main_Page",)

        result = storage.load_sitelink(12345)

        assert result == "Main_Page"

    def test_load_sitelink_not_found(self, mock_vitess_client):
        """Test loading sitelink that doesn't exist."""
        storage = SitelinkVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_sitelink(99999)

        assert result is None

    def test_load_sitelink_error(self, mock_vitess_client):
        """Test loading sitelink with error."""
        storage = SitelinkVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        result = storage.load_sitelink(12345)

        assert result is None

    def test_delete_sitelink(self, mock_vitess_client):
        """Test deleting sitelink."""
        storage = SitelinkVitessStorage(vitess_client=mock_vitess_client)

        result = storage.delete_sitelink(12345)

        assert result.success is True
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        assert mock_cursor.execute.call_count == 2

    def test_delete_sitelink_error(self, mock_vitess_client):
        """Test deleting sitelink with error."""
        storage = SitelinkVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        result = storage.delete_sitelink(12345)

        assert result.success is False
