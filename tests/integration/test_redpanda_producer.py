"""Integration tests for Redpanda stream producer."""

import asyncio
import json
import logging
import os
import time
from typing import Any

import pytest
from aiokafka import AIOKafkaConsumer
from pydantic import BaseModel

from models.data.config.stream import StreamConfig
from models.infrastructure.stream.producer import StreamProducerClient

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "wikibase.entity_change")
TEST_ENTITY_BASE = "Q888888"
TEST_CHANGE_TYPES = ["creation", "edit", "soft_delete", "hard_delete", "redirect", "unredirect"]
TEST_USER_ID = "test-user-123"


class TestProducerIntegration:
    """Integration tests for Redpanda producer."""

    @pytest.mark.asyncio
    async def test_producer_start_and_stop(self) -> None:
        """Test that producer can be started and stopped successfully."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        assert producer.healthy_connection is False
        assert producer.producer is None

        await producer.start()
        assert producer.healthy_connection is True
        assert producer.producer is not None

        await producer.stop()
        assert producer.healthy_connection is False
        assert producer.producer is None

    @pytest.mark.asyncio
    async def test_producer_publishes_creation_event(self) -> None:
        """Test that producer publishes creation events with correct structure."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        event_data = {
            "entity_id": f"{TEST_ENTITY_BASE}0",
            "revision_id": 1,
            "change_type": "creation",
            "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user_id": TEST_USER_ID,
        }

        await producer.start()
        try:
            await producer.publish_change(event_data)

            # Consume the published message
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                received_data = message.value
                assert received_data["entity_id"] == f"{TEST_ENTITY_BASE}0"
                assert received_data["revision_id"] == 1
                assert received_data["change_type"] == "creation"
                assert "changed_at" in received_data
                assert received_data["user_id"] == TEST_USER_ID
                assert received_data["from_revision_id"] is None
            finally:
                await consumer.stop()
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_publishes_edit_event(self) -> None:
        """Test that producer publishes edit events with from_revision_id."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        event_data = {
            "entity_id": f"{TEST_ENTITY_BASE}1",
            "revision_id": 2,
            "change_type": "edit",
            "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user_id": TEST_USER_ID,
            "from_revision_id": 1,
        }

        await producer.start()
        try:
            await producer.publish_change(event_data)

            # Consume the published message
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                received_data = message.value
                assert received_data["entity_id"] == f"{TEST_ENTITY_BASE}1"
                assert received_data["revision_id"] == 2
                assert received_data["change_type"] == "edit"
                assert received_data["from_revision_id"] == 1
                assert received_data["user_id"] == TEST_USER_ID
            finally:
                await consumer.stop()
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_publishes_soft_delete_event(self) -> None:
        """Test that producer publishes soft delete events."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        event_data = {
            "entity_id": f"{TEST_ENTITY_BASE}2",
            "revision_id": 3,
            "change_type": "soft_delete",
            "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user_id": TEST_USER_ID,
            "from_revision_id": 2,
            "delete_type": "soft",
            "deletion_reason": "Test deletion",
        }

        await producer.start()
        try:
            await producer.publish_change(event_data)

            # Consume the published message
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                received_data = message.value
                assert received_data["entity_id"] == f"{TEST_ENTITY_BASE}2"
                assert received_data["change_type"] == "soft_delete"
                assert received_data["delete_type"] == "soft"
                assert received_data["deletion_reason"] == "Test deletion"
            finally:
                await consumer.stop()
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_publishes_redirect_event(self) -> None:
        """Test that producer publishes redirect events."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        event_data = {
            "entity_id": f"{TEST_ENTITY_BASE}3",
            "revision_id": 4,
            "change_type": "redirect",
            "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user_id": TEST_USER_ID,
            "from_revision_id": 3,
            "redirect_from_id": f"{TEST_ENTITY_BASE}3",
            "redirect_to_id": f"{TEST_ENTITY_BASE}4",
        }

        await producer.start()
        try:
            await producer.publish_change(event_data)

            # Consume the published message
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                received_data = message.value
                assert received_data["entity_id"] == f"{TEST_ENTITY_BASE}3"
                assert received_data["change_type"] == "redirect"
                assert received_data["redirect_from_id"] == f"{TEST_ENTITY_BASE}3"
                assert received_data["redirect_to_id"] == f"{TEST_ENTITY_BASE}4"
            finally:
                await consumer.stop()
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_publishes_multiple_events(self) -> None:
        """Test that producer can publish multiple events sequentially."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        events = [
            {"entity_id": f"{TEST_ENTITY_BASE}5", "revision_id": 1, "change_type": "creation", "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "user_id": TEST_USER_ID},
            {"entity_id": f"{TEST_ENTITY_BASE}5", "revision_id": 2, "change_type": "edit", "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "user_id": TEST_USER_ID, "from_revision_id": 1},
            {"entity_id": f"{TEST_ENTITY_BASE}5", "revision_id": 3, "change_type": "edit", "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "user_id": TEST_USER_ID, "from_revision_id": 2},
        ]

        await producer.start()
        try:
            for event_data in events:
                await producer.publish_change(event_data)

            # Consume all events
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                received_events = []
                for _ in events:
                    message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                    received_events.append(message.value)

                assert len(received_events) == 3
                assert received_events[0]["change_type"] == "creation"
                assert received_events[1]["change_type"] == "edit"
                assert received_events[2]["change_type"] == "edit"
            finally:
                await consumer.stop()
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_healthy_connection_after_start(self) -> None:
        """Test that healthy_connection property returns True after start."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        assert producer.healthy_connection is False

        await producer.start()
        assert producer.healthy_connection is True

        await producer.stop()
        assert producer.healthy_connection is False

    @pytest.mark.asyncio
    async def test_producer_event_key_extraction(self) -> None:
        """Test that producer correctly extracts entity_id for key."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        event_data = {
            "entity_id": f"{TEST_ENTITY_BASE}10",
            "revision_id": 5,
            "change_type": "edit",
            "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user_id": TEST_USER_ID,
        }

        await producer.start()
        try:
            await producer.publish_change(event_data)

            # Consume the published message and check key
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                # The key should be the entity_id
                assert message.key == f"{TEST_ENTITY_BASE}10".encode()
            finally:
                await consumer.stop()
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_event_serialization(self) -> None:
        """Test that producer correctly serializes events to JSON."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        event_data = {
            "entity_id": f"{TEST_ENTITY_BASE}20",
            "revision_id": 6,
            "change_type": "edit",
            "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user_id": TEST_USER_ID,
            "from_revision_id": 5,
            "edit_summary": "Test edit summary with special chars: <>&\"'",
        }

        await producer.start()
        try:
            await producer.publish_change(event_data)

            # Consume the published message and verify JSON structure
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                received_data = message.value

                # Verify JSON serialization handles special characters
                assert received_data["edit_summary"] == "Test edit summary with special chars: <>&\"'"
                assert isinstance(received_data, dict)
                assert all(key in received_data for key in ["entity_id", "revision_id", "change_type", "changed_at", "user_id", "from_revision_id"])
            finally:
                await consumer.stop()
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_producer_publishes_different_change_types(self) -> None:
        """Test that producer publishes events for all change types."""
        config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=config)

        await producer.start()
        try:
            for change_type in TEST_CHANGE_TYPES:
                event_data = {
                    "entity_id": f"{TEST_ENTITY_BASE}{ord(change_type)}",
                    "revision_id": 10,
                    "change_type": change_type,
                    "changed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "user_id": TEST_USER_ID,
                }
                if change_type in ["edit", "soft_delete", "redirect", "unredirect"]:
                    event_data["from_revision_id"] = 9
                if change_type == "soft_delete":
                    event_data["delete_type"] = "soft"
                    event_data["deletion_reason"] = f"Test {change_type}"
                if change_type in ["redirect", "unredirect"]:
                    event_data["redirect_from_id"] = f"{TEST_ENTITY_BASE}{ord(change_type)}"
                    event_data["redirect_to_id"] = f"{TEST_ENTITY_BASE}{ord(change_type)+1}"

                await producer.publish_change(event_data)

            # Consume all events and verify types
            consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id="test-consumer",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset="earliest",
            )
            await consumer.start()
            try:
                received_events = []
                for _ in TEST_CHANGE_TYPES:
                    message = await asyncio.wait_for(consumer.getone(), timeout=5.0)
                    received_events.append(message.value)

                assert len(received_events) == len(TEST_CHANGE_TYPES)
                assert [e["change_type"] for e in received_events] == TEST_CHANGE_TYPES
            finally:
                await consumer.stop()
        finally:
            await producer.stop()
