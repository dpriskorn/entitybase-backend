"""Unit tests for EndorsementRepository."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.endorsement import EndorsementRepository


class TestEndorsementRepository:
    """Unit tests for EndorsementRepository."""

    def test_create_endorsement_success(self):
        """Test successful endorsement creation."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # statement exists
        mock_cursor.lastrowid = 123
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is True
        assert result.data == 123

    def test_create_endorsement_statement_not_found(self):
        """Test endorsement creation when statement doesn't exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # statement not found
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is False
        assert "Statement not found" in result.error

    def test_create_endorsement_already_exists(self):
        """Test endorsement creation when already endorsed."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(1,), (1, None)]  # statement exists, existing active endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is False
        assert "Already endorsed" in result.error

    def test_create_endorsement_invalid_params(self):
        """Test endorsement creation with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(0, 789)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_withdraw_endorsement_success(self):
        """Test successful endorsement withdrawal."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (123,)  # existing endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(456, 789)

        assert result.success is True
        assert result.data == 123

    def test_withdraw_endorsement_no_active(self):
        """Test withdrawal when no active endorsement exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # no active endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(456, 789)

        assert result.success is False
        assert "No active endorsement found" in result.error

    def test_get_statement_endorsements_success(self):
        """Test getting statement endorsements."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 456, 789, "2023-01-01", None)],  # endorsements
            (1,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_statement_endorsements(789)

        assert result.success is True
        assert len(result.data["endorsements"]) == 1
        assert result.data["total_count"] == 1

    def test_get_statement_endorsements_invalid_params(self):
        """Test getting endorsements with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_statement_endorsements(0)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_user_endorsement_stats_success(self):
        """Test getting user endorsement stats."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(10,), (7,)]  # total, active
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsement_stats(456)

        assert result.success is True
        assert result.data["total_endorsements_given"] == 10
        assert result.data["total_endorsements_active"] == 7

    def test_create_endorsement_reactivate_removed(self):
        """Test endorsement creation reactivating a previously removed endorsement."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(1,), (1, "2023-01-01")]  # statement exists, existing removed endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is True
        assert result.data == 1  # existing id

    def test_withdraw_endorsement_invalid_params(self):
        """Test withdrawal with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(0, 789)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_user_endorsements_success(self):
        """Test getting user endorsements."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 456, 789, "2023-01-01", None)],  # endorsements
            (1,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsements(456)

        assert result.success is True
        assert len(result.data["endorsements"]) == 1
        assert result.data["total_count"] == 1

    def test_get_user_endorsements_pagination(self):
        """Test getting user endorsements with pagination."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 456, 789, "2023-01-01", None), (2, 456, 790, "2023-01-02", None)],  # endorsements
            (5,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsements(456, limit=2, offset=1)

        assert result.success is True
        assert len(result.data["endorsements"]) == 2
        assert result.data["total_count"] == 5
        assert result.data["has_more"] is True

    def test_get_user_endorsements_include_removed(self):
        """Test getting user endorsements including removed ones."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 456, 789, "2023-01-01", "2023-01-02")],  # removed endorsement
            (1,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsements(456, include_removed=True)

        assert result.success is True
        assert len(result.data["endorsements"]) == 1
        assert result.data["endorsements"][0].removed_at == "2023-01-02"

    def test_get_user_endorsements_invalid_params(self):
        """Test getting user endorsements with invalid params."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsements(0)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_batch_statement_endorsement_stats_success(self):
        """Test getting batch statement endorsement stats."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (789, 5, 3, 2),  # statement_hash, total, active, withdrawn
            (790, 2, 2, 0)
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([789, 790])

        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["statement_hash"] == 789
        assert result.data[0]["total_endorsements"] == 5

    def test_get_batch_statement_endorsement_stats_empty(self):
        """Test getting batch stats with no endorsements."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([789, 790])

        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["total_endorsements"] == 0

    def test_get_batch_statement_endorsement_stats_invalid_params(self):
        """Test batch stats with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([])

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_revision_thanks_invalid_params(self):
        """Test getting revision thanks with invalid params."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision_thanks("", 1)

        assert result.success is False
        assert "Invalid parameters" in result.error
