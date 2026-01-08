import asyncio
import logging
from typing import Any

import pytest
from aiokafka import AIOKafkaConsumer


logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "redpanda:9092"
KAFKA_TOPIC = "wikibase.entity_change"
TEST_ENTITY_BASE = "Q888888"


class TestStreamIntegration:
    """Integration tests for stream producer with real Redpanda"""

    @pytest.mark.asyncio
    async def test_entity_creation_publishes_creation_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that creating an entity publishes a CREATION event"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}0",
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Stream Test Entity Creation"}
            },
            "descriptions": {
                "en": {"language": "en", "value": "Test entity for stream integration"}
            },
        }

        response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert response.status_code == 200

        result = response.json()
        assert result["id"] == f"{TEST_ENTITY_BASE}0"
        assert result["revision_id"] == 1

        await asyncio.sleep(5)  # Allow time for message propagation

        msg = await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)
        event = msg.value

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}0"
        assert event["change_type"] == "creation"
        assert event["revision_id"] == 1
        assert event["from_revision_id"] is None
        assert "changed_at" in event
        assert event["bot"] is False

    @pytest.mark.asyncio
    async def test_entity_update_publishes_edit_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that updating an entity publishes an EDIT event with from_revision_id"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}1",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Entity for Edit Test"}},
        }

        create_response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert create_response.status_code == 200
        create_result = create_response.json()
        assert create_result["revision_id"] == 1

        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        update_data = {
            "id": f"{TEST_ENTITY_BASE}1",
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Updated Entity for Edit Test"},
                "de": {"language": "de", "value": "Test-Entität für Bearbeitung"},
            },
        }

        update_response = api_client.post(f"{base_url}/entity", json=update_data)
        assert update_response.status_code == 200
        update_result = update_response.json()
        assert update_result["revision_id"] == 2

        msg = await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)
        event = msg.value

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}1"
        assert event["change_type"] == "edit"
        assert event["revision_id"] == 2
        assert event["from_revision_id"] == 1
        assert "changed_at" in event

    @pytest.mark.asyncio
    async def test_entity_soft_delete_publishes_soft_delete_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that soft deleting an entity publishes a SOFT_DELETE event"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}2",
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Entity for Soft Delete Test"}
            },
        }

        create_response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert create_response.status_code == 200

        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        delete_response = api_client.delete(
            f"{base_url}/entity/{TEST_ENTITY_BASE}2",
            json={
                "delete_type": "soft",
                "deletion_reason": "Testing stream integration",
                "deleted_by": "test-integration",
            },
        )
        assert delete_response.status_code == 200

        msg = await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)
        event = msg.value

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}2"
        assert event["change_type"] == "soft_delete"
        assert "revision_id" in event
        assert event["from_revision_id"] == 1

    @pytest.mark.asyncio
    async def test_redirect_creation_publishes_redirect_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that creating a redirect publishes a REDIRECT event"""
        source_entity = {
            "id": f"{TEST_ENTITY_BASE}3",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Redirect Source Entity"}},
        }

        target_entity = {
            "id": f"{TEST_ENTITY_BASE}4",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Redirect Target Entity"}},
        }

        create_source = api_client.post(f"{base_url}/entity", json=source_entity)
        assert create_source.status_code == 200
        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        create_target = api_client.post(f"{base_url}/entity", json=target_entity)
        assert create_target.status_code == 200
        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        redirect_response = api_client.post(
            f"{base_url}/redirects",
            json={
                "redirect_from_id": f"{TEST_ENTITY_BASE}3",
                "redirect_to_id": f"{TEST_ENTITY_BASE}4",
                "created_by": "test-integration",
            },
        )
        assert redirect_response.status_code == 200

        msg = await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)
        event = msg.value

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}3"
        assert event["change_type"] == "redirect"
        assert "revision_id" in event
        assert "from_revision_id" in event

    @pytest.mark.asyncio
    async def test_redirect_reversion_publishes_unredirect_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that reverting a redirect publishes an UNREDIRECT event"""
        source_entity = {
            "id": f"{TEST_ENTITY_BASE}5",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Unredirect Source Entity"}},
        }

        target_entity = {
            "id": f"{TEST_ENTITY_BASE}6",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Unredirect Target Entity"}},
        }

        create_source = api_client.post(f"{base_url}/entity", json=source_entity)
        assert create_source.status_code == 200
        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        create_target = api_client.post(f"{base_url}/entity", json=target_entity)
        assert create_target.status_code == 200
        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        redirect_response = api_client.post(
            f"{base_url}/redirects",
            json={
                "redirect_from_id": f"{TEST_ENTITY_BASE}5",
                "redirect_to_id": f"{TEST_ENTITY_BASE}6",
                "created_by": "test-integration",
            },
        )
        assert redirect_response.status_code == 200
        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        revert_response = api_client.post(
            f"{base_url}/entities/{TEST_ENTITY_BASE}5/revert-redirect",
            json={
                "revert_to_revision_id": 1,
                "revert_reason": "Testing unredirect event",
            },
        )
        assert revert_response.status_code == 200

        msg = await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)
        event = msg.value

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}5"
        assert event["change_type"] == "unredirect"
        assert "revision_id" in event
        assert "from_revision_id" in event

    @pytest.mark.asyncio
    async def test_event_schema_validation(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that all published events have the correct schema"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}7",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Schema Validation Test"}},
            "descriptions": {"en": {"language": "en", "value": "Testing event schema"}},
            "aliases": {"en": [{"language": "en", "value": "Test Alias"}]},
        }

        response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert response.status_code == 200

        msg = await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)
        event = msg.value

        required_fields = ["entity_id", "revision_id", "change_type", "changed_at"]
        for field in required_fields:
            assert field in event, f"Event missing required field: {field}"

        assert isinstance(event["entity_id"], str)
        assert event["entity_id"].startswith("Q")
        assert isinstance(event["revision_id"], int)
        assert event["revision_id"] >= 1
        assert isinstance(event["change_type"], str)
        assert isinstance(event["changed_at"], str)

    @pytest.mark.asyncio
    async def test_multiple_entity_operations_publish_multiple_events(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that multiple entity operations publish multiple events"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}8",
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Multi Operation Test Entity"}
            },
        }

        create_response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert create_response.status_code == 200

        await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)

        update_data = {
            "id": f"{TEST_ENTITY_BASE}8",
            "type": "item",
            "labels": {
                "en": {
                    "language": "en",
                    "value": "Updated Multi Operation Test Entity",
                },
                "fr": {"language": "fr", "value": "Entité de test multi-opérations"},
            },
        }

        update_response = api_client.post(f"{base_url}/entity", json=update_data)
        assert update_response.status_code == 200

        update2_response = api_client.post(f"{base_url}/entity", json=update_data)
        assert update2_response.status_code == 200

        events = []
        for _ in range(3):
            msg = await asyncio.wait_for(clean_consumer.getone(), timeout=30.0)
            events.append(msg.value)

        change_types = [e["change_type"] for e in events]
        assert change_types[0] == "creation"
        assert change_types[1] == "edit"
        assert change_types[2] == "edit"

        revision_ids = [e["revision_id"] for e in events]
        assert revision_ids == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_bot_edit_publishes_event_with_bot_true(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that bot edits publish events with bot=True"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}9",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Bot Edit Test Entity"}},
            "bot": True,
            "editor": "admin-bot",
        }

        response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert response.status_code == 200

        msg = await asyncio.wait_for(clean_consumer.getone(), timeout=10.0)
        event = msg.value

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}9"
        assert event["bot"] is True
        assert event["editor"] == "admin-bot"
