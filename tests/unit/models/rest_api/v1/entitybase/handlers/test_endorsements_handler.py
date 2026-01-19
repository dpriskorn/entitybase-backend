"""Unit tests for endorsement handlers."""

import pytest
from unittest.mock import Mock

from models.rest_api.entitybase.request.endorsements import EndorsementListRequest
from models.rest_api.entitybase.response.endorsements import (
    EndorsementListResponse,
    EndorsementResponse,
    EndorsementStatsResponse,
    SingleEndorsementStatsResponse,
    StatementEndorsementStats,
)
from models.rest_api.entitybase.handlers.endorsements import EndorsementHandler


class TestEndorsementHandler:
    @pytest.fixture
    def mock_vitess_client(self):
        """Mock VitessClient with endorsement repository."""
        mock_client = Mock()
        mock_client.user_repository.user_exists.return_value = True
        mock_client.endorsement_repository.create_endorsement.return_value = Mock(
            success=True, data=123
        )
        mock_client.endorsement_repository.withdraw_endorsement.return_value = Mock(
            success=True, data=123
        )
        mock_client.endorsement_repository.get_batch_statement_endorsement_stats.return_value = Mock(
            success=True,
            data=[
                {
                    "statement_hash": 456789,
                    "total_endorsements": 10,
                    "active_endorsements": 8,
                    "withdrawn_endorsements": 2,
                }
            ],
        )
        mock_client.endorsement_repository.get_statement_endorsements.return_value = (
            Mock(
                success=True,
                data={
                    "endorsements": [
                        EndorsementResponse(
                            id=1,
                            user_id=123,
                            hash=456789,
                            created_at="2023-01-01T00:00:00Z",
                            removed_at="",
                        )
                    ],
                    "total_count": 1,
                    "has_more": False,
                },
            )
        )
        mock_client.endorsement_repository.get_user_endorsements.return_value = Mock(
            success=True,
            data={
                "endorsements": [
                    EndorsementResponse(
                        id=1,
                        user_id=123,
                        hash=456789,
                        created_at="2023-01-01T00:00:00Z",
                        removed_at="",
                    )
                ],
                "total_count": 1,
                "has_more": False,
            },
        )
        return mock_client

    @pytest.fixture
    def handler(self):
        return EndorsementHandler()

    def test_endorse_statement_success(self, handler, mock_vitess_client):
        """Test successful statement endorsement."""
        result = handler.endorse_statement(456789, 123, mock_vitess_client)

        assert isinstance(result, EndorsementResponse)
        assert result.endorsement_id == 123
        assert result.user_id == 123
        assert result.statement_hash == 456789

    def test_endorse_statement_user_not_found(self, handler, mock_vitess_client):
        """Test endorsement with non-existent user."""
        mock_vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(Exception):  # Should raise validation error
            handler.endorse_statement(456789, 123, mock_vitess_client)

    def test_endorse_statement_repository_error(self, handler, mock_vitess_client):
        """Test endorsement with repository error."""
        mock_vitess_client.endorsement_repository.create_endorsement.return_value = (
            Mock(success=False, error="Database error")
        )

        with pytest.raises(Exception):  # Should raise validation error
            handler.endorse_statement(456789, 123, mock_vitess_client)

    def test_withdraw_endorsement_success(self, handler, mock_vitess_client):
        """Test successful endorsement withdrawal."""
        result = handler.withdraw_endorsement(456789, 123, mock_vitess_client)

        assert isinstance(result, EndorsementResponse)
        assert result.endorsement_id == 123

    def test_withdraw_endorsement_repository_error(self, handler, mock_vitess_client):
        """Test withdrawal with repository error."""
        mock_vitess_client.endorsement_repository.withdraw_endorsement.return_value = (
            Mock(success=False, error="No active endorsement")
        )

        with pytest.raises(Exception):  # Should raise validation error
            handler.withdraw_endorsement(456789, 123, mock_vitess_client)

    def test_get_statement_endorsements_success(self, handler, mock_vitess_client):
        """Test successful statement endorsements retrieval."""
        request = EndorsementListRequest(limit=50, offset=0, include_removed=False)

        result = handler.get_statement_endorsements(456789, request, mock_vitess_client)

        assert isinstance(result, EndorsementListResponse)
        assert result.statement_hash == 456789
        assert len(result.endorsements) == 1
        assert result.total_count == 1
        assert not result.has_more
        assert isinstance(result.stats, StatementEndorsementStats)

    def test_get_statement_endorsements_repository_error(
        self, handler, mock_vitess_client
    ):
        """Test statement endorsements with repository error."""
        mock_vitess_client.endorsement_repository.get_statement_endorsements.return_value = Mock(
            success=False, error="Database error"
        )

        request = EndorsementListRequest()

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_statement_endorsements(456789, request, mock_vitess_client)

    def test_get_user_endorsements_success(self, handler, mock_vitess_client):
        """Test successful user endorsements retrieval."""
        request = EndorsementListRequest(limit=50, offset=0, include_removed=False)

        result = handler.get_user_endorsements(123, request, mock_vitess_client)

        assert isinstance(result, EndorsementListResponse)
        assert result.user_id == 123
        assert len(result.endorsements) == 1
        assert result.total_count == 1
        assert not result.has_more
        assert isinstance(result.stats, StatementEndorsementStats)

    def test_get_user_endorsements_user_not_found(self, handler, mock_vitess_client):
        """Test user endorsements with non-existent user."""
        mock_vitess_client.user_repository.user_exists.return_value = False

        request = EndorsementListRequest()

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_user_endorsements(123, request, mock_vitess_client)

    def test_get_batch_statement_endorsement_stats_success(
        self, handler, mock_vitess_client
    ):
        """Test successful batch statement endorsement stats."""
        result = handler.get_batch_statement_endorsement_stats(
            [456789], mock_vitess_client
        )

        assert len(result.stats) == 1
        assert result.stats[0].statement_hash == 456789
        assert result.stats[0].total_endorsements == 10
        assert result.stats[0].active_endorsements == 8
        assert result.stats[0].withdrawn_endorsements == 2

    def test_get_batch_statement_endorsement_stats_invalid_hash(
        self, handler, mock_vitess_client
    ):
        """Test batch stats with invalid statement hash."""
        with pytest.raises(Exception):  # Should raise validation error
            handler.get_batch_statement_endorsement_stats([0], mock_vitess_client)

    def test_get_batch_statement_endorsement_stats_repository_error(
        self, handler, mock_vitess_client
    ):
        """Test batch stats with repository error."""
        mock_vitess_client.endorsement_repository.get_batch_statement_endorsement_stats.return_value = Mock(
            success=False, error="Database error"
        )

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_batch_statement_endorsement_stats([456789], mock_vitess_client)
