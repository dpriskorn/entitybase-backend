"""Unit tests for StatementRepository."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.statement import StatementRepository


class TestStatementRepository:
    """Unit tests for StatementRepository."""

    def test_insert_content_success(self):
        """Test successful content insertion."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # not exists
        mock_vitess_client.cursor = mock_cursor

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.insert_content(12345)

        assert result.success is True

    def test_insert_content_already_exists(self):
        """Test inserting content that already exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # exists
        mock_vitess_client.cursor = mock_cursor

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.insert_content(12345)

        assert result.success is False
        assert "already exists" in result.error

    def test_increment_ref_count_success(self):
        """Test successful ref count increment."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (5,)  # new count
        mock_vitess_client.cursor = mock_cursor

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.increment_ref_count(12345)

        assert result.success is True
        assert result.data == 5

    def test_increment_ref_count_invalid_hash(self):
        """Test increment with invalid hash."""
        mock_vitess_client = MagicMock()

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.increment_ref_count(0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_decrement_ref_count_success(self):
        """Test successful ref count decrement."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (3,)  # new count
        mock_vitess_client.cursor = mock_cursor

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(12345)

        assert result.success is True
        assert result.data == 3

    def test_get_orphaned_success(self):
        """Test getting orphaned content."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(12345,), (67890,)]
        mock_vitess_client.cursor = mock_cursor

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.get_orphaned(30, 10)

        assert result.success is True
        assert result.data == [12345, 67890]

    def test_get_orphaned_invalid_params(self):
        """Test get_orphaned with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.get_orphaned(0, 10)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_most_used_success(self):
        """Test getting most used content."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(12345,), (67890,)]
        mock_vitess_client.cursor = mock_cursor

        repo = StatementRepository(vitess_client=mock_vitess_client)

        result = repo.get_most_used(10)

        assert result == [12345, 67890]
