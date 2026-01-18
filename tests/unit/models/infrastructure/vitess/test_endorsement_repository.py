"""Unit tests for endorsement repository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone

from models.common import OperationResult
from models.endorsements import StatementEndorsement
from models.infrastructure.vitess.endorsement_repository import EndorsementRepository


class TestEndorsementRepository:
    @pytest.fixture
    def mock_connection_manager(self):
        return Mock()

    @pytest.fixture
    def repository(self, mock_connection_manager):
        return EndorsementRepository(mock_connection_manager)

    def test_create_endorsement_success(self, repository, mock_connection_manager):
        """Test successful endorsement creation."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock statement exists check
        mock_cursor.fetchone.side_effect = [
            (1,),
            None,
        ]  # statement exists, no existing endorsement
        mock_cursor.lastrowid = 789

        result = repository.create_endorsement(123, 456789)

        assert result.success is True
        assert result.data == 789
        assert result.error is None

    def test_create_endorsement_invalid_parameters(self, repository):
        """Test create_endorsement with invalid parameters."""
        result = repository.create_endorsement(0, 456789)
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.create_endorsement(123, 0)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_create_endorsement_statement_not_found(
        self, repository, mock_connection_manager
    ):
        """Test endorsement creation when statement doesn't exist."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None  # statement doesn't exist

        result = repository.create_endorsement(123, 456789)

        assert result.success is False
        assert "Statement not found" in result.error

    def test_create_endorsement_already_exists(
        self, repository, mock_connection_manager
    ):
        """Test endorsement creation when endorsement already exists."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [
            (1,),
            (5, None),
        ]  # statement exists, existing endorsement

        result = repository.create_endorsement(123, 456789)

        assert result.success is False
        assert "Already endorsed this statement" in result.error

    def test_create_endorsement_reactivate_withdrawn(
        self, repository, mock_connection_manager
    ):
        """Test endorsement creation reactivates previously withdrawn endorsement."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [
            (1,),
            (5, "2023-01-01"),
        ]  # statement exists, withdrawn endorsement
        mock_cursor.rowcount = 1

        result = repository.create_endorsement(123, 456789)

        assert result.success is True
        assert result.data == 5  # Returns existing endorsement ID

    def test_create_endorsement_database_error(
        self, repository, mock_connection_manager
    ):
        """Test endorsement creation with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = Exception("Database connection failed")

        result = repository.create_endorsement(123, 456789)

        assert result.success is False
        assert "Database connection failed" in result.error

    def test_withdraw_endorsement_success(self, repository, mock_connection_manager):
        """Test successful endorsement withdrawal."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (5,)  # existing active endorsement

        result = repository.withdraw_endorsement(123, 456789)

        assert result.success is True
        assert result.data == 5

    def test_withdraw_endorsement_not_found(self, repository, mock_connection_manager):
        """Test withdrawal when no active endorsement exists."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None  # no active endorsement

        result = repository.withdraw_endorsement(123, 456789)

        assert result.success is False
        assert "No active endorsement found" in result.error

    def test_withdraw_endorsement_invalid_parameters(self, repository):
        """Test withdraw_endorsement with invalid parameters."""
        result = repository.withdraw_endorsement(0, 456789)
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.withdraw_endorsement(123, 0)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_withdraw_endorsement_database_error(
        self, repository, mock_connection_manager
    ):
        """Test withdrawal with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = Exception("Database error")

        result = repository.withdraw_endorsement(123, 456789)

        assert result.success is False
        assert "Database error" in result.error

    def test_get_batch_statement_endorsement_stats_success(
        self, repository, mock_connection_manager
    ):
        """Test successful batch endorsement stats retrieval."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (456789, 10, 8, 2),  # hash, total, active, withdrawn
        ]

        result = repository.get_batch_statement_endorsement_stats([456789])

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["statement_hash"] == 456789
        assert result.data[0]["total_endorsements"] == 10
        assert result.data[0]["active_endorsements"] == 8
        assert result.data[0]["withdrawn_endorsements"] == 2

    def test_get_batch_statement_endorsement_stats_multiple_hashes(
        self, repository, mock_connection_manager
    ):
        """Test batch endorsement stats retrieval with multiple statement hashes."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (456789, 10, 8, 2),
            (456790, 5, 5, 0),
            (456791, 0, 0, 0),  # No endorsements
        ]

        result = repository.get_batch_statement_endorsement_stats(
            [456789, 456790, 456791]
        )

        assert result.success is True
        assert len(result.data) == 3
        # Check first
        assert result.data[0]["statement_hash"] == 456789
        assert result.data[0]["total_endorsements"] == 10
        # Check second
        assert result.data[1]["statement_hash"] == 456790
        assert result.data[1]["total_endorsements"] == 5
        # Check third (no endorsements)
        assert result.data[2]["statement_hash"] == 456791
        assert result.data[2]["total_endorsements"] == 0

    def test_get_batch_statement_endorsement_stats_empty(
        self, repository, mock_connection_manager
    ):
        """Test batch stats when statement has no endorsements."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []  # no endorsements

        result = repository.get_batch_statement_endorsement_stats([456789])

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["statement_hash"] == 456789
        assert result.data[0]["total_endorsements"] == 0
        assert result.data[0]["active_endorsements"] == 0
        assert result.data[0]["withdrawn_endorsements"] == 0

    def test_get_batch_statement_endorsement_stats_invalid_params(self, repository):
        """Test batch stats with invalid parameters."""
        result = repository.get_batch_statement_endorsement_stats([])
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.get_batch_statement_endorsement_stats(
            [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                42,
                43,
                44,
                45,
                46,
                47,
                48,
                49,
                50,
                51,
            ]
        )
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_batch_statement_endorsement_stats_database_error(
        self, repository, mock_connection_manager
    ):
        """Test batch statement endorsement stats with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_batch_statement_endorsement_stats([456789])

        assert result.success is False
        assert "Database error" in result.error

    def test_get_user_endorsement_stats_success(
        self, repository, mock_connection_manager
    ):
        """Test successful user endorsement stats retrieval."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [(15,), (12,)]  # total given, active

        result = repository.get_user_endorsement_stats(123)

        assert result.success is True
        assert result.data["total_endorsements_given"] == 15
        assert result.data["total_endorsements_active"] == 12

    def test_get_user_endorsement_stats_invalid_parameters(self, repository):
        """Test get_user_endorsement_stats with invalid parameters."""
        result = repository.get_user_endorsement_stats(0)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_user_endorsement_stats_database_error(
        self, repository, mock_connection_manager
    ):
        """Test user endorsement stats retrieval with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = Exception("Database error")

        result = repository.get_user_endorsement_stats(123)

        assert result.success is False
        assert "Database error" in result.error

    def test_get_statement_endorsements_success(
        self, repository, mock_connection_manager
    ):
        """Test successful statement endorsements retrieval."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, 123, 456789, "2023-01-01T00:00:00Z", None),
        ]
        mock_cursor.fetchone.return_value = (1,)  # total count

        result = repository.get_statement_endorsements(456789, 50, 0, False)

        assert result.success is True
        assert len(result.data["endorsements"]) == 1
        assert result.data["total_count"] == 1
        assert result.data["has_more"] is False

    def test_get_statement_endorsements_with_include_removed(
        self, repository, mock_connection_manager
    ):
        """Test statement endorsements retrieval with include_removed=True."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, 123, 456789, "2023-01-01T00:00:00Z", None),
            (2, 124, 456789, "2023-01-02T00:00:00Z", "2023-01-03T00:00:00Z"),
        ]
        mock_cursor.fetchone.return_value = (2,)  # total count

        result = repository.get_statement_endorsements(456789, 50, 0, True)

        assert result.success is True
        assert len(result.data["endorsements"]) == 2
        assert result.data["total_count"] == 2
        assert result.data["has_more"] is False

        # Check that the query doesn't include removed_at IS NULL condition
        calls = mock_cursor.execute.call_args_list
        query = calls[0][0][0]  # First call's query
        assert "removed_at IS NULL" not in query

    def test_get_statement_endorsements_invalid_parameters(self, repository):
        """Test get_statement_endorsements with invalid parameters."""
        result = repository.get_statement_endorsements(0, 50, 0, False)
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.get_statement_endorsements(456789, 0, 0, False)
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.get_statement_endorsements(456789, 50, -1, False)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_statement_endorsements_database_error(
        self, repository, mock_connection_manager
    ):
        """Test statement endorsements retrieval with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_statement_endorsements(456789, 50, 0, False)

        assert result.success is False
        assert "Database error" in result.error

    def test_get_user_endorsements_database_error(
        self, repository, mock_connection_manager
    ):
        """Test user endorsements retrieval with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_user_endorsements(123, 50, 0, False)

        assert result.success is False
        assert "Database error" in result.error

    def test_get_user_endorsement_stats_database_error(
        self, repository, mock_connection_manager
    ):
        """Test user endorsement stats with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_user_endorsement_stats(123)

        assert result.success is False
        assert "Database error" in result.error

    def test_get_batch_statement_endorsement_stats_database_error(
        self, repository, mock_connection_manager
    ):
        """Test batch statement endorsement stats with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_batch_statement_endorsement_stats([456789])

        assert result.success is False
        assert "Database error" in result.error

    def test_get_user_endorsements_success(self, repository, mock_connection_manager):
        """Test successful user endorsements retrieval."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, 123, 456789, "2023-01-01T00:00:00Z", None),
        ]
        mock_cursor.fetchone.return_value = (1,)  # total count

        result = repository.get_user_endorsements(123, 50, 0, False)

        assert result.success is True
        assert len(result.data["endorsements"]) == 1
        assert result.data["total_count"] == 1
        assert result.data["has_more"] is False

    def test_get_user_endorsements_with_include_removed(
        self, repository, mock_connection_manager
    ):
        """Test user endorsements retrieval with include_removed=True."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, 123, 456789, "2023-01-01T00:00:00Z", None),
            (2, 123, 456790, "2023-01-02T00:00:00Z", "2023-01-03T00:00:00Z"),
        ]
        mock_cursor.fetchone.return_value = (2,)  # total count

        result = repository.get_user_endorsements(123, 50, 0, True)

        assert result.success is True
        assert len(result.data["endorsements"]) == 2
        assert result.data["total_count"] == 2
        assert result.data["has_more"] is False

        # Check that the query doesn't include AND removed_at IS NULL
        calls = mock_cursor.execute.call_args_list
        query = calls[0][0][0]  # First call's query
        assert "AND removed_at IS NULL" not in query

    def test_get_user_endorsements_invalid_parameters(self, repository):
        """Test get_user_endorsements with invalid parameters."""
        result = repository.get_user_endorsements(0, 50, 0, False)
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.get_user_endorsements(123, 0, 0, False)
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.get_user_endorsements(123, 50, -1, False)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_user_endorsements_database_error(
        self, repository, mock_connection_manager
    ):
        """Test user endorsements retrieval with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_user_endorsements(123, 50, 0, False)

        assert result.success is False
        assert "Database error" in result.error
