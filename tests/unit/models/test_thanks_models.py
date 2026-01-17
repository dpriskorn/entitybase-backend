"""Unit tests for thanks models."""

import pytest
from datetime import datetime, timezone

from models.thanks import ThankItem, Thank
from models.rest_api.entitybase.request.thanks import ThanksListRequest
from models.rest_api.entitybase.response.thanks import ThankResponse, ThanksListResponse


class TestThankItem:
    def test_valid_thank_item(self):
        """Test creating a valid ThankItem."""
        item = ThankItem(
            id=1,
            from_user_id=123,
            to_user_id=456,
            entity_id="Q42",
            revision_id=789,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        assert item.id == 1
        assert item.entity_id == "Q42"

    def test_thank_item_serialization(self):
        """Test JSON serialization of ThankItem."""
        item = ThankItem(
            id=1,
            from_user_id=123,
            to_user_id=456,
            entity_id="Q42",
            revision_id=789,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        data = item.model_dump()
        assert data["id"] == 1
        assert "created_at" in data


class TestThank:
    def test_valid_thank(self):
        """Test creating a valid Thank."""
        thank = Thank(
            id=1,
            from_user_id=123,
            to_user_id=456,
            entity_id="Q42",
            revision_id=789,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        assert thank.id == 1
        assert thank.to_user_id == 456

    def test_thank_serialization(self):
        """Test JSON serialization of Thank."""
        thank = Thank(
            id=1,
            from_user_id=123,
            to_user_id=456,
            entity_id="Q42",
            revision_id=789,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        data = thank.model_dump()
        assert data["entity_id"] == "Q42"


class TestThanksListRequest:
    def test_valid_request(self):
        """Test creating a valid ThanksListRequest."""
        request = ThanksListRequest(limit=100, offset=10, hours=48)
        assert request.limit == 100
        assert request.offset == 10
        assert request.hours == 48

    def test_default_values(self):
        """Test default values for ThanksListRequest."""
        request = ThanksListRequest()
        assert request.limit == 50
        assert request.offset == 0
        assert request.hours == 24

    def test_validation_limits(self):
        """Test validation limits for ThanksListRequest."""
        with pytest.raises(ValueError):
            ThanksListRequest(limit=0)  # Below min

        with pytest.raises(ValueError):
            ThanksListRequest(limit=600)  # Above max

        with pytest.raises(ValueError):
            ThanksListRequest(hours=0)  # Below min

        with pytest.raises(ValueError):
            ThanksListRequest(hours=800)  # Above max

        with pytest.raises(ValueError):
            ThanksListRequest(offset=-1)  # Below min


class TestThankResponse:
    def test_valid_response(self):
        """Test creating a valid ThankResponse."""
        response = ThankResponse(
            thank_id=1,
            from_user_id=123,
            to_user_id=456,
            entity_id="Q42",
            revision_id=789,
            created_at="2023-01-01T00:00:00Z",
        )
        assert response.thank_id == 1
        assert response.created_at == "2023-01-01T00:00:00Z"

    def test_response_serialization(self):
        """Test JSON serialization of ThankResponse."""
        response = ThankResponse(
            thank_id=1,
            from_user_id=123,
            to_user_id=456,
            entity_id="Q42",
            revision_id=789,
            created_at="2023-01-01T00:00:00Z",
        )
        data = response.model_dump()
        assert data["entity_id"] == "Q42"


class TestThanksListResponse:
    def test_valid_response(self):
        """Test creating a valid ThanksListResponse."""
        items = [
            ThankItem(
                id=1,
                from_user_id=123,
                to_user_id=456,
                entity_id="Q42",
                revision_id=789,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            )
        ]
        response = ThanksListResponse(
            user_id=123, thanks=items, total_count=1, has_more=False
        )
        assert response.user_id == 123
        assert len(response.thanks) == 1
        assert response.total_count == 1
        assert not response.has_more

    def test_response_serialization(self):
        """Test JSON serialization of ThanksListResponse."""
        items = [
            ThankItem(
                id=1,
                from_user_id=123,
                to_user_id=456,
                entity_id="Q42",
                revision_id=789,
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            )
        ]
        response = ThanksListResponse(
            user_id=123, thanks=items, total_count=1, has_more=False
        )
        data = response.model_dump()
        assert data["user_id"] == 123
        assert len(data["thanks"]) == 1
