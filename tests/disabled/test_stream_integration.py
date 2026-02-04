import asyncio
import logging
from typing import Any

import pytest
from aiokafka import AIOKafkaConsumer  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "redpanda:9092"
KAFKA_TOPIC = "wikibase.entity_change"
TEST_ENTITY_BASE = "Q888888"


class TestStreamIntegration:
    """Integration tests for stream producer with real Redpanda"""

    @staticmethod
    async def _consume_event(
            clean_consumer: AIOKafkaConsumer, expected_entity: str, expected_type: str, timeout: float = 30.0
    ) -> dict[str, Any]:
        """Consume messages until finding the expected event type for an entity."""
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if msg.value is None:
                    continue
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    return msg.value
            except asyncio.TimeoutError:
                continue
        raise TimeoutError(
            f"Expected {expected_type} message for {expected_entity} not received within timeout"
        )

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

        # Consume messages until finding the expected creation event
        expected_entity = f"{TEST_ENTITY_BASE}0"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        event = None
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    event = msg.value
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError("Expected creation message not received within timeout")

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}0"
        assert event["change_type"] == "creation"
        assert event["revision_id"] == 1
        assert event["from_revision_id"] is None
        assert "changed_at" in event

    @pytest.mark.asyncio
    async def test_entity_update_publishes_edit_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that updating an entity publishes an EDIT event with from_revision_id"""
        entity = f"{TEST_ENTITY_BASE}1"
        entity_data = {
            "id": entity,
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Entity for Edit Test"}},
        }

        create_response = api_client.post(f"{base_url}/entity", json=entity_data)
        logger.debug(f"{entity} creation response code:")
        assert create_response.status_code == 200

        # Consume creation event
        expected_entity = f"{TEST_ENTITY_BASE}1"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

        delete_response = api_client.delete(
            f"{base_url}/entity/{TEST_ENTITY_BASE}1",
            json={
                "delete_type": "soft",
                "deletion_reason": "Testing stream integration",
                "deleted_by": "test-integration",
            },
        )
        logger.debug(f"{entity} deletion response code:")
        assert delete_response.status_code == 200

        # Consume soft_delete event
        expected_entity = f"{TEST_ENTITY_BASE}1"
        expected_type = "soft_delete"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    event = msg.value
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}1"
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
        # Consume creation event for source
        expected_entity = f"{TEST_ENTITY_BASE}3"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

        create_target = api_client.post(f"{base_url}/entity", json=target_entity)
        assert create_target.status_code == 200
        # Consume creation event for target
        expected_entity = f"{TEST_ENTITY_BASE}4"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

        redirect_response = api_client.post(
            f"{base_url}/redirects",
            json={
                "redirect_from_id": f"{TEST_ENTITY_BASE}3",
                "redirect_to_id": f"{TEST_ENTITY_BASE}4",
                "created_by": "test-integration",
            },
        )
        assert redirect_response.status_code == 200

        # Consume redirect event
        expected_entity = f"{TEST_ENTITY_BASE}3"
        expected_type = "redirect"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    event = msg.value
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

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
        await self._consume_event(clean_consumer, f"{TEST_ENTITY_BASE}5", "creation")

        create_target = api_client.post(f"{base_url}/entity", json=target_entity)
        assert create_target.status_code == 200
        await self._consume_event(clean_consumer, f"{TEST_ENTITY_BASE}6", "creation")

        redirect_response = api_client.post(
            f"{base_url}/redirects",
            json={
                "redirect_from_id": f"{TEST_ENTITY_BASE}5",
                "redirect_to_id": f"{TEST_ENTITY_BASE}6",
                "created_by": "test-integration",
            },
        )
        assert redirect_response.status_code == 200
        await self._consume_event(clean_consumer, f"{TEST_ENTITY_BASE}5", "redirect")

        revert_response = api_client.post(
            f"{base_url}/entities/{TEST_ENTITY_BASE}5/revert-redirect",
            json={
                "revert_to_revision_id": 1,
                "revert_reason": "Testing unredirect event",
            },
        )
        assert revert_response.status_code == 200

        event = await self._consume_event(clean_consumer, f"{TEST_ENTITY_BASE}5", "unredirect")
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

        # Consume creation event
        expected_entity = f"{TEST_ENTITY_BASE}7"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    event = msg.value
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

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

        # Consume creation event
        expected_entity = f"{TEST_ENTITY_BASE}8"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

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

        update2_data = {
            "id": f"{TEST_ENTITY_BASE}8",
            "type": "item",
            "labels": {
                "en": {
                    "language": "en",
                    "value": "Updated Multi Operation Test Entity",
                },
                "fr": {
                    "language": "fr",
                    "value": "Entité de test multi-opérations modifiée",
                },
            },
        }

        update2_response = api_client.post(f"{base_url}/entity", json=update2_data)
        assert update2_response.status_code == 200

        # Collect 2 edit events for the entity (creation already consumed above)
        expected_entity = f"{TEST_ENTITY_BASE}8"
        events: list[Any] = []
        start_time = asyncio.get_event_loop().time()
        while len(events) < 2 and asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if msg.value["entity_id"] == expected_entity:
                    events.append(msg.value)
            except asyncio.TimeoutError:
                continue
        if len(events) < 2:
            raise TimeoutError(
                f"Expected 2 edit events for {expected_entity}, got {len(events)}"
            )

        change_types = [e["change_type"] for e in events]
        assert change_types == ["edit", "edit"]

        revision_ids = [e["revision_id"] for e in events]
        assert revision_ids == [2, 3]

    @pytest.mark.asyncio
    async def test_entity_update_deduplication_no_duplicate_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that updating an entity with identical content doesn't publish duplicate events"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}9",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Deduplication Test Entity"}},
        }

        create_response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert create_response.status_code == 200
        create_result = create_response.json()
        assert create_result["revision_id"] == 1

        # Consume creation event
        expected_entity = f"{TEST_ENTITY_BASE}9"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

        update_data = {
            "id": f"{TEST_ENTITY_BASE}9",
            "type": "item",
            "labels": {
                "en": {
                    "language": "en",
                    "value": "Updated Deduplication Test Entity",
                },
                "fr": {"language": "fr", "value": "Entité de test de déduplication"},
            },
        }

        update_response = api_client.post(f"{base_url}/entity", json=update_data)
        assert update_response.status_code == 200
        update_result = update_response.json()
        assert update_result["revision_id"] == 2

        # Consume edit event
        expected_type = "edit"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

        # Now update with identical content - should return same revision, no new event
        duplicate_response = api_client.post(f"{base_url}/entity", json=update_data)
        assert duplicate_response.status_code == 200
        duplicate_result = duplicate_response.json()
        assert duplicate_result["revision_id"] == 2  # Same revision

        # Ensure no additional event is published (timeout after short wait)
        start_time = asyncio.get_event_loop().time()
        extra_events = []
        while asyncio.get_event_loop().time() - start_time < 5.0:  # Short timeout
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if msg.value["entity_id"] == expected_entity:
                    extra_events.append(msg.value)
            except asyncio.TimeoutError:
                break
        assert len(extra_events) == 0, (
            f"Unexpected events after deduplication: {extra_events}"
        )

    @pytest.mark.asyncio
    async def test_edit_publishes_creation_event(
        self, api_client: Any, base_url: str, clean_consumer: AIOKafkaConsumer
    ) -> None:
        """Test that edits publish creation events"""
        entity_data = {
            "id": f"{TEST_ENTITY_BASE}10",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Bot Edit Test Entity"}},
        }

        response = api_client.post(f"{base_url}/entity", json=entity_data)
        assert response.status_code == 200

        # Consume creation event
        expected_entity = f"{TEST_ENTITY_BASE}10"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(clean_consumer.getone(), timeout=1.0)
                if (
                    msg.value["entity_id"] == expected_entity
                    and msg.value.get("change_type") == expected_type
                ):
                    event = msg.value
                    break
            except asyncio.TimeoutError:
                continue
        else:
            raise TimeoutError(
                f"Expected {expected_type} message for {expected_entity} not received"
            )

        assert event["entity_id"] == f"{TEST_ENTITY_BASE}10"
