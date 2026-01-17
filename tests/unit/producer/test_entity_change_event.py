import sys
from datetime import datetime, timezone

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import EntityChangeEvent


class TestEntityChangeEvent:
    """Tests for EntityChangeEvent model validation and serialization"""

    @pytest.fixture
    def sample_event_data(self) -> dict:
        """Sample event data for testing"""
        return {
            "entity_id": "Q888888",
            "revision_id": 101,
            "change_type": ChangeType.CREATION,
            "from_revision_id": None,
            "changed_at": datetime(2026, 1, 8, 20, 0, 0, tzinfo=timezone.utc),
            "edit_summary": "Test entity creation",
        }

    def test_entity_change_event_creation(self, sample_event_data: dict) -> None:
        """Test creating valid change event"""
        event = EntityChangeEvent(**sample_event_data)
        assert event.entity_id == "Q888888"
        assert event.revision_id == 101
        assert event.change_type == ChangeType.CREATION
        assert event.from_revision_id is None
        assert event.edit_summary == "Test entity creation"

    def test_entity_change_event_defaults(self) -> None:
        """Test default values for optional fields"""
        event = EntityChangeEvent(
            entity_id="Q888888",
            revision_id=101,
            change_type=ChangeType.EDIT,
            changed_at=datetime(2026, 1, 8, 20, 0, 0, tzinfo=timezone.utc),
        )
        assert event.from_revision_id is None
        assert event.edit_summary is None

    def test_entity_change_event_model_dump(self, sample_event_data: dict) -> None:
        """Test model_dump returns correct dictionary"""
        event = EntityChangeEvent(**sample_event_data)
        data = event.model_dump(by_alias=True)
        assert data["id"] == "Q888888"
        assert data["rev"] == 101
        assert data["type"] == "creation"
        assert data["from_rev"] is None

    def test_entity_change_event_json_serialization(
        self, sample_event_data: dict
    ) -> None:
        """Test JSON serialization with datetime encoding"""
        event = EntityChangeEvent(**sample_event_data)
        json_str = event.model_dump_json()
        assert "Q888888" in json_str
        assert "101" in json_str
        assert "creation" in json_str

    def test_entity_change_event_with_edit_type(self) -> None:
        """Test event with EDIT change type"""
        event = EntityChangeEvent(
            entity_id="Q888888",
            revision_id=102,
            change_type=ChangeType.EDIT,
            from_revision_id=101,
            changed_at=datetime(2026, 1, 8, 20, 30, 0, tzinfo=timezone.utc),
        )
        assert event.change_type == ChangeType.EDIT
        assert event.from_revision_id == 101

    def test_entity_change_event_with_all_deletion_types(self) -> None:
        """Test events with soft_delete and hard_delete types"""
        soft_delete_event = EntityChangeEvent(
            entity_id="Q888888",
            revision_id=103,
            change_type=ChangeType.SOFT_DELETE,
            from_revision_id=102,
            changed_at=datetime(2026, 1, 8, 21, 0, 0, tzinfo=timezone.utc),
        )
        assert soft_delete_event.change_type == ChangeType.SOFT_DELETE

        hard_delete_event = EntityChangeEvent(
            entity_id="Q888888",
            revision_id=104,
            change_type=ChangeType.HARD_DELETE,
            from_revision_id=103,
            changed_at=datetime(2026, 1, 8, 21, 30, 0, tzinfo=timezone.utc),
        )
        assert hard_delete_event.change_type == ChangeType.HARD_DELETE

    def test_entity_change_event_with_redirect_types(self) -> None:
        """Test events with redirect and unredirect types"""
        redirect_event = EntityChangeEvent(
            entity_id="Q888889",
            revision_id=2,
            change_type=ChangeType.REDIRECT,
            from_revision_id=1,
            changed_at=datetime(2026, 1, 8, 22, 0, 0, tzinfo=timezone.utc),
        )
        assert redirect_event.change_type == ChangeType.REDIRECT

        unredirect_event = EntityChangeEvent(
            entity_id="Q888889",
            revision_id=3,
            change_type=ChangeType.UNREDIRECT,
            from_revision_id=2,
            changed_at=datetime(2026, 1, 8, 22, 30, 0, tzinfo=timezone.utc),
        )
        assert unredirect_event.change_type == ChangeType.UNREDIRECT

    def test_entity_change_event_with_protection_types(self) -> None:
        """Test events with lock/unlock and archival types"""
        lock_event = EntityChangeEvent(
            entity_id="Q888890",
            revision_id=5,
            change_type=ChangeType.LOCK,
            from_revision_id=4,
            changed_at=datetime(2026, 1, 8, 23, 0, 0, tzinfo=timezone.utc),
        )
        assert lock_event.change_type == ChangeType.LOCK

        unlock_event = EntityChangeEvent(
            entity_id="Q888890",
            revision_id=6,
            change_type=ChangeType.UNLOCK,
            from_revision_id=5,
            changed_at=datetime(2026, 1, 8, 23, 30, 0, tzinfo=timezone.utc),
        )
        assert unlock_event.change_type == ChangeType.UNLOCK

        archival_event = EntityChangeEvent(
            entity_id="Q888890",
            revision_id=7,
            change_type=ChangeType.ARCHIVAL,
            from_revision_id=6,
            changed_at=datetime(2026, 1, 9, 0, 0, 0, tzinfo=timezone.utc),
        )
        assert archival_event.change_type == ChangeType.ARCHIVAL

        unarchival_event = EntityChangeEvent(
            entity_id="Q888890",
            revision_id=8,
            change_type=ChangeType.UNARCHIVAL,
            from_revision_id=7,
            changed_at=datetime(2026, 1, 9, 0, 30, 0, tzinfo=timezone.utc),
        )
        assert unarchival_event.change_type == ChangeType.UNARCHIVAL
