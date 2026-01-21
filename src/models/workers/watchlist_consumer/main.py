"""Watchlist consumer worker for processing entity change events and notifying users."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from models.config.settings import settings
from models.infrastructure.stream.consumer import Consumer, EntityChangeEvent
from models.infrastructure.vitess.client import VitessClient

logger = logging.getLogger(__name__)


class WatchlistConsumerWorker:
    """Worker that consumes entity change events and creates notifications for watchers."""

    def __init__(self) -> None:
        logger = logging.getLogger(__name__)
        self.consumer: Consumer | None = None
        self.vitess_client | None = None

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None, None]:
        """Lifespan context manager for startup/shutdown."""
        try:
            # Initialize clients
            s3_config = settings.to_s3_config()
            vitess_config = settings.to_vitess_config()
            kafka_brokers = (
                [b.strip() for b in settings.kafka_brokers.split(",")]
                if settings.kafka_brokers
                else []
            )
            kafka_topic = settings.kafka_entitychange_json_topic

            self.vitess_client = VitessClient(vitess_config)

            if kafka_brokers and kafka_topic:
                self.consumer = Consumer(
                    brokers=kafka_brokers,
                    topic=kafka_topic,
                    group_id="watchlist-consumer",
                )
                assert self.consumer is not None
                await self.consumer.start()
                logger.info("Watchlist consumer started")
            else:
                logger.warning("Kafka config missing, consumer not started")

            yield
        except Exception as e:
            logger.error(f"Failed to start watchlist consumer: {e}")
            raise
        finally:
            if self.consumer:
                await self.consumer.stop()
                logger.info("Watchlist consumer stopped")

    async def run(self) -> None:
        """Run the consumer loop."""
        if not self.consumer:
            logger.warning("Consumer not started, cannot run")
            return

        try:
            async for event in self.consumer.consume_events():
                await self.process_message(event)
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            raise

    async def process_message(self, message: EntityChangeEvent) -> None:
        """Process a single entity change event message."""
        try:
            # Parse the event
            entity_id = message.entity_id
            revision_id = message.revision_id
            change_type = message.type

            if not entity_id or not revision_id or not change_type:
                logger.warning(
                    f"Invalid event message: missing required fields {message}"
                )
                return

            logger.info(
                f"Processing event: {entity_id} {change_type} rev {revision_id}"
            )

            # Get watchers for this entity
            assert self.vitess_client is not None
            watchers = self.vitess_client.watchlist_repository.get_watchers_for_entity(
                entity_id
            )

            notifications_created = 0
            for watcher in watchers:
                user_id = watcher["user_id"]
                # For now, notify on any change (simplified)
                should_notify = True

                if should_notify:
                    # Create notification (cleanup worker handles limits)
                    await self._create_notification(
                        user_id=user_id,
                        entity_id=entity_id,
                        revision_id=revision_id,
                        change_type=change_type,
                        changed_properties=[],  # TODO: add to event model
                        event_timestamp=message.timestamp,
                    )
                    notifications_created += 1

            logger.info(
                f"Created {notifications_created} notifications for {entity_id}"
            )

        except Exception as e:
            logger.error(f"Error processing message {message}: {e}")

    def _should_notify(
        self, watched_properties: list[str] | None, changed_properties: list[str] | None
    ) -> bool:
        """Determine if user should be notified based on watched vs changed properties."""
        if watched_properties is None:
            # Watching entire entity
            return True

        if changed_properties is None:
            # No specific properties changed info, but user watches specific props - notify to be safe
            return True

        # Check if any changed property is watched
        return any(prop in watched_properties for prop in changed_properties)

    async def _create_notification(
        self,
        user_id: int,
        entity_id: str,
        revision_id: int,
        change_type: str,
        changed_properties: list[str] | None,
        event_timestamp: str = "",
    ) -> None:
        """Create a notification record in the database."""
        # For now, insert into user_notifications table
        # In a real system, this might trigger email/webhook
        assert self.vitess_client is not None
        with self.vitess_client.connection_manager.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO user_notifications
                (user_id, entity_id, revision_id, change_type, changed_properties, event_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    entity_id,
                    revision_id,
                    change_type,
                    json.dumps(changed_properties) if changed_properties else None,
                    event_timestamp,
                ),
            )
            logger.debug(f"Created notification for user {user_id} on {entity_id}")


async def main() -> None:
    """Main entry point for the watchlist consumer worker."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    worker = WatchlistConsumerWorker()

    # noinspection PyArgumentList
    async with worker.lifespan():
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
