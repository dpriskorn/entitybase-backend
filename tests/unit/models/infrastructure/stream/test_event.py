"""Unit tests for event."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from models.data.infrastructure.stream.actions import EndorseAction
from models.data.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import (
    EndorseChangeEvent,
    EntityChangeEvent,
    NewThankEvent,
    UserChangeEvent,
)


class TestUserChangeEvent:
    """Unit tests for UserChangeEvent."""

    def test_user_change_event_creation(self) -> None:
        """Test UserChangeEvent can be created with valid data."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = UserChangeEvent(
            user="user123",
            type=ChangeType.EDIT,
            timestamp=ts,
        )

        assert event.user_id == "user123"
        assert event.change_type == ChangeType.EDIT
        assert event.timestamp == ts

    def test_user_change_event_serialization(self) -> None:
        """Test UserChangeEvent serializes timestamp to ISO format with Z."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = UserChangeEvent(
            user="user123",
            type=ChangeType.EDIT,
            timestamp=ts,
        )

        data = event.model_dump(by_alias=True)
        assert data["ts"] == "2024-01-01T12:00:00Z"


class TestEndorseChangeEvent:
    """Unit tests for EndorseChangeEvent."""

    def test_endorse_change_event_creation(self) -> None:
        """Test EndorseChangeEvent can be created with valid data."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = EndorseChangeEvent(
            hash="abc123",
            user="user456",
            action=EndorseAction.ENDORSE,
            timestamp=ts,
        )

        assert event.statement_hash == "abc123"
        assert event.user_id == "user456"
        assert event.action == EndorseAction.ENDORSE
        assert event.timestamp == ts

    def test_endorse_change_event_serialization(self) -> None:
        """Test EndorseChangeEvent serializes timestamp to ISO format with Z."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = EndorseChangeEvent(
            hash="abc123",
            user="user456",
            action=EndorseAction.ENDORSE,
            timestamp=ts,
        )

        data = event.model_dump(by_alias=True)
        assert data["ts"] == "2024-01-01T12:00:00Z"


class TestNewThankEvent:
    """Unit tests for NewThankEvent."""

    def test_new_thank_event_creation(self) -> None:
        """Test NewThankEvent can be created with valid data."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = NewThankEvent(
            from_user_id="user1",
            to_user_id="user2",
            entity_id="Q123",
            revision_id=1,
            timestamp=ts,
        )

        assert event.from_user_id == "user1"
        assert event.to_user_id == "user2"
        assert event.entity_id == "Q123"
        assert event.revision_id == 1
        assert event.timestamp == ts

    def test_new_thank_event_serialization(self) -> None:
        """Test NewThankEvent serializes timestamp to ISO format with Z."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = NewThankEvent(
            from_user_id="user1",
            to_user_id="user2",
            entity_id="Q123",
            revision_id=1,
            timestamp=ts,
        )

        data = event.model_dump(by_alias=True)
        assert data["ts"] == "2024-01-01T12:00:00Z"


class TestEntityChangeEvent:
    """Unit tests for EntityChangeEvent."""

    def test_entity_change_event_creation(self) -> None:
        """Test EntityChangeEvent can be created with valid data."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = EntityChangeEvent(
            id="Q123",
            rev=1,
            type=ChangeType.EDIT,
            at=ts,
            user="user1",
        )

        assert event.entity_id == "Q123"
        assert event.revision_id == 1
        assert event.change_type == ChangeType.EDIT
        assert event.changed_at == ts
        assert event.user_id == "user1"

    def test_entity_change_event_with_from_revision(self) -> None:
        """Test EntityChangeEvent can include from_revision_id."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = EntityChangeEvent(
            id="Q123",
            rev=2,
            type=ChangeType.EDIT,
            from_rev=1,
            at=ts,
            user="user1",
        )

        assert event.entity_id == "Q123"
        assert event.revision_id == 2
        assert event.from_revision_id == 1

    def test_entity_change_event_serialization(self) -> None:
        """Test EntityChangeEvent serializes timestamp to ISO format with Z."""
        ts = datetime(2024, 1, 1, 12, 0, 0)
        event = EntityChangeEvent(
            id="Q123",
            rev=1,
            type=ChangeType.EDIT,
            at=ts,
            user="user1",
            summary="Test edit",
        )

        data = event.model_dump(by_alias=True)
        assert data["at"] == "2024-01-01T12:00:00Z"
        assert data["summary"] == "Test edit"
