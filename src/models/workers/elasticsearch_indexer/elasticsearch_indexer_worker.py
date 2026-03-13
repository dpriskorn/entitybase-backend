"""Elasticsearch indexer worker for processing entity changes and indexing to OpenSearch."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from pydantic import Field

from models.config.settings import settings
from models.data.infrastructure.stream.consumer import EntityChangeEventData
from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.stream.consumer import StreamConsumerClient
from models.infrastructure.vitess.client import VitessClient
from models.services.elasticsearch import (
    ElasticsearchClient,
    transform_to_elasticsearch,
)
from models.workers.worker import Worker

logger = logging.getLogger(__name__)


class ElasticsearchIndexerWorker(Worker):
    """Worker that consumes entity change events and indexes them to Elasticsearch.

    This worker:
    1. Consumes entity change events from entitybase.entity_change Kafka topic
    2. Fetches entity snapshots from S3 for the new revision
    3. Transforms entity data to Elasticsearch format
    4. Indexes the document to OpenSearch
    """

    vitess_client: Optional[VitessClient] = Field(default=None, exclude=True)
    s3_client: Optional[MyS3Client] = Field(default=None, exclude=True)
    consumer: Optional[StreamConsumerClient] = Field(default=None, exclude=True)
    elasticsearch_client: Any = Field(default=None, exclude=True)
    worker_enabled: bool = Field(default=False, exclude=True)

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None, None]:
        """Lifespan context manager for startup/shutdown."""
        try:
            if not self.worker_enabled:
                logger.info("ElasticsearchIndexerWorker disabled by configuration")
                yield
                return

            logger.info("Starting ElasticsearchIndexerWorker")

            await self._initialize_clients()

            logger.info("ElasticsearchIndexerWorker started successfully")

            yield
        except Exception as e:
            logger.error(f"Failed to start ElasticsearchIndexerWorker: {e}")
            raise
        finally:
            await self._cleanup_clients()
            logger.info("ElasticsearchIndexerWorker stopped")

    async def _initialize_clients(self) -> None:
        """Initialize Kafka consumer, S3 client, and Elasticsearch client."""
        kafka_brokers = self._get_kafka_brokers()

        if kafka_brokers:
            await self._initialize_kafka(kafka_brokers)
        else:
            logger.warning(
                "Kafka not configured, worker will not be able to consume events"
            )

        await self._initialize_storage_clients()
        await self._initialize_elasticsearch()

    def _get_kafka_brokers(self) -> list[str]:
        """Get Kafka brokers from settings."""
        if not settings.kafka_bootstrap_servers:
            return []
        return [
            b.strip() for b in settings.kafka_bootstrap_servers.split(",") if b.strip()
        ]

    async def _initialize_kafka(self, kafka_brokers: list[str]) -> None:
        """Initialize Kafka consumer."""
        from models.data.config.stream_consumer import StreamConsumerConfig

        consumer_config = StreamConsumerConfig(
            brokers=kafka_brokers,
            topic=settings.kafka_entitychange_json_topic,
            group_id=settings.elasticsearch_consumer_group,
        )
        self.consumer = StreamConsumerClient(config=consumer_config)
        await self.consumer.start()
        logger.info(
            f"Kafka consumer started: topic={settings.kafka_entitychange_json_topic}, "
            f"group={settings.elasticsearch_consumer_group}"
        )

    async def _initialize_storage_clients(self) -> None:
        """Initialize S3 and Vitess clients."""
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
        if s3_config.endpoint_url:
            self.s3_client = MyS3Client(config=s3_config)
            logger.info("S3 client initialized")
        else:
            logger.warning("S3 not configured, worker cannot fetch entity snapshots")

    async def _initialize_elasticsearch(self) -> None:
        """Initialize Elasticsearch client."""
        self.elasticsearch_client = ElasticsearchClient(
            host=settings.elasticsearch_host,
            port=settings.elasticsearch_port,
            index=settings.elasticsearch_index,
            username=settings.elasticsearch_username or None,
            password=settings.elasticsearch_password or None,
        )

        if self.elasticsearch_client.connect():
            logger.info(
                f"Elasticsearch client connected: {settings.elasticsearch_host}:{settings.elasticsearch_port}/{settings.elasticsearch_index}"
            )
        else:
            logger.error("Failed to connect to Elasticsearch")

    async def _cleanup_clients(self) -> None:
        """Clean up all clients."""
        if self.consumer:
            await self.consumer.stop()
        if self.elasticsearch_client:
            self.elasticsearch_client.close()
        if self.vitess_client and self.vitess_client.connection_manager:
            self.vitess_client.connection_manager.disconnect()
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
            change_type = message.change_type

            if not entity_id or not revision_id:
                logger.warning(
                    f"Invalid event message: missing required fields {message}"
                )
                return

            logger.info(
                f"Processing {change_type} event for {entity_id}: rev {revision_id}"
            )

            if change_type == "delete":
                await self._handle_delete(entity_id)
            else:
                await self._handle_change(entity_id, revision_id, change_type)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _handle_delete(self, entity_id: str) -> None:
        """Handle entity deletion."""
        if self.elasticsearch_client:
            self.elasticsearch_client.delete_document(entity_id)
            logger.info(f"Deleted entity {entity_id} from Elasticsearch")

    async def _handle_change(
        self, entity_id: str, revision_id: int, change_type: str
    ) -> None:
        """Handle entity change (create/update)."""
        if not self.s3_client or not self.elasticsearch_client:
            logger.warning(
                "S3 or Elasticsearch client not available, skipping indexing"
            )
            return

        try:
            entity_json = await self._fetch_entity_from_s3(entity_id, revision_id)
            if not entity_json:
                logger.warning(f"Could not fetch entity {entity_id} from S3")
                return

            es_document = transform_to_elasticsearch(entity_json)

            success = self.elasticsearch_client.index_document(entity_id, es_document)
            if success:
                logger.info(f"Indexed entity {entity_id} to Elasticsearch")
            else:
                logger.error(f"Failed to index entity {entity_id}")

        except Exception as e:
            logger.error(f"Error handling change for {entity_id}: {e}")

    async def _fetch_entity_from_s3(
        self, entity_id: str, revision_id: int
    ) -> Optional[dict[str, Any]]:
        """Fetch entity data from S3."""
        if not self.s3_client:
            return None

        try:
            from models.infrastructure.s3.entity_storage import EntityStorage

            storage = EntityStorage(s3_client=self.s3_client)
            entity_data = await storage.get_entity(entity_id, revision_id)

            if entity_data and entity_data.entity_data:
                result: dict[str, Any] = entity_data.entity_data.revision.model_dump(
                    mode="json"
                )
                return result

            return None

        except Exception as e:
            logger.error(f"Error fetching entity {entity_id} from S3: {e}")
            return None


async def main() -> None:
    """Main entry point for the ElasticsearchIndexerWorker."""
    worker = ElasticsearchIndexerWorker(
        worker_id="elasticsearch-indexer",
        worker_enabled=settings.elasticsearch_enabled,
    )

    async with worker.lifespan():
        await worker.run()
