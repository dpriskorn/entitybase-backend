"""Integration tests for entity stream integration with Redpanda."""

import asyncio
import json
import logging
import os
import uuid
from typing import Any

import pytest
from aiokafka import AIOKafkaConsumer
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "wikibase.entity_change")
TEST_ENTITY_BASE = "Q888888"


def get_unique_consumer_id() -> str:
    """Generate a unique consumer group ID for each test."""
    return f"test-consumer-{uuid.uuid4().hex[:8]}"


async def _consume_event(
    consumer: AIOKafkaConsumer,
    expected_entity: str,
    expected_type: str,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Consume messages until finding the expected event type for an entity."""
    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        try:
            msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
            if msg.value is None:
                continue
            if (
                msg.value.get("entity_id") == expected_entity
                and msg.value.get("change_type") == expected_type
            ):
                return msg.value
        except asyncio.TimeoutError:
            continue
    raise TimeoutError(
        f"Expected {expected_type} message for {expected_entity} not received within timeout"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_creation_publishes_creation_event(api_prefix: str) -> None:
    """Test that creating an entity publishes a CREATION event"""
    from models.rest_api.main import app

    entity_data = {
        "id": f"{TEST_ENTITY_BASE}0",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Stream Test Entity Creation"}},
        "descriptions": {
            "en": {"language": "en", "value": "Test entity for stream integration"}
        },
    }

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            result = response.json()
            assert result["id"] == f"{TEST_ENTITY_BASE}0"
            assert result["rev_id"] == 1

        expected_entity = f"{TEST_ENTITY_BASE}0"
        expected_type = "creation"
        start_time = asyncio.get_event_loop().time()
        event = None
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                if (
                    msg.value.get("entity_id") == expected_entity
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
        assert event.get("from_revision_id") is None
        assert "changed_at" in event
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_update_publishes_edit_event(api_prefix: str) -> None:
    """Test that updating an entity publishes an EDIT event with from_revision_id"""
    from models.rest_api.main import app

    entity = f"{TEST_ENTITY_BASE}1"
    entity_data = {
        "id": entity,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Entity for Edit Test"}},
    }

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            logger.debug(f"{entity} creation response code:")
            assert create_response.status_code == 200

            expected_entity = f"{TEST_ENTITY_BASE}1"
            expected_type = "creation"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
                        and msg.value.get("change_type") == expected_type
                    ):
                        break
                except asyncio.TimeoutError:
                    continue
            else:
                raise TimeoutError(
                    f"Expected {expected_type} message for {expected_entity} not received"
                )

            delete_response = await client.request(
                "DELETE",
                f"{api_prefix}/entities/{TEST_ENTITY_BASE}1",
                json={
                    "delete_type": "soft",
                    "deletion_reason": "Testing stream integration",
                },
                headers={
                    "X-Edit-Summary": "delete entity",
                    "X-User-ID": "test-integration",
                    "Content-Type": "application/json",
                },
            )
            logger.debug(f"{entity} deletion response code:")
            assert delete_response.status_code == 200

            expected_entity = f"{TEST_ENTITY_BASE}1"
            expected_type = "soft_delete"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
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
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_redirect_creation_publishes_redirect_event(api_prefix: str) -> None:
    """Test that creating a redirect publishes a REDIRECT event"""
    from models.rest_api.main import app

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

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_source = await client.post(
                f"{api_prefix}/entities/items",
                json=source_entity,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert create_source.status_code == 200
            expected_entity = f"{TEST_ENTITY_BASE}3"
            expected_type = "creation"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
                        and msg.value.get("change_type") == expected_type
                    ):
                        break
                except asyncio.TimeoutError:
                    continue
            else:
                raise TimeoutError(
                    f"Expected {expected_type} message for {expected_entity} not received"
                )

            create_target = await client.post(
                f"{api_prefix}/entities/items",
                json=target_entity,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert create_target.status_code == 200
            expected_entity = f"{TEST_ENTITY_BASE}4"
            expected_type = "creation"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
                        and msg.value.get("change_type") == expected_type
                    ):
                        break
                except asyncio.TimeoutError:
                    continue
            else:
                raise TimeoutError(
                    f"Expected {expected_type} message for {expected_entity} not received"
                )

            redirect_response = await client.post(
                f"{api_prefix}/redirects",
                json={
                    "redirect_from_id": f"{TEST_ENTITY_BASE}3",
                    "redirect_to_id": f"{TEST_ENTITY_BASE}4",
                    "created_by": "test-integration",
                },
                headers={"X-Edit-Summary": "create redirect", "X-User-ID": "0"},
            )
            assert redirect_response.status_code == 200

            expected_entity = f"{TEST_ENTITY_BASE}3"
            expected_type = "redirect"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
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
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_redirect_reversion_publishes_unredirect_event(api_prefix: str) -> None:
    """Test that reverting a redirect publishes an UNREDIRECT event"""
    from models.rest_api.main import app

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

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_source = await client.post(
                f"{api_prefix}/entities/items",
                json=source_entity,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert create_source.status_code == 200
            await _consume_event(consumer, f"{TEST_ENTITY_BASE}5", "creation")

            create_target = await client.post(
                f"{api_prefix}/entities/items",
                json=target_entity,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert create_target.status_code == 200
            await _consume_event(consumer, f"{TEST_ENTITY_BASE}6", "creation")

            redirect_response = await client.post(
                f"{api_prefix}/redirects",
                json={
                    "redirect_from_id": f"{TEST_ENTITY_BASE}5",
                    "redirect_to_id": f"{TEST_ENTITY_BASE}6",
                    "created_by": "test-integration",
                },
                headers={"X-Edit-Summary": "create redirect", "X-User-ID": "0"},
            )
            assert redirect_response.status_code == 200
            await _consume_event(consumer, f"{TEST_ENTITY_BASE}5", "redirect")

            revert_response = await client.post(
                f"{api_prefix}/entities/{TEST_ENTITY_BASE}5/revert-redirect",
                json={
                    "revert_to_revision_id": 1,
                    "revert_reason": "Testing unredirect event",
                },
                headers={"X-Edit-Summary": "revert redirect", "X-User-ID": "0"},
            )
            assert revert_response.status_code == 200

            event = await _consume_event(consumer, f"{TEST_ENTITY_BASE}5", "unredirect")
            assert event["entity_id"] == f"{TEST_ENTITY_BASE}5"
            assert event["change_type"] == "unredirect"
            assert "revision_id" in event
            assert "from_revision_id" in event
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_event_schema_validation(api_prefix: str) -> None:
    """Test that all published events have the correct schema"""
    from models.rest_api.main import app

    entity_data = {
        "id": f"{TEST_ENTITY_BASE}7",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Schema Validation Test"}},
        "descriptions": {"en": {"language": "en", "value": "Testing event schema"}},
        "aliases": {"en": [{"language": "en", "value": "Test Alias"}]},
    }

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            expected_entity = f"{TEST_ENTITY_BASE}7"
            expected_type = "creation"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
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
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_multiple_entity_operations_publish_multiple_events(
    api_prefix: str,
) -> None:
    """Test that multiple entity operations publish multiple events"""
    from models.rest_api.main import app

    entity_data = {
        "id": f"{TEST_ENTITY_BASE}8",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Multi Operation Test Entity"}},
    }

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert create_response.status_code == 200

            expected_entity = f"{TEST_ENTITY_BASE}8"
            expected_type = "creation"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
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
                    "fr": {
                        "language": "fr",
                        "value": "Entité de test multi-opérations",
                    },
                },
            }

            update_response = await client.post(
                f"{api_prefix}/entities/items",
                json=update_data,
                headers={"X-Edit-Summary": "update test entity", "X-User-ID": "0"},
            )
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

            update2_response = await client.post(
                f"{api_prefix}/entities/items",
                json=update2_data,
                headers={
                    "X-Edit-Summary": "update test entity again",
                    "X-User-ID": "0",
                },
            )
            assert update2_response.status_code == 200

            expected_entity = f"{TEST_ENTITY_BASE}8"
            events: list[Any] = []
            start_time = asyncio.get_event_loop().time()
            while (
                len(events) < 2 and asyncio.get_event_loop().time() - start_time < 30.0
            ):
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if msg.value.get("entity_id") == expected_entity:
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
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_update_deduplication_no_duplicate_event(api_prefix: str) -> None:
    """Test that updating an entity with identical content doesn't publish duplicate events"""
    from models.rest_api.main import app

    entity_data = {
        "id": f"{TEST_ENTITY_BASE}9",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Deduplication Test Entity"}},
    }

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            create_response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert create_response.status_code == 200
            create_result = create_response.json()
            assert create_result["rev_id"] == 1

            expected_entity = f"{TEST_ENTITY_BASE}9"
            expected_type = "creation"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
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
                    "fr": {
                        "language": "fr",
                        "value": "Entité de test de déduplication",
                    },
                },
            }

            update_response = await client.post(
                f"{api_prefix}/entities/items",
                json=update_data,
                headers={"X-Edit-Summary": "update test entity", "X-User-ID": "0"},
            )
            assert update_response.status_code == 200
            update_result = update_response.json()
            assert update_result["rev_id"] == 2

            expected_type = "edit"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
                        and msg.value.get("change_type") == expected_type
                    ):
                        break
                except asyncio.TimeoutError:
                    continue
            else:
                raise TimeoutError(
                    f"Expected {expected_type} message for {expected_entity} not received"
                )

            duplicate_response = await client.post(
                f"{api_prefix}/entities/items",
                json=update_data,
                headers={"X-Edit-Summary": "update test entity", "X-User-ID": "0"},
            )
            assert duplicate_response.status_code == 200
            duplicate_result = duplicate_response.json()
            assert duplicate_result["rev_id"] == 2

            start_time = asyncio.get_event_loop().time()
            extra_events = []
            while asyncio.get_event_loop().time() - start_time < 5.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if msg.value.get("entity_id") == expected_entity:
                        extra_events.append(msg.value)
                except asyncio.TimeoutError:
                    break
            assert len(extra_events) == 0, (
                f"Unexpected events after deduplication: {extra_events}"
            )
    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_publishes_creation_event(api_prefix: str) -> None:
    """Test that edits publish creation events"""
    from models.rest_api.main import app

    entity_data = {
        "id": f"{TEST_ENTITY_BASE}10",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Bot Edit Test Entity"}},
    }

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=get_unique_consumer_id(),
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            expected_entity = f"{TEST_ENTITY_BASE}10"
            expected_type = "creation"
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 30.0:
                try:
                    msg = await asyncio.wait_for(consumer.getone(), timeout=1.0)
                    if (
                        msg.value.get("entity_id") == expected_entity
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
    finally:
        await consumer.stop()
