"""Tests for stream consumer."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = pytest.mark.unit

from models.infrastructure.stream.consumer import Consumer, EntityChangeEvent


class TestEntityChangeEvent:
    """Test EntityChangeEvent model."""

    def test_entity_change_event_creation(self) -> None:
        """Test creating an EntityChangeEvent."""
        event = EntityChangeEvent(
            entity_id="Q123",
            revision_id=456,
            timestamp="2023-01-01T00:00:00Z",
            user_id="user123",
            type="edit",
        )
        assert event.entity_id == "Q123"
        assert event.revision_id == 456
        assert event.timestamp == "2023-01-01T00:00:00Z"
        assert event.user_id == "user123"
        assert event.type == "edit"


class TestConsumer:
    """Test Consumer class."""

    @pytest.fixture
    def consumer(self) -> Consumer:
        """Create a consumer instance."""
        return Consumer(brokers=["localhost:9092"])

    def test_consumer_init(self, consumer: Consumer) -> None:
        """Test consumer initialization."""
        assert consumer.bootstrap_servers == "localhost:9092"
        assert consumer.topic == "wikibase-entity-changes"
        assert consumer.group_id == "watchlist-consumer"
        assert consumer.consumer is None

    @pytest.mark.asyncio
    async def test_start_consumer(self, consumer: Consumer) -> None:
        """Test starting the consumer."""
        mock_kafka_consumer = AsyncMock()
        with patch(
            "models.infrastructure.stream.consumer.AIOKafkaConsumer",
            return_value=mock_kafka_consumer,
        ):
            await consumer.start()

        assert consumer.consumer is mock_kafka_consumer
        mock_kafka_consumer.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_consumer(self, consumer: Consumer) -> None:
        """Test stopping the consumer."""
        mock_consumer = AsyncMock()
        consumer.consumer = mock_consumer

        await consumer.stop()

        mock_consumer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_events_without_start(self, consumer: Consumer) -> None:
        """Test consuming events without starting raises error."""
        with pytest.raises(RuntimeError, match="Consumer not started"):
            async for _ in consumer.consume_events():
                pass

    @pytest.mark.asyncio
    async def test_consume_events(self, consumer: Consumer) -> None:
        """Test consuming events."""

        # Create an async generator for messages
        async def mock_messages():
            mock_message = MagicMock()
            mock_message.value = {
                "entity_id": "Q123",
                "revision_id": 456,
                "timestamp": "2023-01-01T00:00:00Z",
                "user_id": "user123",
                "type": "edit",
            }
            yield mock_message

        consumer.consumer = mock_messages()  # Assign the async generator

        events = []
        async for event in consumer.consume_events():
            events.append(event)
            break  # Only consume one for test

        assert len(events) == 1
        assert isinstance(events[0], EntityChangeEvent)
        assert events[0].entity_id == "Q123"
