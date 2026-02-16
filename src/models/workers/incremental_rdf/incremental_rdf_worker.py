"""Incremental RDF worker for processing entity changes and generating RDF diffs."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Optional

from pydantic import Field

from models.config.settings import settings
from models.data.infrastructure.stream.consumer import EntityChangeEventData
from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.stream.consumer import StreamConsumerClient
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess.client import VitessClient
from models.internal_representation.entity_data import EntityData
from models.rdf_builder.incremental_updater import IncrementalRDFUpdater
from models.workers.worker import Worker
from models.workers.incremental_rdf.rdf_change_builder import RDFChangeEventBuilder

logger = logging.getLogger(__name__)


class IncrementalRDFWorker(Worker):
    """Worker that consumes entity change events and generates incremental RDF diffs.

    This worker:
    1. Consumes entity change events from entitybase.entity_change Kafka topic
    2. Looks up revision metadata in MySQL to get content hashes
    3. Fetches entity snapshots from S3 for both old and new revisions
    4. Computes RDF diffs using IncrementalRDFUpdater
    5. Publishes RDF change events to incremental_rdf_diff Kafka topic
    """

    vitess_client: Optional[VitessClient] = Field(default=None, exclude=True)
    s3_client: Optional[MyS3Client] = Field(default=None, exclude=True)
    consumer: Optional[StreamConsumerClient] = Field(default=None, exclude=True)
    producer: Optional[StreamProducerClient] = Field(default=None, exclude=True)
    worker_enabled: bool = Field(default=False, exclude=True)

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None, None]:
        """Lifespan context manager for startup/shutdown."""
        try:
            if not self.worker_enabled:
                logger.info("IncrementalRDFWorker disabled by configuration")
                yield
                return

            logger.info("Starting IncrementalRDFWorker")

            await self._initialize_clients()

            logger.info("IncrementalRDFWorker started successfully")

            yield
        except Exception as e:
            logger.error(f"Failed to start IncrementalRDFWorker: {e}")
            raise
        finally:
            await self._cleanup_clients()
            logger.info("IncrementalRDFWorker stopped")

    async def _initialize_clients(self) -> None:
        """Initialize Kafka consumer, producer, Vitess and S3 clients."""
        kafka_brokers = self._get_kafka_brokers()

        if kafka_brokers:
            await self._initialize_kafka(kafka_brokers)
        else:
            logger.warning(
                "Kafka not configured, worker will not be able to consume/produce events"
            )

        await self._initialize_storage_clients()

    def _get_kafka_brokers(self) -> list[str]:
        """Get Kafka brokers from settings."""
        if not settings.kafka_bootstrap_servers:
            return []
        return [
            b.strip() for b in settings.kafka_bootstrap_servers.split(",") if b.strip()
        ]

    async def _initialize_kafka(self, kafka_brokers: list[str]) -> None:
        """Initialize Kafka consumer and producer."""
        from models.data.config.stream_consumer import StreamConsumerConfig

        consumer_config = StreamConsumerConfig(
            brokers=kafka_brokers,
            topic=settings.kafka_entitychange_json_topic,
            group_id=settings.incremental_rdf_consumer_group,
        )
        self.consumer = StreamConsumerClient(config=consumer_config)
        await self.consumer.start()
        logger.info(
            f"Kafka consumer started: topic={settings.kafka_entitychange_json_topic}, "
            f"group={settings.incremental_rdf_consumer_group}"
        )

        producer_config = settings.get_incremental_rdf_stream_config
        self.producer = StreamProducerClient(config=producer_config)
        await self.producer.start()
        logger.info(
            f"Kafka producer started: topic={settings.kafka_incremental_rdf_topic}"
        )

    async def _initialize_storage_clients(self) -> None:
        """Initialize Vitess and S3 clients."""
        if not self.worker_enabled:
            return

        vitess_config = settings.get_vitess_config
        if vitess_config.host and vitess_config.port:
            self.vitess_client = VitessClient(config=vitess_config)
            logger.info("Vitess client initialized")
        else:
            logger.warning(
                "Vitess not configured, worker cannot fetch revision metadata"
            )

        s3_config = settings.get_s3_config
        if s3_config.endpoint:
            self.s3_client = MyS3Client(config=s3_config)
            logger.info("S3 client initialized")
        else:
            logger.warning("S3 not configured, worker cannot fetch entity snapshots")

    async def _cleanup_clients(self) -> None:
        """Clean up all clients."""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        if self.vitess_client:
            self.vitess_client.connection_manager.close()
        logger.debug("All clients cleaned up")

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

    async def process_message(self, message: EntityChangeEventData) -> None:
        """Process a single entity change event message."""
        try:
            entity_id = message.entity_id
            revision_id = message.revision_id
            from_revision_id = message.from_revision_id
            change_type = message.change_type

            if not entity_id or not revision_id:
                logger.warning(
                    f"Invalid event message: missing required fields {message}"
                )
                return

            logger.info(
                f"Processing {change_type} event for {entity_id}: "
                f"rev {revision_id} (from_rev: {from_revision_id})"
            )

            await self._process_entity_change(
                entity_id=entity_id,
                to_revision_id=revision_id,
                from_revision_id=from_revision_id,
                change_type=change_type,
            )

        except Exception as e:
            logger.error(f"Error processing message {message}: {e}")

    async def _process_entity_change(
        self,
        entity_id: str,
        to_revision_id: int,
        from_revision_id: Optional[int],
        change_type: str,
    ) -> None:
        """Process an entity change and generate RDF diff."""
        if change_type == "delete":
            await self._handle_entity_deletion(entity_id, to_revision_id)
            return

        old_entity_data = None
        if from_revision_id and from_revision_id > 0:
            old_entity_data = await self._fetch_entity_data(entity_id, from_revision_id)

        new_entity_data = await self._fetch_entity_data(entity_id, to_revision_id)

        if old_entity_data is None:
            operation = "import"
        else:
            operation = "diff"

        updater = IncrementalRDFUpdater(entity_id=entity_id)

        if old_entity_data and new_entity_data:
            try:
                old_entity = self._convert_to_entity_data(old_entity_data)
                new_entity = self._convert_to_entity_data(new_entity_data)
                if old_entity and new_entity:
                    diffs = IncrementalRDFUpdater.compute_diffs(old_entity, new_entity)
                    updater.apply_diffs(diffs)
            except Exception as e:
                logger.warning(f"Failed to compute diffs: {e}")

        rdf_added = updater.get_updated_rdf() if operation == "diff" else ""

        event_config = RDFChangeEventBuilder.EventConfig(
            entity_id=entity_id,
            rev_id=to_revision_id,
            operation=operation,
            rdf_added_data=rdf_added,
            rdf_deleted_data="",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        event_data = RDFChangeEventBuilder.build(event_config)

        if self.producer:
            await self.producer.publish_change(event_data)
            logger.info(
                f"Published RDF change event for {entity_id} rev {to_revision_id}"
            )

    async def _fetch_entity_data(
        self, entity_id: str, revision_id: int
    ) -> Optional[dict[str, Any]]:
        """Fetch entity data for a given revision from S3."""
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return None

        try:
            s3_revision = self.s3_client.read_revision(entity_id, revision_id)
            return s3_revision.revision
        except Exception as e:
            logger.error(
                f"Failed to fetch entity data for {entity_id} rev {revision_id}: {e}"
            )
            return None

    def _convert_to_entity_data(
        self, entity_data: dict[str, Any]
    ) -> Optional[EntityData]:
        """Convert S3 revision dict to EntityData for diff computation."""
        try:
            return EntityData(
                id=entity_data.get("entity", {}).get("id", ""),
                type=entity_data.get("entity", {}).get("type", "item"),
                labels=entity_data.get("entity", {}).get("labels", {}),
                descriptions=entity_data.get("entity", {}).get("descriptions", {}),
                aliases=entity_data.get("entity", {}).get("aliases", {}),
                statements=entity_data.get("entity", {}).get("statements", []),
                sitelinks=entity_data.get("entity", {}).get("sitelinks"),
            )
        except Exception as e:
            logger.warning(f"Failed to convert to EntityData: {e}")
            return None

    async def _handle_entity_deletion(self, entity_id: str, revision_id: int) -> None:
        """Handle entity deletion by publishing a delete event."""
        event_config = RDFChangeEventBuilder.EventConfig(
            entity_id=entity_id,
            rev_id=revision_id,
            operation="delete",
            rdf_added_data="",
            rdf_deleted_data="",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        event_data = RDFChangeEventBuilder.build(event_config)

        if self.producer:
            await self.producer.publish_change(event_data)
            logger.info(f"Published delete event for {entity_id}")


async def main() -> None:
    """Main entry point for the IncrementalRDFWorker."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = IncrementalRDFWorker(
        worker_id=f"incremental-rdf-{id(main)}",
        worker_enabled=settings.incremental_rdf_enabled,
    )

    async with worker.lifespan():
        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
