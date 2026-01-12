"""Watchlist consumer worker for processing entity change events and notifying users."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from models.config.settings import settings
from models.infrastructure.stream.consumer import Consumer
from models.infrastructure.vitess_client import VitessClient
from models.watchlist import WatchlistEntry


class WatchlistConsumerWorker:
    """Worker that consumes entity change events and creates notifications for watchers."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.consumer: Consumer | None = None
        self.vitess_client: VitessClient | None = None

    @asynccontextmanager
    async def lifespan(self):
        """Lifespan context manager for startup/shutdown."""
        try:
            # Initialize clients
            s3_config = settings.to_s3_config()
            vitess_config = settings.to_vitess_config()
            kafka_brokers = settings.kafka_brokers
            kafka_topic = settings.kafka_topic

            self.vitess_client = VitessClient(vitess_config)

            if kafka_brokers and kafka_topic:
                self.consumer = Consumer(
                    brokers=kafka_brokers,
                    topic=kafka_topic,
                    group_id="watchlist-consumer",
                )
                await self.consumer.start()
                self.logger.info("Watchlist consumer started")
            else:
                self.logger.warning("Kafka config missing, consumer not started")

            yield
        except Exception as e:
            self.logger.error(f"Failed to start watchlist consumer: {e}")
            raise
        finally:
            if self.consumer:
                await self.consumer.stop()
                self.logger.info("Watchlist consumer stopped")

    async def process_message(self, message: dict[str, Any]) -> None:
        """Process a single entity change event message."""
        try:
            # Parse the event
            entity_id = message.get("entity_id")
            revision_id = message.get("revision_id")
            change_type = message.get("change_type")
            changed_properties = message.get("changed_properties")  # Optional

            if not entity_id or not revision_id or not change_type:
                self.logger.warning(
                    f"Invalid event message: missing required fields {message}"
                )
                return

            self.logger.info(
                f"Processing event: {entity_id} {change_type} rev {revision_id}"
            )

            # Get watchers for this entity
            watchers = self.vitess_client.watchlist_repository.get_watchers_for_entity(
                entity_id
            )

            notifications_created = 0
            for watcher in watchers:
                user_id = watcher["user_id"]
                watched_properties = watcher["properties"]

                # Check if this change matches the watch
                should_notify = self._should_notify(
                    watched_properties, changed_properties
                )

                if should_notify:
                    # Create notification (cleanup worker handles limits)
                    await self._create_notification(
                        user_id=user_id,
                        entity_id=entity_id,
                        revision_id=revision_id,
                        change_type=change_type,
                        changed_properties=changed_properties,
                        event_timestamp=message.get("changed_at"),
                    )
                    notifications_created += 1

            self.logger.info(
                f"Created {notifications_created} notifications for {entity_id}"
            )

        except Exception as e:
            self.logger.error(f"Error processing message {message}: {e}")

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
        event_timestamp: str | None,
    ) -> None:
        """Create a notification record in the database."""
        # For now, insert into user_notifications table
        # In a real system, this might trigger email/webhook
        with self.vitess_client.get_connection() as conn:
            with conn.cursor() as cursor:
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
                self.logger.debug(
                    f"Created notification for user {user_id} on {entity_id}"
                )


async def main() -> None:
    """Main entry point for the watchlist consumer worker."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = WatchlistConsumerWorker()

    async with worker.lifespan():
        if worker.consumer:
            self.logger.info("Starting message consumption loop")
            async for message in worker.consumer.consume():
                await worker.process_message(message)
        else:
            self.logger.warning("No consumer available, exiting")


if __name__ == "__main__":
    asyncio.run(main())
