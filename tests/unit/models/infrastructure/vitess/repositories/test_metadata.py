"""Unit tests for MetadataRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.metadata import MetadataRepository
from models.data.rest_api.v1.response import MetadataContent


class TestMetadataRepository:
    """Unit tests for MetadataRepository."""

    def test_insert_metadata_content_success(self):
        """Test inserting metadata content successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.insert_metadata_content(12345, "labels")

        assert result.success is True

    def test_insert_metadata_content_database_error(self):
        """Test inserting metadata content with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.insert_metadata_content(12345, "labels")

        assert result.success is False
        assert "DB error" in result.error

    def test_get_metadata_content_success(self):
        """Test getting metadata content successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (5,)
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.get_metadata_content(12345, "labels")

        assert result.success is True
        assert isinstance(result.data, MetadataContent)
        assert result.data.ref_count == 5

    def test_get_metadata_content_not_found(self):
        """Test getting metadata content when not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.get_metadata_content(12345, "labels")

        assert result.success is False
        assert "not found" in result.error

    def test_get_metadata_content_invalid_params(self):
        """Test getting metadata content with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.get_metadata_content(0, "labels")

        assert result.success is False
        assert "Invalid content hash or type" in result.error

    def test_get_metadata_content_empty_type(self):
        """Test getting metadata content with empty type."""
        mock_vitess_client = MagicMock()

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.get_metadata_content(12345, "")

        assert result.success is False
        assert "Invalid content hash or type" in result.error

    def test_decrement_ref_count_success(self):
        """Test decrementing ref count successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (3,)
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(12345, "labels")

        assert result.success is True
        assert result.data is False  # ref_count > 0

    def test_decrement_ref_count_to_zero(self):
        """Test decrementing ref count to zero."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(12345, "labels")

        assert result.success is True
        assert result.data is True  # ref_count <= 0

    def test_decrement_ref_count_not_found(self):
        """Test decrementing ref count when content not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(12345, "labels")

        assert result.success is False
        assert "not found" in result.error

    def test_decrement_ref_count_invalid_params(self):
        """Test decrementing ref count with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(0, "labels")

        assert result.success is False
        assert "Invalid content hash or type" in result.error

    def test_decrement_ref_count_database_error(self):
        """Test decrementing ref count with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(12345, "labels")

        assert result.success is False
        assert "DB error" in result.error

    def test_delete_metadata_content_success(self):
        """Test deleting metadata content successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = MetadataRepository(vitess_client=mock_vitess_client)

        # Should not raise
        repo.delete_metadata_content(12345, "labels")
