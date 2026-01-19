import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import EntityChangeEvent
from models.infrastructure.stream.producer import StreamProducerClient


class TestStreamProducerClient:
    """Tests for StreamProducerClient with mocked aiokafka"""

    @pytest.fixture
    def mock_aiokafka_producer(self) -> AsyncMock:
        """Create a mock AIOKafkaProducer"""
        mock = AsyncMock()
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.send_and_wait = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_producer_initialization(self) -> None:
        """Test producer client initialization"""
        producer = StreamProducerClient(
            bootstrap_servers="redpanda:9092",
            topic="wikibase.entity_change",
        )
        assert producer.bootstrap_servers == "redpanda:9092"
        assert producer.topic == "wikibase.entity_change"
        assert producer.producer is None

    @pytest.mark.asyncio
    async def test_producer_start_creates_producer(
        self, mock_aiokafka_producer: AsyncMock
    ) -> None:
        """Test that start() creates the underlying producer"""
        with patch(
            "models.infrastructure.stream.producer.AIOKafkaProducer",
            return_value=mock_aiokafka_producer,
        ):
            producer = StreamProducerClient(
                bootstrap_servers="redpanda:9092",
                topic="wikibase.entity_change",
            )
            await producer.start()
            assert producer.producer is not None
            mock_aiokafka_producer.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_producer_stop(self, mock_aiokafka_producer: AsyncMock) -> None:
        """Test that stop() closes the producer"""
        with patch(
            "models.infrastructure.stream.producer.AIOKafkaProducer",
            return_value=mock_aiokafka_producer,
        ):
            producer = StreamProducerClient(
                bootstrap_servers="redpanda:9092",
                topic="wikibase.entity_change",
            )
            producer.producer = mock_aiokafka_producer
            await producer.stop()
            assert producer.producer is None
            mock_aiokafka_producer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_producer_publish_success(
        self, mock_aiokafka_producer: AsyncMock
    ) -> None:
        """Test successful event publishing"""
        producer = StreamProducerClient(
            bootstrap_servers="redpanda:9092",
            topic="wikibase.entity_change",
        )
        producer.producer = mock_aiokafka_producer

        event = EntityChangeEvent(
            entity_id="Q888888",
            revision_id=101,
            change_type=ChangeType.CREATION,
            changed_at=datetime(2026, 1, 8, 20, 0, 0, tzinfo=timezone.utc),
        )
        await producer.publish_change(event)

        mock_aiokafka_producer.send_and_wait.assert_called_once_with(
            topic="wikibase.entity_change",
            key="Q888888",
            value=event,
        )

    @pytest.mark.asyncio
    async def test_producer_publish_uses_entity_id_as_key(
        self, mock_aiokafka_producer: AsyncMock
    ) -> None:
        """Test that entity_id is used as partition key"""
        producer = StreamProducerClient(
            bootstrap_servers="redpanda:9092",
            topic="wikibase.entity_change",
        )
        producer.producer = mock_aiokafka_producer

        event = EntityChangeEvent(
            id="Q888889",
            rev=102,
            type=ChangeType.EDIT,
            at=datetime(2026, 1, 8, 20, 0, 0, tzinfo=timezone.utc),
        )
        await producer.publish_change(event)

        call_kwargs = mock_aiokafka_producer.send_and_wait.call_args
        assert call_kwargs.kwargs["key"] == "Q888889"

    @pytest.mark.asyncio
    async def test_producer_publish_without_initialization(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test graceful handling when producer not started"""
        producer = StreamProducerClient(
            bootstrap_servers="redpanda:9092",
            topic="wikibase.entity_change",
        )
        assert producer.producer is None

        event = EntityChangeEvent(
            id="Q888888",
            rev=101,
            type=ChangeType.CREATION,
            at=datetime(2026, 1, 8, 20, 0, 0, tzinfo=timezone.utc),
        )
        await producer.publish_change(event)
        assert "Kafka producer not started" in caplog.text

    @pytest.mark.asyncio
    async def test_producer_publish_handles_error(
        self, mock_aiokafka_producer: AsyncMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test graceful handling when publish fails"""
        mock_aiokafka_producer.send_and_wait.side_effect = Exception(
            "Kafka broker unavailable"
        )

        producer = StreamProducerClient(
            bootstrap_servers="redpanda:9092",
            topic="wikibase.entity_change",
        )
        producer.producer = mock_aiokafka_producer

        event = EntityChangeEvent(
            id="Q888888",
            rev=101,
            type=ChangeType.CREATION,
            at=datetime(2026, 1, 8, 20, 0, 0, tzinfo=timezone.utc),
        )
        await producer.publish_change(event)
        assert "Failed to publish event" in caplog.text

    @pytest.mark.asyncio
    async def test_producer_publish_multiple_events(
        self, mock_aiokafka_producer: AsyncMock
    ) -> None:
        """Test publishing multiple events in sequence"""
        producer = StreamProducerClient(
            bootstrap_servers="redpanda:9092",
            topic="wikibase.entity_change",
        )
        producer.producer = mock_aiokafka_producer

        events = [
            EntityChangeEvent(
                id="Q888888",
                rev=i,
                type=ChangeType.EDIT,
                at=datetime(2026, 1, 8, 20, i, 0, tzinfo=timezone.utc),
            )
            for i in range(1, 4)
        ]

        for event in events:
            await producer.publish_change(event)

        assert mock_aiokafka_producer.send_and_wait.call_count == 3

    @pytest.mark.asyncio
    async def test_producer_start_idempotent(
        self, mock_aiokafka_producer: AsyncMock
    ) -> None:
        """Test that start() can be called multiple times safely"""
        with patch(
            "models.infrastructure.stream.producer.AIOKafkaProducer",
            return_value=mock_aiokafka_producer,
        ):
            producer = StreamProducerClient(
                bootstrap_servers="redpanda:9092",
                topic="wikibase.entity_change",
            )
            await producer.start()
            await producer.start()
            await producer.start()

            assert producer.producer is not None
            assert mock_aiokafka_producer.start.call_count == 1

    @pytest.mark.asyncio
    async def test_producer_stop_idempotent(
        self, mock_aiokafka_producer: AsyncMock
    ) -> None:
        """Test that stop() can be called multiple times safely"""
        producer = StreamProducerClient(
            bootstrap_servers="redpanda:9092",
            topic="wikibase.entity_change",
        )
        producer.producer = mock_aiokafka_producer

        await producer.stop()
        await producer.stop()

        assert producer.producer is None
        assert mock_aiokafka_producer.stop.call_count == 1

    @pytest.mark.asyncio
    async def test_producer_lifecycle(self, mock_aiokafka_producer: AsyncMock) -> None:
        """Test complete start -> publish -> stop lifecycle"""
        with patch(
            "models.infrastructure.stream.producer.AIOKafkaProducer",
            return_value=mock_aiokafka_producer,
        ):
            producer = StreamProducerClient(
                bootstrap_servers="redpanda:9092",
                topic="wikibase.entity_change",
            )

            await producer.start()
            assert producer.producer is not None

            event = EntityChangeEvent(
                id="Q888888",
                rev=101,
                type=ChangeType.CREATION,
                at=datetime(2026, 1, 8, 20, 0, 0, tzinfo=timezone.utc),
            )
            await producer.publish_change(event)
            mock_aiokafka_producer.send_and_wait.assert_called_once()

            await producer.stop()
            assert producer.producer is None
