import pytest
from unittest.mock import MagicMock, patch

from models.infrastructure.vitess.storage.statement_storage import (
    StatementVitessStorage,
)
from models.infrastructure.vitess.storage.qualifier_storage import (
    QualifierVitessStorage,
)
from models.infrastructure.vitess.storage.reference_storage import (
    ReferenceVitessStorage,
)
from models.infrastructure.vitess.storage.snak_storage import SnakVitessStorage


class TestStatementVitessStorage:
    """Tests for StatementVitessStorage."""

    @pytest.fixture
    def mock_vitess_client(self):
        """Create a mock vitess client."""
        client = MagicMock()
        cursor = MagicMock()
        client.cursor.__enter__ = MagicMock(return_value=cursor)
        client.cursor.__exit__ = MagicMock(return_value=False)
        return client

    def test_store_statement(self, mock_vitess_client):
        """Test storing a statement."""
        storage = StatementVitessStorage(vitess_client=mock_vitess_client)
        statement_data = {
            "statement": {"type": "statement", "mainsnak": {}},
            "schema": "1.0.0",
            "hash": 12345,
            "created_at": "2026-01-01T00:00:00Z",
        }

        result = storage.store_statement(12345, statement_data)

        assert result.success is True

    def test_load_statement_not_found(self, mock_vitess_client):
        """Test loading a non-existent statement returns None."""
        storage = StatementVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_statement(99999)

        assert result is None

    def test_delete_statement(self, mock_vitess_client):
        """Test deleting a statement."""
        storage = StatementVitessStorage(vitess_client=mock_vitess_client)

        result = storage.delete_statement(12345)

        assert result.success is True

    def test_increment_ref_count(self, mock_vitess_client):
        """Test incrementing reference count."""
        storage = StatementVitessStorage(vitess_client=mock_vitess_client)

        result = storage.increment_ref_count(12345)

        assert result.success is True

    def test_decrement_ref_count(self, mock_vitess_client):
        """Test decrementing reference count."""
        storage = StatementVitessStorage(vitess_client=mock_vitess_client)

        result = storage.decrement_ref_count(12345)

        assert result.success is True

    def test_exists(self, mock_vitess_client):
        """Test checking if statement exists."""
        storage = StatementVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = (1,)

        result = storage.exists(12345)

        assert result is True

    def test_exists_not_found(self, mock_vitess_client):
        """Test checking if statement exists returns False."""
        storage = StatementVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.exists(99999)

        assert result is False


class TestQualifierVitessStorage:
    """Tests for QualifierVitessStorage."""

    @pytest.fixture
    def mock_vitess_client(self):
        """Create a mock vitess client."""
        client = MagicMock()
        cursor = MagicMock()
        client.cursor.__enter__ = MagicMock(return_value=cursor)
        client.cursor.__exit__ = MagicMock(return_value=False)
        return client

    def test_store_qualifier(self, mock_vitess_client):
        """Test storing a qualifier."""
        storage = QualifierVitessStorage(vitess_client=mock_vitess_client)
        from models.data.infrastructure.s3.qualifier_data import S3QualifierData

        qualifier_data = S3QualifierData(
            qualifier={"property": "P31", "value": "test"},
            hash=12345,
            created_at="2026-01-01T00:00:00Z",
        )

        result = storage.store_qualifier(12345, qualifier_data)

        assert result.success is True

    def test_load_qualifier_not_found(self, mock_vitess_client):
        """Test loading a non-existent qualifier returns None."""
        storage = QualifierVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_qualifier(99999)

        assert result is None


class TestReferenceVitessStorage:
    """Tests for ReferenceVitessStorage."""

    @pytest.fixture
    def mock_vitess_client(self):
        """Create a mock vitess client."""
        client = MagicMock()
        cursor = MagicMock()
        client.cursor.__enter__ = MagicMock(return_value=cursor)
        client.cursor.__exit__ = MagicMock(return_value=False)
        return client

    def test_store_reference(self, mock_vitess_client):
        """Test storing a reference."""
        storage = ReferenceVitessStorage(vitess_client=mock_vitess_client)
        from models.data.infrastructure.s3.reference_data import S3ReferenceData

        reference_data = S3ReferenceData(
            reference={"snaks": {}},
            hash=12345,
            created_at="2026-01-01T00:00:00Z",
        )

        result = storage.store_reference(12345, reference_data)

        assert result.success is True

    def test_load_reference_not_found(self, mock_vitess_client):
        """Test loading a non-existent reference returns None."""
        storage = ReferenceVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_reference(99999)

        assert result is None


class TestSnakVitessStorage:
    """Tests for SnakVitessStorage."""

    @pytest.fixture
    def mock_vitess_client(self):
        """Create a mock vitess client."""
        client = MagicMock()
        cursor = MagicMock()
        client.cursor.__enter__ = MagicMock(return_value=cursor)
        client.cursor.__exit__ = MagicMock(return_value=False)
        return client

    def test_store_snak(self, mock_vitess_client):
        """Test storing a snak."""
        storage = SnakVitessStorage(vitess_client=mock_vitess_client)
        from models.data.infrastructure.s3.snak_data import S3SnakData

        snak_data = S3SnakData(
            snak={"snaktype": "value", "property": "P31"},
            hash=12345,
            schema="1.0.0",
            created_at="2026-01-01T00:00:00Z",
        )

        result = storage.store_snak(12345, snak_data)

        assert result.success is True

    def test_load_snak_not_found(self, mock_vitess_client):
        """Test loading a non-existent snak returns None."""
        storage = SnakVitessStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_snak(99999)

        assert result is None
