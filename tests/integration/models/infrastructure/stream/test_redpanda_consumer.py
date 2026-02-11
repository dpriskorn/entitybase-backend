"""Integration tests for Redpanda stream consumer."""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import AsyncGenerator, Any

import pytest
from aiokafka import AIOKafkaProducer

from models.data.config.stream_consumer import StreamConsumerConfig
from models.data.infrastructure.stream.consumer import EntityChangeEventData
from models.infrastructure.stream.consumer import StreamConsumerClient
from models.data.config.stream import StreamConfig
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.stream.event import EntityChangeEvent
from models.data.infrastructure.stream.change_type import ChangeType

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "wikibase.entity_change")
TEST_ENTITY_BASE = "Q888888"
TEST_USER_ID = "test-user-123"


class TestConsumerIntegration:
    """Integration tests for Redpanda consumer."""

    @pytest.mark.asyncio
    async def test_consumer_start_and_stop(self) -> None:
        """Test that consumer can be started and stopped successfully."""
        config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id="test-consumer",
        )
        consumer = StreamConsumerClient(config=config)

        assert consumer.healthy_connection is False
        assert consumer.consumer is None

        await consumer.start()
        assert consumer.healthy_connection is True
        assert consumer.consumer is not None

        await consumer.stop()
        assert consumer.healthy_connection is False
        assert consumer.consumer is None

    @pytest.mark.asyncio
    async def test_consumer_consume_single_event(self) -> None:
        """Test that consumer can consume single events from the topic."""
        config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id="test-consumer-single",
        )
        consumer = StreamConsumerClient(config=config)

        # First, publish an event
        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        changed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}30",
            revision_id=1,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        await producer.start()
        await producer.publish_change(event)
        await producer.stop()

        # Then, consume the event
        await consumer.start()
        try:
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                break  # Only consume one for this test

            assert len(events) == 1
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}30"
            assert events[0].revision_id == 1
            assert events[0].change_type == "creation"
            assert events[0].user_id == TEST_USER_ID
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_consumer_consume_multiple_events(self) -> None:
        """Test that consumer can consume multiple events from the topic."""
        config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id="test-consumer-multi",
        )
        consumer = StreamConsumerClient(config=config)

        # First, publish multiple events
        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        events_to_publish = [
            EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}40",
                revision_id=1,
                change_type=ChangeType.CREATION,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
            ),
            EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}40",
                revision_id=2,
                change_type=ChangeType.EDIT,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
                from_revision_id=1,
            ),
            EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}41",
                revision_id=3,
                change_type=ChangeType.CREATION,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
            ),
        ]

        await producer.start()
        for event in events_to_publish:
            await producer.publish_change(event)
        await producer.stop()

        # Then, consume all events
        await consumer.start()
        try:
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                if len(events) >= 3:
                    break

            assert len(events) == 3
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}40"
            assert events[0].revision_id == 1
            assert events[0].change_type == "creation"

            assert events[1].entity_id == f"{TEST_ENTITY_BASE}40"
            assert events[1].revision_id == 2
            assert events[1].change_type == "edit"

            assert events[2].entity_id == f"{TEST_ENTITY_BASE}41"
            assert events[2].revision_id == 3
            assert events[2].change_type == "creation"
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_consumer_consume_from_different_topics(self) -> None:
        """Test that consumer can consume from different topics."""
        topic1 = "wikibase.entity_change"
        topic2 = "wikibase.entity_diff"

        # Publish events to different topics
        producer_config1 = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=topic1
        )
        producer1 = StreamProducerClient(config=producer_config1)

        producer_config2 = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=topic2
        )
        producer2 = StreamProducerClient(config=producer_config2)

        event1 = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}50",
            revision_id=1,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        event2 = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}51",
            revision_id=1,
            change_type=ChangeType.EDIT,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        await producer1.start()
        await producer2.start()
        await producer1.publish_change(event1)
        await producer2.publish_change(event2)
        await producer1.stop()
        await producer2.stop()

        # Consume from topic1
        consumer_config1 = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=topic1,
            group_id="test-consumer-topic1",
        )
        consumer1 = StreamConsumerClient(config=consumer_config1)

        await consumer1.start()
        try:
            events: list[EntityChangeEventData] = []
            async for event in consumer1.consume_events():
                events.append(event)
                break

            assert len(events) == 1
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}50"
            assert events[0].change_type == "creation"
        finally:
            await consumer1.stop()

        # Consume from topic2
        consumer_config2 = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=topic2,
            group_id="test-consumer-topic2",
        )
        consumer2 = StreamConsumerClient(config=consumer_config2)

        await consumer2.start()
        try:
            events: list[EntityChangeEventData] = []
            async for event in consumer2.consume_events():
                events.append(event)
                break

            assert len(events) == 1
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}51"
            assert events[0].change_type == "entity_diff"
        finally:
            await consumer2.stop()

    @pytest.mark.asyncio
    async def test_consumer_health_check(self) -> None:
        """Test consumer health check property."""
        config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id="test-consumer-health",
        )
        consumer = StreamConsumerClient(config=config)

        assert consumer.healthy_connection is False

        await consumer.start()
        assert consumer.healthy_connection is True

        await consumer.stop()
        assert consumer.healthy_connection is False

    @pytest.mark.asyncio
    async def test_consumer_consume_after_producer_stop(self) -> None:
        """Test that consumer can still consume after producer stops."""
        config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id="test-consumer-after-stop",
        )
        consumer = StreamConsumerClient(config=config)

        # Publish an event
        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        event_data = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}60",
            revision_id=1,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        await producer.start()
        await producer.publish_change(event_data)
        await producer.stop()

        # Consume the event
        await consumer.start()
        try:
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                break

            assert len(events) == 1
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}60"
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_consumer_consume_multiple_groups(self) -> None:
        """Test that multiple consumer groups can consume from the same topic."""
        topic = "wikibase.entity_change"

        # Publish an event
        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=topic
        )
        producer = StreamProducerClient(config=producer_config)

        event_data = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}70",
            revision_id=1,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        await producer.start()
        await producer.publish_change(event_data)
        await producer.stop()

        # Create multiple consumers with different groups
        consumer1_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS], topic=topic, group_id="group-consumer-1"
        )
        consumer1 = StreamConsumerClient(config=consumer1_config)

        consumer2_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS], topic=topic, group_id="group-consumer-2"
        )
        consumer2 = StreamConsumerClient(config=consumer2_config)

        await consumer1.start()
        await consumer2.start()

        try:
            events1: list[EntityChangeEventData] = []
            events2: list[EntityChangeEventData] = []

            async for event in consumer1.consume_events():
                events1.append(event)
                break

            async for event in consumer2.consume_events():
                events2.append(event)
                break

            assert len(events1) == 1
            assert len(events2) == 1
            assert (
                events1[0].entity_id == events2[0].entity_id == f"{TEST_ENTITY_BASE}70"
            )
        finally:
            await consumer1.stop()
            await consumer2.stop()

    @pytest.mark.asyncio
    async def test_consumer_consume_from_late_messages(self) -> None:
        """Test that consumer can consume messages published after consumer starts."""
        topic = "wikibase.entity_change"

        # Start consumer first
        config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=topic,
            group_id="test-consumer-late",
        )
        consumer = StreamConsumerClient(config=config)

        await consumer.start()
        try:
            # Give consumer time to start
            await asyncio.sleep(0.5)

            # Publish event after consumer starts
            producer_config = StreamConfig(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=topic
            )
            producer = StreamProducerClient(config=producer_config)

            event_data = EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}80",
                revision_id=1,
                change_type=ChangeType.CREATION,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
            )

            await producer.start()
            await producer.publish_change(event_data)
            await producer.stop()

            # Consume the event
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                break

            assert len(events) == 1
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}80"
            assert events[0].change_type == "creation"
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_consumer_consume_event_with_special_characters(self) -> None:
        """Test that consumer can handle events with special characters."""
        topic = "wikibase.entity_change"

        # Publish event with special characters
        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=topic
        )
        producer = StreamProducerClient(config=producer_config)

        event_data = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}90",
            revision_id=1,
            change_type=ChangeType.EDIT,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
            edit_summary="Test with special chars: <>&\"' and emojis: 🚀✨",
        )

        await producer.start()
        await producer.publish_change(event_data)
        await producer.stop()

        # Consume and verify special characters
        config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=topic,
            group_id="test-consumer-special",
        )
        consumer = StreamConsumerClient(config=config)

        await consumer.start()
        try:
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                break

            assert len(events) == 1
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}90"
            assert (
                events[0].edit_summary
                == "Test with special chars: <>&\"' and emojis: 🚀✨"
            )
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_consumer_multiple_brokers(self) -> None:
        """Test that consumer can connect to multiple brokers."""
        config = StreamConsumerConfig(
            brokers=["redpanda:9092", "redpanda:9093"],
            topic=KAFKA_TOPIC,
            group_id="test-consumer-multi-brokers",
        )
        consumer = StreamConsumerClient(config=config)

        assert consumer.healthy_connection is False

        await consumer.start()
        assert consumer.healthy_connection is True

        await consumer.stop()
        assert consumer.healthy_connection is False
