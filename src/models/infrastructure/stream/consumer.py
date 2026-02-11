"""Kafka consumer for Wikibase entity change events."""

import json
import logging
from typing import AsyncGenerator, Any

from aiokafka import AIOKafkaConsumer  # type: ignore[import-untyped]
from pydantic import ConfigDict, Field

from models.data.config.stream_consumer import StreamConsumerConfig
from models.data.infrastructure.stream.consumer import EntityChangeEventData
from models.infrastructure.client import Client

logger = logging.getLogger(__name__)


class StreamConsumerClient(Client):
    """Kafka consumer for entity change events.
    You have to run start() after instantiation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: StreamConsumerConfig

    consumer: AIOKafkaConsumer | None = Field(default=None)
    bootstrap_servers: str = Field(default="", init=False)

    @property
    def healthy_connection(self) -> bool:
        """Check if the consumer has a healthy connection."""
        return self.consumer is not None

    @property
    def brokers(self) -> list[str]:
        """Get brokers."""
        return self.config.brokers

    @property
    def topic(self) -> str:
        """Get topic."""
        return self.config.topic

    @property
    def group_id(self) -> str:
        """Get group_id."""
        return self.config.group_id

    def model_post_init(self, context: Any) -> None:
        self.bootstrap_servers = ",".join(self.config.brokers)

    async def start(self) -> None:
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            self.config.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.config.group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset=self.config.auto_offset_reset,
        )
        await self.consumer.start()
        logger.info(f"Started Kafka consumer for topic {self.config.topic}")

    async def stop(self) -> None:
        """Stop the Kafka consumer."""
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
            logger.info("Stopped Kafka consumer")

    async def consume_events(self) -> AsyncGenerator[EntityChangeEventData, None]:
        """Consume entity change events."""
        if not self.consumer:
            raise RuntimeError("Consumer not started")

        try:
            async for message in self.consumer:
                event_data = message.value
                event = EntityChangeEventData(**event_data)
                logger.debug(f"Consumed event: {event}")
                yield event
        except Exception as e:
            logger.error(f"Error consuming events: {e}")
            raise
