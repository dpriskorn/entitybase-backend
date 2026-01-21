"""Kafka consumer for Wikibase entity change events."""

import json
import logging
from typing import AsyncGenerator

from aiokafka import AIOKafkaConsumer  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class EntityChangeEvent(BaseModel):
    """Model for entity change events."""

    model_config = ConfigDict(populate_by_name=True)

    entity_id: str
    revision_id: int
    timestamp: str
    user_id: str
    type: str


class Consumer(BaseModel):
    """Kafka consumer for entity change events."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    brokers: list[str]
    topic: str = "wikibase-entity-changes"
    group_id: str = "watchlist-consumer"
    consumer: AIOKafkaConsumer | None = Field(default=None)
    bootstrap_servers: str = Field(default="", init=False)

    def model_post_init(self, context) -> None:
        self.bootstrap_servers = ",".join(self.brokers)

    async def start(self) -> None:
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
        )
        await self.consumer.start()
        logger.info(f"Started Kafka consumer for topic {self.topic}")

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Stopped Kafka consumer")

    async def consume_events(self) -> AsyncGenerator[EntityChangeEvent, None]:
        """Consume entity change events."""
        if not self.consumer:
            raise RuntimeError("Consumer not started")

        try:
            async for message in self.consumer:
                event_data = message.value
                event = EntityChangeEvent(**event_data)
                logger.debug(f"Consumed event: {event}")
                yield event
        except Exception as e:
            logger.error(f"Error consuming events: {e}")
            raise
