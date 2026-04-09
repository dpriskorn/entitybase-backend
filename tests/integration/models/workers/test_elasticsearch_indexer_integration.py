"""Integration tests for Elasticsearch indexing pipeline.

Tests the full flow:
1. Create an entity with statements via the API
2. Verify entity_change event is published to Kafka
3. Verify the entity is indexed in Elasticsearch
"""

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
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "entitybase")
TEST_ENTITY_BASE = "Q999999"


@pytest.fixture(scope="session", autouse=True)
def configure_kafka_for_elasticsearch_tests():
    """Configure Kafka for Elasticsearch integration tests.

    These tests require specific Kafka configuration.
    """
    os.environ["KAFKA_BOOTSTRAP_SERVERS"] = KAFKA_BOOTSTRAP_SERVERS
    os.environ["KAFKA_ENTITYCHANGE_JSON_TOPIC"] = KAFKA_TOPIC
    yield


def get_unique_consumer_id() -> str:
    """Generate a unique consumer group ID for each test."""
    return f"test-es-consumer-{uuid.uuid4().hex[:8]}"


async def wait_for_elasticsearch(
    host: str,
    port: int,
    timeout: float = 30.0,
) -> bool:
    """Wait for Elasticsearch to be available."""
    import socket

    start_time = asyncio.get_event_loop().time()
    while asyncio.get_event_loop().time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                await asyncio.sleep(2)
                return True
        except Exception:
            pass
        await asyncio.sleep(1)
    return False


async def get_elasticsearch_doc(
    doc_id: str,
    host: str,
    port: int,
    index: str,
    timeout: float = 30.0,
) -> dict[str, Any] | None:
    """Wait for a document to appear in Elasticsearch."""
    import aiohttp

    start_time = asyncio.get_event_loop().time()
    url = f"http://{host}:{port}/{index}/_doc/{doc_id}"

    while asyncio.get_event_loop().time() - start_time < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("found"):
                            return data.get("_source")
                    elif resp.status == 404:
                        pass
        except Exception as e:
            logger.debug(f"Elasticsearch get failed: {e}")

        await asyncio.sleep(1)

    return None


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
@pytest.mark.requires_kafka
async def test_entity_creation_indexes_to_elasticsearch(api_prefix: str) -> None:
    """Test that creating an entity indexes it to Elasticsearch."""
    from models.rest_api.main import app

    if not await wait_for_elasticsearch(ELASTICSEARCH_HOST, ELASTICSEARCH_PORT):
        pytest.skip("Elasticsearch not available")

    entity_id = f"{TEST_ENTITY_BASE}1"
    entity_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "ES Test Entity"}},
        "descriptions": {
            "en": {"language": "en", "value": "Test entity for ES integration"}
        },
        "statements": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"id": "Q5", "numeric-id": 5},
                        },
                    }
                }
            ]
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
                headers={
                    "X-Edit-Summary": "create test entity for ES",
                    "X-User-ID": "0",
                },
            )
            assert response.status_code == 200

            result = response.json()
            assert result["id"] == entity_id
            assert result["rev_id"] == 1

        event = await _consume_event(consumer, entity_id, "creation", timeout=30.0)
        assert event["entity_id"] == entity_id
        assert event["change_type"] == "creation"
        assert event["revision_id"] == 1

        es_doc = await get_elasticsearch_doc(
            entity_id,
            ELASTICSEARCH_HOST,
            ELASTICSEARCH_PORT,
            ELASTICSEARCH_INDEX,
            timeout=30.0,
        )

        assert es_doc is not None, f"Entity {entity_id} not found in Elasticsearch"
        assert es_doc["id"] == entity_id
        assert es_doc["labels"]["en"]["value"] == "ES Test Entity"
        assert es_doc["descriptions"]["en"]["value"] == "Test entity for ES integration"

    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.requires_kafka
async def test_entity_update_indexes_to_elasticsearch(api_prefix: str) -> None:
    """Test that updating an entity updates it in Elasticsearch."""
    from models.rest_api.main import app

    if not await wait_for_elasticsearch(ELASTICSEARCH_HOST, ELASTICSEARCH_PORT):
        pytest.skip("Elasticsearch not available")

    entity_id = f"{TEST_ENTITY_BASE}2"
    entity_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Original Label"}},
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

            await _consume_event(consumer, entity_id, "creation", timeout=30.0)

            updated_data = {
                "id": entity_id,
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Updated Label"}},
                "descriptions": {
                    "en": {"language": "en", "value": "Updated description"}
                },
            }

            update_response = await client.post(
                f"{api_prefix}/entities/items",
                json=updated_data,
                headers={"X-Edit-Summary": "update test entity", "X-User-ID": "0"},
            )
            assert update_response.status_code == 200
            assert update_response.json()["rev_id"] == 2

        await _consume_event(consumer, entity_id, "edit", timeout=30.0)

        es_doc = await get_elasticsearch_doc(
            entity_id,
            ELASTICSEARCH_HOST,
            ELASTICSEARCH_PORT,
            ELASTICSEARCH_INDEX,
            timeout=30.0,
        )

        assert es_doc is not None
        assert es_doc["labels"]["en"]["value"] == "Updated Label"
        assert es_doc["descriptions"]["en"]["value"] == "Updated description"

    finally:
        await consumer.stop()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.requires_kafka
async def test_entity_deletion_removes_from_elasticsearch(api_prefix: str) -> None:
    """Test that deleting an entity removes it from Elasticsearch."""
    from models.rest_api.main import app

    if not await wait_for_elasticsearch(ELASTICSEARCH_HOST, ELASTICSEARCH_PORT):
        pytest.skip("Elasticsearch not available")

    entity_id = f"{TEST_ENTITY_BASE}3"
    entity_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Entity to Delete"}},
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

            await _consume_event(consumer, entity_id, "creation", timeout=30.0)

            es_doc_before = await get_elasticsearch_doc(
                entity_id,
                ELASTICSEARCH_HOST,
                ELASTICSEARCH_PORT,
                ELASTICSEARCH_INDEX,
                timeout=30.0,
            )
            assert es_doc_before is not None

            delete_response = await client.request(
                "DELETE",
                f"{api_prefix}/entities/{entity_id}",
                json={
                    "delete_type": "soft",
                    "deletion_reason": "Testing ES deletion",
                },
                headers={
                    "X-Edit-Summary": "delete entity",
                    "X-User-ID": "test-integration",
                    "Content-Type": "application/json",
                },
            )
            assert delete_response.status_code == 200

        await _consume_event(consumer, entity_id, "soft_delete", timeout=30.0)

        import aiohttp

        url = f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}/{ELASTICSEARCH_INDEX}/_doc/{entity_id}"
        start_time = asyncio.get_event_loop().time()
        found = True
        while asyncio.get_event_loop().time() - start_time < 30.0:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        if resp.status == 404:
                            found = False
                            break
            except Exception:
                pass
            await asyncio.sleep(1)

        assert not found, (
            f"Entity {entity_id} still found in Elasticsearch after deletion"
        )

    finally:
        await consumer.stop()
