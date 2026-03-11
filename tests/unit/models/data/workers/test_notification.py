"""Unit tests for ChangedProperties and NotificationData models."""

import pytest

from models.data.workers.changed_properties import ChangedProperties
from models.data.workers.notification import NotificationData


class TestChangedProperties:
    """Unit tests for ChangedProperties model."""

    def test_empty_properties(self):
        """Test default empty properties list."""
        changed = ChangedProperties()
        assert changed.properties == []

    def test_with_properties(self):
        """Test with properties list."""
        changed = ChangedProperties(properties=["P31", "P569"])
        assert changed.properties == ["P31", "P569"]

    def test_model_dump(self):
        """Test model_dump()."""
        changed = ChangedProperties(properties=["P31"])
        dumped = changed.model_dump()
        assert dumped == {"properties": ["P31"]}

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        changed = ChangedProperties(properties=["P31", "P569"])
        json_str = changed.model_dump_json()
        assert "P31" in json_str
        assert "P569" in json_str


class TestNotificationData:
    """Unit tests for NotificationData model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        notification = NotificationData(
            entity_id="Q1",
            revision_id=123,
            change_type="create",
        )
        assert notification.entity_id == "Q1"
        assert notification.revision_id == 123
        assert notification.change_type == "create"

    def test_with_changed_properties(self):
        """Test with changed properties."""
        changed = ChangedProperties(properties=["P31", "P569"])
        notification = NotificationData(
            entity_id="Q1",
            revision_id=123,
            change_type="update",
            changed_properties=changed,
        )
        assert notification.changed_properties == changed

    def test_with_event_timestamp(self):
        """Test with event timestamp."""
        notification = NotificationData(
            entity_id="Q1",
            revision_id=123,
            change_type="create",
            event_timestamp="2024-01-01T00:00:00Z",
        )
        assert notification.event_timestamp == "2024-01-01T00:00:00Z"

    def test_default_timestamp(self):
        """Test default empty timestamp."""
        notification = NotificationData(
            entity_id="Q1",
            revision_id=123,
            change_type="create",
        )
        assert notification.event_timestamp == ""

    def test_model_dump(self):
        """Test model_dump()."""
        notification = NotificationData(
            entity_id="Q1",
            revision_id=123,
            change_type="update",
            event_timestamp="2024-01-01T00:00:00Z",
        )
        dumped = notification.model_dump()
        assert dumped["entity_id"] == "Q1"
        assert dumped["revision_id"] == 123
        assert dumped["change_type"] == "update"
        assert dumped["event_timestamp"] == "2024-01-01T00:00:00Z"

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        notification = NotificationData(
            entity_id="Q1",
            revision_id=123,
            change_type="create",
        )
        json_str = notification.model_dump_json()
        assert "Q1" in json_str
        assert "123" in json_str
        assert "create" in json_str
