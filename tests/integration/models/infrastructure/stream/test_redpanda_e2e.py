"""End-to-end tests for Redpanda producer and consumer together."""

import asyncio
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import pytest

from models.data.config.stream import StreamConfig
from models.data.config.stream_consumer import StreamConsumerConfig
from models.data.infrastructure.stream.consumer import EntityChangeEventData
from models.infrastructure.stream.consumer import StreamConsumerClient
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.stream.event import EntityChangeEvent
from models.data.infrastructure.stream.change_type import ChangeType

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "wikibase.entity_change")
TEST_ENTITY_BASE = "Q888888"
TEST_USER_ID = "test-user-123"


def get_unique_consumer_id() -> str:
    """Generate a unique consumer group ID for each test."""
    return f"test-consumer-e2e-{uuid.uuid4().hex[:8]}"


class TestProducerConsumerEndToEnd:
    """End-to-end tests for producer and consumer integration."""

    @pytest.mark.asyncio
    async def test_producer_consume_complete_lifecycle(self) -> None:
        """Test complete producer-consumer lifecycle with multiple events."""
        # Setup consumer first
        consumer_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id=get_unique_consumer_id(),
        )
        consumer = StreamConsumerClient(config=consumer_config)

        # Setup producer
        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        # Create events
        events = [
            EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}100",
                revision_id=1,
                change_type=ChangeType.CREATION,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
            ),
            EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}100",
                revision_id=2,
                change_type=ChangeType.EDIT,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
                from_revision_id=1,
            ),
            EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}101",
                revision_id=3,
                change_type=ChangeType.CREATION,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
            ),
        ]

        # Start consumer and producer
        await consumer.start()
        await producer.start()

        try:
            # Publish all events
            for event in events:
                await producer.publish_change(event)

            # Consume all events
            received_events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                received_events.append(event)
                if len(received_events) >= len(events):
                    break

            # Verify all events were received
            assert len(received_events) == len(events), (
                f"Expected {len(events)} events, got {len(received_events)}"
            )

            # Verify first event
            assert received_events[0].entity_id == f"{TEST_ENTITY_BASE}100"
            assert received_events[0].revision_id == 1
            assert received_events[0].change_type == "creation"

            # Verify second event
            assert received_events[1].entity_id == f"{TEST_ENTITY_BASE}100"
            assert received_events[1].revision_id == 2
            assert received_events[1].change_type == "edit"
            assert received_events[1].from_revision_id == 1

            # Verify third event
            assert received_events[2].entity_id == f"{TEST_ENTITY_BASE}101"
            assert received_events[2].revision_id == 3
            assert received_events[2].change_type == "creation"

        finally:
            await producer.stop()
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_producer_consume_delete_workflow(self) -> None:
        """Test producer-consumer workflow for entity deletion."""
        # Setup components
        consumer_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id=get_unique_consumer_id(),
        )
        consumer = StreamConsumerClient(config=consumer_config)

        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        # Create a new entity
        create_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}200",
            revision_id=1,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        # Publish creation
        await producer.start()
        await consumer.start()

        try:
            await producer.publish_change(create_event)

            # Consume creation
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                break

            assert len(events) == 1
            assert events[0].change_type == "creation"

            # Publish soft delete
            delete_event = EntityChangeEvent(
                entity_id=f"{TEST_ENTITY_BASE}200",
                revision_id=2,
                change_type=ChangeType.SOFT_DELETE,
                changed_at=datetime.now(timezone.utc),
                user_id=TEST_USER_ID,
                from_revision_id=1,
                edit_summary="Test deletion",
            )

            await producer.publish_change(delete_event)

            # Consume soft delete
            events = []
            async for event in consumer.consume_events():
                events.append(event)
                break

            assert len(events) == 1
            assert events[0].change_type == "soft_delete"
            assert events[0].edit_summary == "Test deletion"
            assert events[0].from_revision_id == 1

        finally:
            await producer.stop()
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_producer_consume_redirect_workflow(self) -> None:
        """Test producer-consumer workflow for entity redirection."""
        # Setup components
        consumer_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id=get_unique_consumer_id(),
        )
        consumer = StreamConsumerClient(config=consumer_config)

        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        # Create two entities
        source_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}300",
            revision_id=1,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        target_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}301",
            revision_id=2,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        # Create redirect
        redirect_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}300",
            revision_id=3,
            change_type=ChangeType.REDIRECT,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
            from_revision_id=2,
        )

        # Start both components
        await producer.start()
        await consumer.start()

        try:
            # Publish events in sequence
            await producer.publish_change(source_event)
            await producer.publish_change(target_event)
            await producer.publish_change(redirect_event)

            # Consume all events
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                if len(events) >= 3:
                    break

            # Verify events
            assert len(events) == 3

            # Source creation
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}300"
            assert events[0].change_type == "creation"

            # Target creation
            assert events[1].entity_id == f"{TEST_ENTITY_BASE}301"
            assert events[1].change_type == "creation"

            # Redirect
            assert events[2].entity_id == f"{TEST_ENTITY_BASE}300"
            assert events[2].change_type == "redirect"
            assert events[2].from_revision_id == 2

        finally:
            await producer.stop()
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_producer_consume_unredirect_workflow(self) -> None:
        """Test producer-consumer workflow for removing redirection."""
        # Setup components
        consumer_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id=get_unique_consumer_id(),
        )
        consumer = StreamConsumerClient(config=consumer_config)

        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        # Create entities and redirect
        source_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}400",
            revision_id=1,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        target_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}401",
            revision_id=2,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
        )

        redirect_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}400",
            revision_id=3,
            change_type=ChangeType.REDIRECT,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
            from_revision_id=2,
        )

        # Unredirect
        unredirect_event = EntityChangeEvent(
            entity_id=f"{TEST_ENTITY_BASE}400",
            revision_id=4,
            change_type=ChangeType.UNREDIRECT,
            changed_at=datetime.now(timezone.utc),
            user_id=TEST_USER_ID,
            from_revision_id=3,
        )

        # Start both components
        await producer.start()
        await consumer.start()

        try:
            # Publish events in sequence
            await producer.publish_change(source_event)
            await producer.publish_change(target_event)
            await producer.publish_change(redirect_event)
            await producer.publish_change(unredirect_event)

            # Consume all events
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                if len(events) >= 4:
                    break

            # Verify events
            assert len(events) == 4

            # Source creation
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}400"
            assert events[0].change_type == "creation"

            # Target creation
            assert events[1].entity_id == f"{TEST_ENTITY_BASE}401"
            assert events[1].change_type == "creation"

            # Redirect
            assert events[2].entity_id == f"{TEST_ENTITY_BASE}400"
            assert events[2].change_type == "redirect"

            # Unredirect
            assert events[3].entity_id == f"{TEST_ENTITY_BASE}400"
            assert events[3].change_type == "unredirect"
            assert events[3].from_revision_id == 3

        finally:
            await producer.stop()
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_producer_consume_multiple_entities(self) -> None:
        """Test producer-consumer workflow with multiple independent entities."""
        # Setup components
        consumer_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id=get_unique_consumer_id(),
        )
        consumer = StreamConsumerClient(config=consumer_config)

        producer_config = StreamConfig(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS], topic=KAFKA_TOPIC
        )
        producer = StreamProducerClient(config=producer_config)

        # Create multiple independent entities with their revisions
        entities_to_create = [
            f"{TEST_ENTITY_BASE}500",
            f"{TEST_ENTITY_BASE}501",
            f"{TEST_ENTITY_BASE}502",
        ]

        # Start both components
        await producer.start()
        await consumer.start()

        try:
            # Publish creation and edit events for each entity
            for entity_id in entities_to_create:
                # Creation
                await producer.publish_change(
                    EntityChangeEvent(
                        entity_id=entity_id,
                        revision_id=1,
                        change_type=ChangeType.CREATION,
                        changed_at=datetime.now(timezone.utc),
                        user_id=TEST_USER_ID,
                    )
                )
                # Edit
                await producer.publish_change(
                    EntityChangeEvent(
                        entity_id=entity_id,
                        revision_id=2,
                        change_type=ChangeType.EDIT,
                        changed_at=datetime.now(timezone.utc),
                        user_id=TEST_USER_ID,
                        from_revision_id=1,
                    )
                )

            # Consume all events
            events: list[EntityChangeEventData] = []
            async for event in consumer.consume_events():
                events.append(event)
                if len(events) >= 6:
                    break

            # Verify all events
            assert len(events) == 6

            # Verify first entity
            assert events[0].entity_id == f"{TEST_ENTITY_BASE}500"
            assert events[0].change_type == "creation"
            assert events[1].entity_id == f"{TEST_ENTITY_BASE}500"
            assert events[1].change_type == "edit"

            # Verify second entity
            assert events[2].entity_id == f"{TEST_ENTITY_BASE}501"
            assert events[2].change_type == "creation"
            assert events[3].entity_id == f"{TEST_ENTITY_BASE}501"
            assert events[3].change_type == "edit"

            # Verify third entity
            assert events[4].entity_id == f"{TEST_ENTITY_BASE}502"
            assert events[4].change_type == "creation"
            assert events[5].entity_id == f"{TEST_ENTITY_BASE}502"
            assert events[5].change_type == "edit"

        finally:
            await producer.stop()
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_producer_consume_error_handling(self) -> None:
        """Test that consumer handles errors gracefully."""
        # Setup consumer
        consumer_config = StreamConsumerConfig(
            brokers=[KAFKA_BOOTSTRAP_SERVERS],
            topic=KAFKA_TOPIC,
            group_id=get_unique_consumer_id(),
        )
        consumer = StreamConsumerClient(config=consumer_config)

        # Start consumer
        await consumer.start()

        try:
            # Try to consume without publishing events (should timeout)
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    consumer.consume_events().__anext__(), timeout=2.0
                )
        finally:
            await consumer.stop()
