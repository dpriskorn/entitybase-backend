import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, "src")

from models.infrastructure.stream.consumer import EntityChangeEvent
from models.workers.watchlist_consumer.main import WatchlistConsumerWorker


class TestWatchlistConsumerIntegration:
    """Integration tests for WatchlistConsumerWorker with mocked dependencies"""

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

    @pytest.mark.asyncio
    async def test_full_consumer_workflow_with_multiple_events(
        self, mock_vitess_client: MagicMock, mock_consumer: AsyncMock
    ) -> None:
        """Test the complete consumer workflow processing multiple events"""
        worker = WatchlistConsumerWorker()

        # Mock settings
        with (
            patch("models.workers.watchlist_consumer.main.settings") as mock_settings,
            patch(
                "models.workers.watchlist_consumer.main.VitessClient",
                return_value=mock_vitess_client,
            ),
            patch(
                "models.workers.watchlist_consumer.main.Consumer",
                return_value=mock_consumer,
            ),
        ):
            mock_settings.to_s3_config.return_value = {}
            mock_settings.to_vitess_config.return_value = {}
            mock_settings.kafka_brokers = "localhost:9092"
            mock_settings.kafka_topic = "wikibase-entity-changes"

            # Events to process
            events = [
                EntityChangeEvent(
                    entity_id="Q42",
                    revision_id=123,
                    timestamp="2023-01-01T12:00:00Z",
                    author_id="user123",
                    type="edit",
                ),
                EntityChangeEvent(
                    entity_id="Q43",
                    revision_id=124,
                    timestamp="2023-01-01T12:01:00Z",
                    author_id="user124",
                    type="create",
                ),
                EntityChangeEvent(
                    entity_id="Q42",
                    revision_id=125,
                    timestamp="2023-01-01T12:02:00Z",
                    author_id="user125",
                    type="delete",
                ),
            ]

            # Mock watchers for each entity
            mock_vitess_client.watchlist_repository.get_watchers_for_entity.side_effect = [
                [{"user_id": 1}, {"user_id": 2}],  # Q42 edit: 2 watchers
                [{"user_id": 3}],  # Q43 create: 1 watcher
                [],  # Q42 delete: no watchers
            ]

            # Mock the consume_events generator
            async def mock_consume_events():
                for event in events:
                    yield event

            mock_consumer.consume_events = mock_consume_events

            # Run the lifespan and worker
            async with worker.lifespan():
                await worker.run()

            # Verify consumer lifecycle
            mock_consumer.start.assert_called_once()
            mock_consumer.stop.assert_called_once()

            # Verify watchers were queried for each event
            assert (
                mock_vitess_client.watchlist_repository.get_watchers_for_entity.call_count
                == 3
            )
            mock_vitess_client.watchlist_repository.get_watchers_for_entity.assert_any_call(
                "Q42"
            )
            mock_vitess_client.watchlist_repository.get_watchers_for_entity.assert_any_call(
                "Q43"
            )

            # Verify notifications were created (2 for first event, 1 for second, 0 for third)
            expected_notifications = 3
            assert (
                mock_vitess_client.get_connection.call_count == expected_notifications
            )

    @pytest.mark.asyncio
    async def test_consumer_error_handling(
        self, mock_vitess_client: MagicMock, mock_consumer: AsyncMock
    ) -> None:
        """Test consumer handles errors gracefully"""
        worker = WatchlistConsumerWorker()

        with (
            patch("models.workers.watchlist_consumer.main.settings") as mock_settings,
            patch(
                "models.workers.watchlist_consumer.main.VitessClient",
                return_value=mock_vitess_client,
            ),
            patch(
                "models.workers.watchlist_consumer.main.Consumer",
                return_value=mock_consumer,
            ),
        ):
            mock_settings.to_s3_config.return_value = {}
            mock_settings.to_vitess_config.return_value = {}
            mock_settings.kafka_brokers = "localhost:9092"
            mock_settings.kafka_topic = "wikibase-entity-changes"

            # Mock an event that causes processing error
            event = EntityChangeEvent(
                entity_id="Q42",
                revision_id=123,
                timestamp="2023-01-01T12:00:00Z",
                author_id="user123",
                type="edit",
            )

            # Mock watchers to raise an exception
            mock_vitess_client.watchlist_repository.get_watchers_for_entity.side_effect = Exception(
                "DB error"
            )

            async def mock_consume_events():
                yield event

            mock_consumer.consume_events = mock_consume_events

            # Run and expect no crash (error logged)
            async with worker.lifespan():
                await worker.run()

            # Should still have started/stopped
            mock_consumer.start.assert_called_once()
            mock_consumer.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_consumer_without_kafka_config(
        self, mock_vitess_client: MagicMock
    ) -> None:
        """Test consumer runs without Kafka (should do nothing)"""
        worker = WatchlistConsumerWorker()

        with (
            patch("models.workers.watchlist_consumer.main.settings") as mock_settings,
            patch(
                "models.workers.watchlist_consumer.main.VitessClient",
                return_value=mock_vitess_client,
            ),
        ):
            mock_settings.to_s3_config.return_value = {}
            mock_settings.to_vitess_config.return_value = {}
            mock_settings.kafka_brokers = None
            mock_settings.kafka_topic = None

            async with worker.lifespan():
                await worker.run()

            # No consumer should be created
            assert worker.consumer is None

    @pytest.mark.asyncio
    async def test_notification_creation_with_properties(
        self, mock_vitess_client: MagicMock, mock_consumer: AsyncMock
    ) -> None:
        """Test notification creation includes changed properties"""
        worker = WatchlistConsumerWorker()

        with (
            patch("models.workers.watchlist_consumer.main.settings") as mock_settings,
            patch(
                "models.workers.watchlist_consumer.main.VitessClient",
                return_value=mock_vitess_client,
            ),
            patch(
                "models.workers.watchlist_consumer.main.Consumer",
                return_value=mock_consumer,
            ),
        ):
            mock_settings.to_s3_config.return_value = {}
            mock_settings.to_vitess_config.return_value = {}
            mock_settings.kafka_brokers = "localhost:9092"
            mock_settings.kafka_topic = "wikibase-entity-changes"

            event = EntityChangeEvent(
                entity_id="Q42",
                revision_id=123,
                timestamp="2023-01-01T12:00:00Z",
                author_id="user123",
                type="edit",
            )

            mock_vitess_client.watchlist_repository.get_watchers_for_entity.return_value = [
                {"user_id": 1}
            ]

            async def mock_consume_events():
                yield event

            mock_consumer.consume_events = mock_consume_events

            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_vitess_client.get_connection.return_value.__enter__.return_value = (
                mock_connection
            )
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            async with worker.lifespan():
                await worker.run()

            # Verify the notification insert includes changed_properties
            mock_cursor.execute.assert_called_once()
            args, kwargs = mock_cursor.execute.call_args
            query = args[0]
            params = args[1]

            assert "INSERT INTO user_notifications" in query
            assert params[4] is None  # changed_properties (empty list becomes None)
