"""Unit tests for producer."""

from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.stream.event import EntityChangeEvent
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.config.stream import StreamConfig


class TestStreamProducerClient:
    """Unit tests for StreamProducerClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = StreamConfig(bootstrap_servers=["localhost:9092"], topic="test-topic")
        self.client = StreamProducerClient(config=self.config)

    @pytest.mark.asyncio
    async def test_start_producer(self):
        """Test starting the Kafka producer."""
        with patch('models.infrastructure.stream.producer.AIOKafkaProducer') as mock_producer_class:
            mock_producer = AsyncMock()
            mock_producer_class.return_value = mock_producer

            await self.client.start()

            mock_producer_class.assert_called_once_with(
                bootstrap_servers=["localhost:9092"],
                value_serializer=ANY,
            )
            mock_producer.start.assert_called_once()
            assert self.client.producer == mock_producer

    @pytest.mark.asyncio
    async def test_start_producer_already_started(self):
        """Test starting producer when already started."""
        self.client.producer = MagicMock()

        await self.client.start()

        # Should not create new producer
        assert self.client.producer is not None

    @pytest.mark.asyncio
    async def test_stop_producer(self):
        """Test stopping the Kafka producer."""
        mock_producer = AsyncMock()
        self.client.producer = mock_producer

        await self.client.stop()

        mock_producer.stop.assert_called_once()
        assert self.client.producer is None

    @pytest.mark.asyncio
    async def test_stop_producer_no_producer(self):
        """Test stopping when no producer exists."""
        self.client.producer = None

        await self.client.stop()

        # Should not raise error
        assert self.client.producer is None

    @pytest.mark.asyncio
    async def test_publish_change_success_entity_event(self):
        """Test publishing entity change event successfully."""
        mock_producer = AsyncMock()
        self.client.producer = mock_producer

        event = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.EDIT,
            changed_at=MagicMock(),
        )

        await self.client.publish_change(event)

        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            key="Q42",
            value=event,
        )

    @pytest.mark.asyncio
    async def test_publish_change_success_endorse_event(self):
        """Test publishing endorse change event successfully."""
        mock_producer = AsyncMock()
        self.client.producer = mock_producer

        event = MagicMock()
        event.hash = "abc123"
        event.entity_id = None  # No entity_id, should use hash

        await self.client.publish_change(event)

        mock_producer.send_and_wait.assert_called_once_with(
            topic="test-topic",
            key="abc123",
            value=event,
        )

    @pytest.mark.asyncio
    @patch('models.infrastructure.stream.producer.AIOKafkaProducer')
    async def test_publish_change_no_producer(self, mock_producer_class):
        """Test publishing when producer is not started (lazy start)."""
        self.client.producer = None
        mock_producer = AsyncMock()
        mock_producer_class.return_value = mock_producer

        event = MagicMock()

        await self.client.publish_change(event)

        # Should start producer and publish
        mock_producer_class.assert_called_once()
        mock_producer.start.assert_called_once()
        mock_producer.send_and_wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_change_no_key(self):
        """Test publishing event with no key field."""
        mock_producer = AsyncMock()
        self.client.producer = mock_producer

        event = MagicMock()
        event.entity_id = None
        event.hash = None  # No key available

        await self.client.publish_change(event)

        # Should log error and return without publishing
        mock_producer.send_and_wait.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_change_send_error(self):
        """Test publishing when send_and_wait raises exception."""
        mock_producer = AsyncMock()
        mock_producer.send_and_wait.side_effect = Exception("Kafka error")
        self.client.producer = mock_producer

        event = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.EDIT,
            changed_at=MagicMock(),
        )

        await self.client.publish_change(event)

        # Should log error but not raise



    def test_value_serializer(self):
        """Test the value serializer function."""
        event = MagicMock()
        event.model_dump_json.return_value = '{"test": "data"}'

        serializer = lambda v: v.model_dump_json(by_alias=True).encode("utf-8")
        result = serializer(event)

        assert result == b'{"test": "data"}'
        event.model_dump_json.assert_called_once_with(by_alias=True)
