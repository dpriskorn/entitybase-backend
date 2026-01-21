"""Kafka streaming infrastructure for publishing change events."""

import logging
from typing import Any

from aiokafka import AIOKafkaProducer  # type: ignore[import-untyped]

from models.infrastructure.client import Client
from models.infrastructure.stream.config import StreamConfig

logger = logging.getLogger(__name__)


class StreamProducerClient(Client):
    """Kafka producer client for publishing events."""

    producer: AIOKafkaProducer | None = None
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, config: StreamConfig) -> None:
        super().__init__(config=config)
        self.start()

    async def start(self) -> None:
        """Start the Kafka producer."""
        if self.producer is not None:
            return
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            value_serializer=lambda v: v.model_dump_json(by_alias=True).encode("utf-8"),
        )
        await self.producer.start()
        logger.info(f"Started Kafka producer for topic {self.topic}")

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            self.producer = None
            logger.info("Stopped Kafka producer")

    async def publish_change(self, event: Any) -> None:
        """Publish an event to Kafka."""
        if not self.producer:
            logger.warning("Kafka producer not started, skipping event publish")
            return

        try:
            key = getattr(event, "entity_id", getattr(event, "hash", None))
            if key is None:
                logger.error(f"Event {event} has no key field")
                return

            await self.producer.send_and_wait(
                topic=self.config.topic,
                key=str(key),
                value=event,
            )
            logger.debug(f"Published event: {event}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
