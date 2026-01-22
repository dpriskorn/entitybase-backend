"""Unit tests for event."""

from datetime import datetime, timezone

from models.data.infrastructure.stream.actions import EndorseAction
from models.data.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import (
    EndorseChangeEvent,
    NewThankEvent,
    EntityChangeEvent,
)


class TestEndorseChangeEvent:
    """Unit tests for EndorseChangeEvent."""

    def test_endorse_change_event_creation(self):
        """Test creating an EndorseChangeEvent."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = EndorseChangeEvent(
            statement_hash="abc123",
            user_id="user456",
            action=EndorseAction.ENDORSE,
            timestamp=timestamp,
        )

        assert event.statement_hash == "abc123"
        assert event.user_id == "user456"
        assert event.action == EndorseAction.ENDORSE
        assert event.timestamp == timestamp

    def test_endorse_change_event_serialization(self):
        """Test JSON serialization with aliases and timestamp formatting."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = EndorseChangeEvent(
            statement_hash="abc123",
            user_id="user456",
            action=EndorseAction.ENDORSE,
            timestamp=timestamp,
        )

        json_data = event.model_dump_json(by_alias=True)
        assert '"hash":"abc123"' in json_data
        assert '"user":"user456"' in json_data
        assert '"act":"endorse"' in json_data
        assert '"ts":"2023-01-01T12:00:00+00:00Z"' in json_data

    def test_serialize_timestamp(self):
        """Test timestamp serialization method."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = EndorseChangeEvent(
            statement_hash="abc123",
            user_id="user456",
            action=EndorseAction.ENDORSE,
            timestamp=timestamp,
        )

        serialized = event.serialize_timestamp(timestamp)
        assert serialized == "2023-01-01T12:00:00+00:00Z"


class TestNewThankEvent:
    """Unit tests for NewThankEvent."""

    def test_new_thank_event_creation(self):
        """Test creating a NewThankEvent."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = NewThankEvent(
            from_user_id="user1",
            to_user_id="user2",
            entity_id="Q42",
            revision_id=123,
            timestamp=timestamp,
        )

        assert event.from_user_id == "user1"
        assert event.to_user_id == "user2"
        assert event.entity_id == "Q42"
        assert event.revision_id == 123
        assert event.timestamp == timestamp

    def test_new_thank_event_serialization(self):
        """Test JSON serialization with aliases."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = NewThankEvent(
            from_user_id="user1",
            to_user_id="user2",
            entity_id="Q42",
            revision_id=123,
            timestamp=timestamp,
        )

        json_data = event.model_dump_json(by_alias=True)
        assert '"from":"user1"' in json_data
        assert '"to":"user2"' in json_data
        assert '"id":"Q42"' in json_data
        assert '"rev":123' in json_data
        assert '"ts":"2023-01-01T12:00:00+00:00Z"' in json_data

    def test_serialize_timestamp(self):
        """Test timestamp serialization method."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = NewThankEvent(
            from_user_id="user1",
            to_user_id="user2",
            entity_id="Q42",
            revision_id=123,
            timestamp=timestamp,
        )

        serialized = event.serialize_timestamp(timestamp)
        assert serialized == "2023-01-01T12:00:00+00:00Z"


class TestEntityChangeEvent:
    """Unit tests for EntityChangeEvent."""

    def test_entity_change_event_creation(self):
        """Test creating an EntityChangeEvent."""
        changed_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.CREATE,
            from_revision_id=122,
            changed_at=changed_at,
            edit_summary="Test edit",
        )

        assert event.entity_id == "Q42"
        assert event.revision_id == 123
        assert event.change_type == ChangeType.CREATE
        assert event.from_revision_id == 122
        assert event.changed_at == changed_at
        assert event.edit_summary == "Test edit"

    def test_entity_change_event_minimal(self):
        """Test creating minimal EntityChangeEvent."""
        changed_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.UPDATE,
            changed_at=changed_at,
        )

        assert event.from_revision_id is None
        assert event.edit_summary == ""

    def test_entity_change_event_serialization(self):
        """Test JSON serialization with aliases."""
        changed_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.CREATE,
            from_revision_id=122,
            changed_at=changed_at,
            edit_summary="Test edit",
        )

        json_data = event.model_dump_json(by_alias=True)
        assert '"id":"Q42"' in json_data
        assert '"rev":123' in json_data
        assert '"type":"create"' in json_data
        assert '"from_rev":122' in json_data
        assert '"at":"2023-01-01T12:00:00+00:00Z"' in json_data
        assert '"summary":"Test edit"' in json_data

    def test_serialize_changed_at(self):
        """Test changed_at serialization method."""
        changed_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.UPDATE,
            changed_at=changed_at,
        )

        serialized = event.serialize_changed_at(changed_at)
        assert serialized == "2023-01-01T12:00:00+00:00Z"
