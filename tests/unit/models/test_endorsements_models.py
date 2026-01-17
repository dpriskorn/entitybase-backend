"""Unit tests for endorsement models."""

import pytest
from datetime import datetime, timezone

from models.endorsements import Endorsement
from models.rest_api.entitybase.request.endorsements import EndorsementListRequest
from models.rest_api.entitybase.response.endorsements import (
    EndorsementListResponse,
    EndorsementResponse,
    StatementEndorsementStats,
    SingleEndorsementStatsResponse,
)
from models.endorsements import Endorsement


class TestStatementEndorsementStats:
    def test_valid_stats(self):
        """Test creating valid StatementEndorsementStats."""
        stats = StatementEndorsementStats(
            total=50,
            active=42,
            withdrawn=8,
        )
        assert stats.total == 50
        assert stats.active == 42
        assert stats.withdrawn == 8

    def test_stats_serialization(self):
        """Test JSON serialization of StatementEndorsementStats."""
        stats = StatementEndorsementStats(
            total=50,
            active=42,
            withdrawn=8,
        )
        data = stats.model_dump()
        assert data["total"] == 50
        assert data["active"] == 42
        assert data["withdrawn"] == 8


class TestEndorsementListRequest:
    def test_valid_request(self):
        """Test creating a valid EndorsementListRequest."""
        request = EndorsementListRequest(limit=100, offset=10, include_removed=True)
        assert request.limit == 100
        assert request.offset == 10
        assert request.include_removed is True

    def test_default_values(self):
        """Test default values for EndorsementListRequest."""
        request = EndorsementListRequest()
        assert request.limit == 50
        assert request.offset == 0
        assert request.include_removed is False

    def test_validation_limits(self):
        """Test validation limits for EndorsementListRequest."""
        with pytest.raises(ValueError):
            EndorsementListRequest(limit=0)  # Below min

        with pytest.raises(ValueError):
            EndorsementListRequest(limit=600)  # Above max

        with pytest.raises(ValueError):
            EndorsementListRequest(offset=-1)  # Below min


class TestEndorsementResponse:
    def test_valid_response(self):
        """Test creating a valid EndorsementResponse."""
        response = EndorsementResponse(
            endorsement_id=1,
            user_id=123,
            statement_hash=456789,
            created_at="2023-01-01T00:00:00Z",
            removed_at=None,
        )
        assert response.endorsement_id == 1
        assert response.user_id == 123
        assert response.removed_at is None

    def test_response_with_removal(self):
        """Test EndorsementResponse with removal timestamp."""
        response = EndorsementResponse(
            endorsement_id=1,
            user_id=123,
            statement_hash=456789,
            created_at="2023-01-01T00:00:00Z",
            removed_at="2023-01-02T00:00:00Z",
        )
        assert response.removed_at == "2023-01-02T00:00:00Z"


class TestSingleEndorsementStatsResponse:
    def test_valid_response(self):
        """Test creating a valid SingleEndorsementStatsResponse."""
        response = SingleEndorsementStatsResponse(
            total=50,
            active=42,
            withdrawn=8,
        )
        assert response.total == 50
        assert response.active == 42
        assert response.withdrawn == 8

    def test_response_serialization(self):
        """Test JSON serialization of SingleEndorsementStatsResponse."""
        response = SingleEndorsementStatsResponse(
            total=50,
            active=42,
            withdrawn=8,
        )
        data = response.model_dump()
        assert data["total"] == 50
        assert data["active"] == 42
        assert data["withdrawn"] == 8


class TestEndorsementListResponse:
    def test_valid_response(self):
        """Test creating a valid EndorsementListResponse."""
        endorsements = [
            Endorsement(
                id=1,
                user_id=123,
                hash=456789,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                removed_at=None,
            )
        ]
        stats = StatementEndorsementStats(total=50, active=42, withdrawn=8)
        response = EndorsementListResponse(
            statement_hash=456789,
            endorsements=endorsements,
            total_count=1,
            has_more=False,
            stats=stats,
        )
        assert response.statement_hash == 456789
        assert len(response.endorsements) == 1
        assert response.total_count == 1
        assert not response.has_more
        assert response.stats.total == 50

    def test_response_without_statement_hash(self):
        """Test EndorsementListResponse for user listings (no statement_hash)."""
        endorsements = [
            Endorsement(
                id=1,
                user_id=123,
                hash=456789,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                removed_at=None,
            )
        ]
        response = EndorsementListResponse(
            user_id=123,
            endorsements=endorsements,
            total_count=1,
            has_more=False,
            stats=StatementEndorsementStats(total=10, active=8, withdrawn=2),
        )
        assert response.user_id == 123
        assert response.statement_hash is None