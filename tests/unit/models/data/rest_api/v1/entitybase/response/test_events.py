"""Unit tests for events response models."""

import pytest

from models.data.rest_api.v1.entitybase.response.events import RDFChangeEvent


class TestRDFChangeEvent:
    """Unit tests for RDFChangeEvent model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        event = RDFChangeEvent(
            meta={"id": "123"},
            entity_id="Q42",
            revision_id=100,
            triple_count_diff=5,
            title="Q42",
            user="ExampleUser",
            timestamp=1704067200,
            server_name="www.example.com",
            server_url="https://www.example.com",
            wiki="examplewiki",
        )
        assert event.entity_id == "Q42"
        assert event.revision_id == 100
        assert event.triple_count_diff == 5

    def test_with_optional_fields(self):
        """Test with optional fields."""
        event = RDFChangeEvent(
            meta={"id": "456"},
            entity_id="P31",
            revision_id=50,
            triple_count_diff=2,
            title="Property:P31",
            user="BotUser",
            timestamp=1704067200,
            comment="Added statement",
            bot=True,
            server_name="www.example.com",
            server_url="https://www.example.com",
            wiki="examplewiki",
        )
        assert event.comment == "Added statement"
        assert event.bot is True

    def test_default_values(self):
        """Test default values."""
        event = RDFChangeEvent(
            meta={"id": "789"},
            entity_id="Q100",
            revision_id=1,
            triple_count_diff=10,
            title="Q100",
            user="User",
            timestamp=1704067200,
            server_name="www.example.com",
            server_url="https://www.example.com",
            wiki="examplewiki",
        )
        assert event.from_revision_id == 0
        assert event.bot is False
        assert event.minor is False
        assert event.comment == ""

    def test_model_dump(self):
        """Test model_dump()."""
        event = RDFChangeEvent(
            meta={"id": "123"},
            entity_id="Q42",
            revision_id=100,
            triple_count_diff=5,
            title="Q42",
            user="User",
            timestamp=1704067200,
            server_name="www.example.com",
            server_url="https://www.example.com",
            wiki="examplewiki",
        )
        dumped = event.model_dump()
        assert "entity_id" in dumped
        assert dumped["entity_id"] == "Q42"
