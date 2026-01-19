import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.infrastructure.stream.consumer import EntityChangeEvent
from models.workers.watchlist_consumer.main import WatchlistConsumerWorker


class TestWatchlistConsumerWorker:
    """Unit tests for WatchlistConsumerWorker"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.watchlist_repository = MagicMock()
        client.get_connection.return_value.__enter__.return_value.cursor.return_value = MagicMock()
        return client

    @pytest.fixture
    def mock_consumer(self) -> AsyncMock:
        """Mock Kafka consumer"""
        consumer = AsyncMock()
        consumer.start = AsyncMock()
        consumer.stop = AsyncMock()
        return consumer

    @pytest.fixture
    def worker(self) -> WatchlistConsumerWorker:
        """Create worker instance"""
        return WatchlistConsumerWorker()

    @pytest.mark.asyncio
    async def test_lifespan_with_kafka_config(
        self,
        worker: WatchlistConsumerWorker,
        mock_vitess_client: MagicMock,
        mock_consumer: AsyncMock,
    ) -> None:
        """Test lifespan context manager with Kafka config"""
        with (
            patch("models.workers.watchlist_consumer.main.settings") as mock_settings,
            patch(
                "models.workers.watchlist_consumer.main.VitessClient"
            ) as mock_vitess_class,
            patch(
                "models.workers.watchlist_consumer.main.Consumer",
                return_value=mock_consumer,
            ) as mock_consumer_class,
        ):
            mock_settings.to_s3_config.return_value = {}
            mock_settings.to_vitess_config.return_value = {}
            mock_settings.kafka_brokers = "localhost:9092"
            mock_settings.kafka_topic = "test-topic"
            mock_vitess_class.return_value = mock_vitess_client

            async with worker.lifespan():
                assert worker.consumer == mock_consumer
                assert worker.vitess_client == mock_vitess_client

            mock_consumer.start.assert_called_once()
            mock_consumer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_without_kafka_config(
        self, worker: WatchlistConsumerWorker, mock_vitess_client: MagicMock
    ) -> None:
        """Test lifespan context manager without Kafka config"""
        with (
            patch("models.workers.watchlist_consumer.main.settings") as mock_settings,
            patch(
                "models.workers.watchlist_consumer.main.VitessClient"
            ) as mock_vitess_class,
        ):
            mock_settings.to_s3_config.return_value = {}
            mock_settings.to_vitess_config.return_value = {}
            mock_settings.kafka_brokers = None
            mock_settings.kafka_topic = None
            mock_vitess_class.return_value = mock_vitess_client

            async with worker.lifespan():
                assert worker.consumer is None
                assert worker.vitess_client == mock_vitess_client

    @pytest.mark.asyncio
    async def test_run_with_no_consumer(self, worker: WatchlistConsumerWorker) -> None:
        """Test run method when no consumer is configured"""
        worker.consumer = None

        await worker.run()  # Should not raise or do anything

    @pytest.mark.asyncio
    async def test_run_with_consumer(
        self,
        worker: WatchlistConsumerWorker,
        mock_vitess_client: MagicMock,
        mock_consumer: AsyncMock,
    ) -> None:
        """Test run method with consumer"""
        worker.consumer = mock_consumer
        worker.vitess_client = mock_vitess_client

        # Mock the consume_events generator
        event1 = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            timestamp="2023-01-01T12:00:00Z",
            author_id="user123",
            type="edit",
        )
        event2 = EntityChangeEvent(
            entity_id="Q43",
            revision_id=124,
            timestamp="2023-01-01T12:01:00Z",
            author_id="user124",
            type="create",
        )

        async def mock_consume_events():
            yield event1
            yield event2

        mock_consumer.consume_events = mock_consume_events

        # Mock watchers
        mock_vitess_client.watchlist_repository.get_watchers_for_entity.side_effect = [
            [{"user_id": 1}],  # For Q42
            [{"user_id": 2}, {"user_id": 3}],  # For Q43
        ]

        # Mock the process_message to avoid database calls
        with patch.object(
            worker, "process_message", new_callable=AsyncMock
        ) as mock_process:
            await worker.run()

            # Should have processed two messages
            assert mock_process.call_count == 2
            mock_process.assert_any_call(event1)
            mock_process.assert_any_call(event2)

    @pytest.mark.asyncio
    async def test_process_message_with_watchers(
        self, worker: WatchlistConsumerWorker, mock_vitess_client: MagicMock
    ) -> None:
        """Test processing a message with watchers"""
        worker.vitess_client = mock_vitess_client

        event = EntityChangeEvent(
            entity_id="Q42",
            revision_id=123,
            timestamp="2023-01-01T12:00:00Z",
            author_id="user123",
            type="edit",
        )

        # Mock watchers
        mock_vitess_client.watchlist_repository.get_watchers_for_entity.return_value = [
            {"user_id": 1, "watched_properties": None},  # Watching entire entity
            {
                "user_id": 2,
                "watched_properties": ["P31"],
            },  # Watching specific properties
        ]

        # Mock the _create_notification method
        with patch.object(
            worker, "_create_notification", new_callable=AsyncMock
        ) as mock_create:
            await worker.process_message(event)

            # Should create 2 notifications
            assert mock_create.call_count == 2
            mock_create.assert_any_call(
                user_id=1,
                entity_id="Q42",
                revision_id=123,
                change_type="edit",
                changed_properties=[],
                event_timestamp="2023-01-01T12:00:00Z",
            )
            mock_create.assert_any_call(
                user_id=2,
                entity_id="Q42",
                revision_id=123,
                change_type="edit",
                changed_properties=[],
                event_timestamp="2023-01-01T12:00:00Z",
            )

    @pytest.mark.asyncio
    async def test_process_message_invalid_event(
        self, worker: WatchlistConsumerWorker, mock_vitess_client: MagicMock
    ) -> None:
        """Test processing an invalid message"""
        worker.vitess_client = mock_vitess_client

        # Invalid event missing required fields
        event = EntityChangeEvent(
            entity_id="",  # Invalid
            revision_id=123,
            timestamp="2023-01-01T12:00:00Z",
            author_id="user123",
            type="edit",
        )

        await worker.process_message(event)

        # Should not call get_watchers or create notifications
        mock_vitess_client.watchlist_repository.get_watchers_for_entity.assert_not_called()

    def test_should_notify_watching_all(self) -> None:
        """Test notification logic when watching entire entity"""
        worker = WatchlistConsumerWorker()

        assert worker._should_notify(None, None) is True
        assert worker._should_notify(None, ["P31"]) is True

    def test_should_notify_watching_specific(self) -> None:
        """Test notification logic when watching specific properties"""
        worker = WatchlistConsumerWorker()

        # No changed properties info, but watching specific - notify to be safe
        assert worker._should_notify(["P31"], None) is True

        # Changed properties include watched
        assert worker._should_notify(["P31"], ["P31", "P32"]) is True

        # Changed properties don't include watched
        assert worker._should_notify(["P31"], ["P32"]) is False

        # No overlap
        assert worker._should_notify(["P31"], []) is False

    @pytest.mark.asyncio
    async def test_create_notification(
        self, worker: WatchlistConsumerWorker, mock_vitess_client: MagicMock
    ) -> None:
        """Test creating a notification record"""
        worker.vitess_client = mock_vitess_client

        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.get_connection.return_value.__enter__.return_value = (
            mock_connection
        )
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        await worker._create_notification(
            user_id=123,
            entity_id="Q42",
            revision_id=456,
            change_type="edit",
            changed_properties=["P31"],
            event_timestamp="2023-01-01T12:00:00Z",
        )

        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        assert "INSERT INTO user_notifications" in args[0]
        assert args[1] == (123, "Q42", 456, "edit", '["P31"]', "2023-01-01T12:00:00Z")
