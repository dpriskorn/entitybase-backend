#!/usr/bin/env python3
"""Development worker for Kafka/Redpanda topic creation and management."""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, TypedDict

from aiokafka.admin import AIOKafkaAdminClient, NewTopic  # type: ignore[import-untyped]
from aiokafka.errors import NodeNotReadyError  # type: ignore[import-untyped]
from pydantic import BaseModel


class TopicHealthCheckResult(TypedDict):
    """Result of topic health check."""

    overall_status: str
    topics: Dict[str, Any]
    issues: List[str]


class TopicSetupResult(TypedDict):
    """Result of topic setup operation."""

    topics_created: Dict[str, str]
    health_check: TopicHealthCheckResult
    setup_status: str


logger = logging.getLogger(__name__)

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, src_path)


class CreateTopics(BaseModel):
    """Create worker for Kafka/Redpanda topic creation and management."""

    model_config = {"arbitrary_types_allowed": True}

    kafka_bootstrap_servers: str = ""
    required_topics: List[str] = []

    def model_post_init(self, context: Any) -> None:
        self.kafka_bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092"
        )
        logger.info(
            f"KAFKA_BOOTSTRAP_SERVERS env var: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}"
        )
        logger.info(f"Using bootstrap servers: {self.kafka_bootstrap_servers}")
        self.required_topics = [
            os.getenv("KAFKA_ENTITY_CHANGE_TOPIC", "entity_change"),
            os.getenv("KAFKA_ENTITY_DIFF_TOPIC", "entity_diff"),
            os.getenv("KAFKA_INCREMENTAL_RDF_TOPIC", "incremental_rdf_diff"),
        ]

    async def ensure_topics_exist(self) -> Dict[str, str]:
        """Ensure all required topics exist, creating them if necessary."""
        results: Dict[str, str] = {}

        if not self.kafka_bootstrap_servers:
            logger.warning(
                "No Kafka bootstrap servers configured, skipping topic creation"
            )
            return results

        max_retries = 5
        retry_delay = 3

        for attempt in range(max_retries):
            try:
                admin_client = AIOKafkaAdminClient(
                    bootstrap_servers=self.kafka_bootstrap_servers,
                )
                await admin_client.start()

                existing_topics = await admin_client.list_topics()

                logger.info(f"Existing topics: {existing_topics}")

                topics_to_create: List[NewTopic] = []
                for topic in self.required_topics:
                    if topic not in existing_topics:
                        new_topic = NewTopic(
                            name=topic,
                            num_partitions=1,
                            replication_factor=1,
                        )
                        topics_to_create.append(new_topic)
                        logger.info(f"Will create topic: {topic}")
                    else:
                        results[topic] = "exists"
                        logger.info(f"Topic already exists: {topic}")

                if topics_to_create:
                    await admin_client.create_topics(topics_to_create)
                    logger.info(f"Created {len(topics_to_create)} topics")
                    for topic_obj in topics_to_create:
                        results[topic_obj.name] = "created"

                await admin_client.close()
                break

            except NodeNotReadyError as e:
                logger.warning(
                    f"Redpanda not ready (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error("Max retries reached for topic creation")
                    raise
            except Exception as e:
                logger.error(f"Failed to create topics: {e}")
                raise

        return results

    async def topic_health_check(self) -> TopicHealthCheckResult:
        """Check if all required topics exist and are accessible."""
        issues: List[str] = []
        topics_status: Dict[str, Any] = {}

        if not self.kafka_bootstrap_servers:
            return TopicHealthCheckResult(
                overall_status="skipped",
                topics={},
                issues=["No Kafka bootstrap servers configured"],
            )

        try:
            admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.kafka_bootstrap_servers,
            )
            await admin_client.start()

            existing_topics = await admin_client.list_topics()

            await admin_client.close()

            for topic in self.required_topics:
                if topic in existing_topics:
                    topics_status[topic] = {"status": "exists", "accessible": True}
                else:
                    topics_status[topic] = {"status": "missing", "accessible": False}
                    issues.append(f"Topic '{topic}' does not exist")

        except Exception as e:
            issues.append(f"Failed to check topics: {e}")

        overall_status = "healthy" if len(issues) == 0 else "unhealthy"

        return TopicHealthCheckResult(
            overall_status=overall_status,
            topics=topics_status,
            issues=issues,
        )

    async def run_setup(self) -> TopicSetupResult:
        """Run complete topic setup process for development environment."""
        logger.info("Starting Kafka topic setup")

        topic_results = await self.ensure_topics_exist()

        health_status = await self.topic_health_check()

        setup_results: TopicSetupResult = {
            "topics_created": topic_results,
            "health_check": health_status,
            "setup_status": "completed"
            if health_status["overall_status"] == "healthy"
            else "failed",
        }

        logger.info(
            f"Kafka topic setup completed with status: {setup_results['setup_status']}"
        )
        return setup_results
