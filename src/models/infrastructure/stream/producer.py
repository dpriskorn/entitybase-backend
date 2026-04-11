"""Kafka streaming infrastructure for publishing change events."""

import logging
from typing import Any

from aiokafka import AIOKafkaProducer  # type: ignore[import-untyped]

from models.data.config.stream import StreamConfig
from models.infrastructure.client import Client

logger = logging.getLogger(__name__)


class StreamProducerClient(Client):
    """Kafka producer client for publishing events.
    Producer starts lazily on first publish."""

    config: StreamConfig
    producer: AIOKafkaProducer | None = None
    model_config = {"arbitrary_types_allowed": True}

    @property
    def healthy_connection(self) -> bool:
        """Check if the producer has a healthy connection."""
        return self.producer is not None and not self.producer._closed

    async def start(self) -> None:
        """Start the Kafka producer."""
        if self.producer is not None:
            return
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            value_serializer=lambda v: v.model_dump_json(by_alias=True).encode("utf-8"),
        )
        await self.producer.start()
        logger.info(f"Started Kafka producer for topic {self.config.topic}")

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            self.producer = None
            logger.info("Stopped Kafka producer")

    async def publish(self, event: Any) -> None:
        """Publish an event to Kafka."""
        from models.config.settings import settings

        if not self.config.bootstrap_servers or not settings.streaming_enabled:
            logger.debug(
                f"Streaming disabled or not configured for topic {self.config.topic}, "
                "skipping publish"
            )
            return
        if not self.producer:
            logger.info(
                f"Producer not started, starting now for topic {self.config.topic}"
            )
            await self.start()

        try:
            if self.producer is None:
                logger.error("Producer not initialized")
                return
            key = getattr(event, "entity_id", None) or getattr(event, "hash", None)
            if key is None:
                logger.error(f"Event {event} has no key field")
                return

            logger.info(
                f"Sending event to Kafka: topic={self.config.topic}, "
                f"key={key}, event_type={type(event).__name__}"
            )
            await self.producer.send_and_wait(
                topic=self.config.topic,
                key=str(key).encode("utf-8"),
                value=event,
            )
            logger.info(
                f"Successfully sent event to Kafka: topic={self.config.topic}, key={key}"
            )
        except Exception as e:
            logger.error(
                f"Failed to publish event to Kafka: {type(e).__name__}: {e}",
                exc_info=True,
            )
