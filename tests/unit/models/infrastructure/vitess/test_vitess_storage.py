import pytest
from unittest.mock import MagicMock, patch

from models.infrastructure.vitess.storage.statement_storage import (
    StatementSqlStorage,
)
from models.infrastructure.vitess.storage.qualifier_storage import (
    QualifierSqlStorage,
)
from models.infrastructure.vitess.storage.reference_storage import (
    ReferenceSqlStorage,
)
from models.infrastructure.vitess.storage.snak_storage import SnakSqlStorage
from models.infrastructure.vitess.storage.base import BaseSqlStorage


class TestStatementSqlStorage:
    """Tests for StatementSqlStorage."""

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
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
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
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_statement(99999)

        assert result is None

    def test_delete_statement(self, mock_vitess_client):
        """Test deleting a statement."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.delete_statement(12345)

        assert result.success is True

    def test_increment_ref_count(self, mock_vitess_client):
        """Test incrementing reference count."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.increment_ref_count(12345)

        assert result.success is True

    def test_decrement_ref_count(self, mock_vitess_client):
        """Test decrementing reference count."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.decrement_ref_count(12345)

        assert result.success is True

    def test_exists(self, mock_vitess_client):
        """Test checking if statement exists."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = (1,)

        result = storage.exists(12345)

        assert result is True

    def test_exists_not_found(self, mock_vitess_client):
        """Test checking if statement exists returns False."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.exists(99999)

        assert result is False

    def test_store_statement_invalid_hash(self, mock_vitess_client):
        """Test storing statement with invalid hash returns error."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.store_statement(0, {})

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_store_statement_exception(self, mock_vitess_client):
        """Test storing statement when database raises exception."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage.store_statement(12345, {"test": "data"})

        assert result.success is False
        assert "DB error" in result.error

    def test_load_statement_invalid_hash(self, mock_vitess_client):
        """Test loading statement with invalid hash returns None."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.load_statement(0)

        assert result is None

    def test_load_statement_exception(self, mock_vitess_client):
        """Test loading statement when database raises exception."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage.load_statement(12345)

        assert result is None

    def test_load_statements_batch_empty(self, mock_vitess_client):
        """Test loading statements with empty hash list."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.load_statements_batch([])

        assert result == []

    def test_load_statements_batch_all_invalid(self, mock_vitess_client):
        """Test loading statements with all invalid hashes."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.load_statements_batch([0, -1, 0])

        assert result == [None, None, None]

    def test_load_statements_batch_exception(self, mock_vitess_client):
        """Test loading statements batch when database raises exception."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage.load_statements_batch([12345, 67890])

        assert result == [None, None]

    def test_delete_statement_invalid_hash(self, mock_vitess_client):
        """Test deleting statement with invalid hash returns error."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.delete_statement(0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_delete_statement_exception(self, mock_vitess_client):
        """Test deleting statement when database raises exception."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage.delete_statement(12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_increment_ref_count_invalid_hash(self, mock_vitess_client):
        """Test incrementing ref count with invalid hash."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.increment_ref_count(0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_increment_ref_count_exception(self, mock_vitess_client):
        """Test incrementing ref count when database raises exception."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage.increment_ref_count(12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_decrement_ref_count_invalid_hash(self, mock_vitess_client):
        """Test decrementing ref count with invalid hash."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.decrement_ref_count(0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_decrement_ref_count_exception(self, mock_vitess_client):
        """Test decrementing ref count when database raises exception."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage.decrement_ref_count(12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_exists_invalid_hash(self, mock_vitess_client):
        """Test checking existence with invalid hash."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)

        result = storage.exists(0)

        assert result is False

    def test_exists_exception(self, mock_vitess_client):
        """Test checking existence when database raises exception."""
        storage = StatementSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage.exists(12345)

        assert result is False


class TestQualifierSqlStorage:
    """Tests for QualifierSqlStorage."""

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
        storage = QualifierSqlStorage(vitess_client=mock_vitess_client)
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
        storage = QualifierSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_qualifier(99999)

        assert result is None


class TestReferenceSqlStorage:
    """Tests for ReferenceSqlStorage."""

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
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)
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
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_reference(99999)

        assert result is None

    def test_load_reference_success(self, mock_vitess_client):
        """Test loading a reference successfully."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        import json

        mock_cursor.fetchone.return_value = (
            json.dumps(
                {
                    "reference": {"snaks": {}},
                    "hash": 12345,
                    "created_at": "2026-01-01T00:00:00Z",
                }
            ),
        )

        result = storage.load_reference(12345)

        assert result is not None
        assert result.content_hash == 12345

    def test_load_references_batch(self, mock_vitess_client):
        """Test loading multiple references in batch."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        import json

        mock_cursor.fetchall.return_value = [
            (
                12345,
                json.dumps(
                    {
                        "reference": {"snaks": {}},
                        "hash": 12345,
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ),
            ),
            (
                12346,
                json.dumps(
                    {
                        "reference": {"snaks": {}},
                        "hash": 12346,
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ),
            ),
        ]

        result = storage.load_references_batch([12345, 12346])

        assert len(result) == 2
        assert result[0] is not None
        assert result[1] is not None

    def test_load_references_batch_with_none(self, mock_vitess_client):
        """Test loading batch when some references don't exist."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        import json

        mock_cursor.fetchall.return_value = [
            (
                12345,
                json.dumps(
                    {
                        "reference": {"snaks": {}},
                        "hash": 12345,
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ),
            ),
        ]

        result = storage.load_references_batch([12345, 99999])

        assert len(result) == 2
        assert result[0] is not None
        assert result[1] is None

    def test_delete_reference(self, mock_vitess_client):
        """Test deleting a reference."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)

        result = storage.delete_reference(12345)

        assert result.success is True

    def test_increment_ref_count(self, mock_vitess_client):
        """Test incrementing reference count."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)

        result = storage.increment_ref_count(12345)

        assert result.success is True

    def test_decrement_ref_count(self, mock_vitess_client):
        """Test decrementing reference count."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)

        result = storage.decrement_ref_count(12345)

        assert result.success is True

    def test_exists(self, mock_vitess_client):
        """Test checking if reference exists."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = (1,)

        result = storage.exists(12345)

        assert result is True

    def test_exists_not_found(self, mock_vitess_client):
        """Test checking if reference exists returns False."""
        storage = ReferenceSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.exists(99999)

        assert result is False


class TestSnakSqlStorage:
    """Tests for SnakSqlStorage."""

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
        storage = SnakSqlStorage(vitess_client=mock_vitess_client)
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
        storage = SnakSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage.load_snak(99999)

        assert result is None


class TestBaseSqlStorage:
    """Tests for BaseSqlStorage methods directly."""

    @pytest.fixture
    def mock_vitess_client(self):
        """Create a mock vitess client."""
        client = MagicMock()
        cursor = MagicMock()
        client.cursor.__enter__ = MagicMock(return_value=cursor)
        client.cursor.__exit__ = MagicMock(return_value=False)
        return client

    def test_get_ref_count_found(self, mock_vitess_client):
        """Test getting ref count when record exists."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = (5,)

        result = storage._get_ref_count(12345)

        assert result == 5

    def test_get_ref_count_not_found(self, mock_vitess_client):
        """Test getting ref count when record doesn't exist."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage._get_ref_count(12345)

        assert result == 0

    def test_get_ref_count_invalid_hash(self, mock_vitess_client):
        """Test getting ref count with invalid hash."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._get_ref_count(0)

        assert result == 0

    def test_get_ref_count_exception(self, mock_vitess_client):
        """Test getting ref count when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._get_ref_count(12345)

        assert result == 0

    def test_store_invalid_hash(self, mock_vitess_client):
        """Test storing with invalid hash."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._store(0, {})

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_store_exception(self, mock_vitess_client):
        """Test storing when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._store(12345, {"test": "data"})

        assert result.success is False
        assert "DB error" in result.error

    def test_load_invalid_hash(self, mock_vitess_client):
        """Test loading with invalid hash."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._load(0)

        assert result is None

    def test_load_exception(self, mock_vitess_client):
        """Test loading when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._load(12345)

        assert result is None

    def test_load_batch_empty(self, mock_vitess_client):
        """Test loading batch with empty list."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._load_batch([])

        assert result == []

    def test_load_batch_all_invalid(self, mock_vitess_client):
        """Test loading batch with all invalid hashes."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._load_batch([0, -1])

        assert result == [None, None]

    def test_load_batch_exception(self, mock_vitess_client):
        """Test loading batch when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._load_batch([12345, 67890])

        assert result == [None, None]

    def test_delete_invalid_hash(self, mock_vitess_client):
        """Test deleting with invalid hash."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._delete(0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_delete_exception(self, mock_vitess_client):
        """Test deleting when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._delete(12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_delete_success(self, mock_vitess_client):
        """Test deleting successfully."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._delete(12345)

        assert result.success is True

    def test_increment_ref_count_invalid_hash(self, mock_vitess_client):
        """Test incrementing ref count with invalid hash."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._increment_ref_count(0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_increment_ref_count_exception(self, mock_vitess_client):
        """Test incrementing ref count when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._increment_ref_count(12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_increment_ref_count_success(self, mock_vitess_client):
        """Test incrementing ref count successfully."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._increment_ref_count(12345)

        assert result.success is True

    def test_decrement_ref_count_invalid_hash(self, mock_vitess_client):
        """Test decrementing ref count with invalid hash."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._decrement_ref_count(0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_decrement_ref_count_exception(self, mock_vitess_client):
        """Test decrementing ref count when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._decrement_ref_count(12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_decrement_ref_count_success(self, mock_vitess_client):
        """Test decrementing ref count successfully."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._decrement_ref_count(12345)

        assert result.success is True

    def test_exists_invalid_hash(self, mock_vitess_client):
        """Test checking existence with invalid hash."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)

        result = storage._exists(0)

        assert result is False

    def test_exists_exception(self, mock_vitess_client):
        """Test checking existence when database raises exception."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        result = storage._exists(12345)

        assert result is False

    def test_exists_found(self, mock_vitess_client):
        """Test checking existence when found."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = (1,)

        result = storage._exists(12345)

        assert result is True

    def test_exists_not_found(self, mock_vitess_client):
        """Test checking existence when not found."""
        storage = BaseSqlStorage(vitess_client=mock_vitess_client)
        mock_cursor = mock_vitess_client.cursor.__enter__.return_value
        mock_cursor.fetchone.return_value = None

        result = storage._exists(12345)

        assert result is False
