"""Unit tests for Elasticsearch indexer worker."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from models.workers.elasticsearch_indexer.elasticsearch_indexer_worker import (
    ElasticsearchIndexerWorker,
)


class TestElasticsearchIndexerWorker:
    """Tests for ElasticsearchIndexerWorker class."""

    def test_init_disabled(self):
        """Test worker initialization when disabled."""
        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=False,
        )

        assert worker.worker_enabled is False
        assert worker.worker_id == "test-worker"

    @pytest.mark.asyncio
    async def test_lifespan_disabled(self):
        """Test lifespan when worker is disabled."""
        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=False,
        )

        async with worker.lifespan():
            pass

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_lifespan_enabled_no_kafka(self, mock_settings):
        """Test lifespan when worker is enabled but no Kafka."""
        mock_settings.kafka_bootstrap_servers = ""
        mock_settings.elasticsearch_enabled = True
        mock_settings.elasticsearch_host = "localhost"
        mock_settings.elasticsearch_port = 9200
        mock_settings.elasticsearch_index = "entitybase"
        mock_settings.elasticsearch_username = ""
        mock_settings.elasticsearch_password = ""
        mock_settings.elasticsearch_use_ssl = True
        mock_settings.elasticsearch_verify_certs = True
        mock_settings.get_vitess_config = MagicMock(host="", port=0)
        mock_settings.get_s3_config = MagicMock(endpoint_url="")

        with patch(
            "models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.ElasticsearchClient"
        ) as mock_es:
            mock_es_client = MagicMock()
            mock_es_client.connect.return_value = True
            mock_es.return_value = mock_es_client

            worker = ElasticsearchIndexerWorker(
                worker_id="test-worker",
                worker_enabled=True,
            )

            async with worker.lifespan():
                pass

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_lifespan_enabled_kafka(self, mock_settings):
        """Test lifespan when worker is enabled with Kafka."""
        mock_settings.kafka_bootstrap_servers = "localhost:9092"
        mock_settings.elasticsearch_enabled = True
        mock_settings.elasticsearch_host = "localhost"
        mock_settings.elasticsearch_port = 9200
        mock_settings.elasticsearch_index = "entitybase"
        mock_settings.elasticsearch_username = ""
        mock_settings.elasticsearch_password = ""
        mock_settings.elasticsearch_use_ssl = True
        mock_settings.elasticsearch_verify_certs = True
        mock_settings.get_vitess_config = MagicMock(host="", port=0)
        mock_settings.get_s3_config = MagicMock(endpoint_url="")
        mock_settings.kafka_entitychange_json_topic = "entity_change"
        mock_settings.elasticsearch_consumer_group = "test-group"

        with patch(
            "models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.ElasticsearchClient"
        ) as mock_es:
            mock_es_client = MagicMock()
            mock_es_client.connect.return_value = True
            mock_es.return_value = mock_es_client

            with patch(
                "models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.StreamConsumerClient"
            ) as mock_consumer_cls:
                mock_consumer = AsyncMock()
                mock_consumer.start = AsyncMock()
                mock_consumer.stop = AsyncMock()
                mock_consumer_cls.return_value = mock_consumer

                worker = ElasticsearchIndexerWorker(
                    worker_id="test-worker",
                    worker_enabled=True,
                )

                async with worker.lifespan():
                    pass

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_lifespan_exception(self, mock_settings):
        """Test lifespan with exception during startup."""
        mock_settings.kafka_bootstrap_servers = ""
        mock_settings.elasticsearch_enabled = True
        mock_settings.elasticsearch_host = "localhost"
        mock_settings.elasticsearch_port = 9200
        mock_settings.elasticsearch_index = "entitybase"
        mock_settings.elasticsearch_username = ""
        mock_settings.elasticsearch_password = ""
        mock_settings.elasticsearch_use_ssl = True
        mock_settings.elasticsearch_verify_certs = True
        mock_settings.get_vitess_config = MagicMock(host="", port=0)
        mock_settings.get_s3_config = MagicMock(endpoint_url="")

        with patch(
            "models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.ElasticsearchClient"
        ) as mock_es:
            mock_es.side_effect = Exception("Connection failed")

            worker = ElasticsearchIndexerWorker(
                worker_id="test-worker",
                worker_enabled=True,
            )

            with pytest.raises(Exception):
                async with worker.lifespan():
                    pass

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_get_kafka_brokers_empty(self, mock_settings):
        """Test getting Kafka brokers when not configured."""
        mock_settings.kafka_bootstrap_servers = ""

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        brokers = worker._get_kafka_brokers()
        assert brokers == []

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_get_kafka_brokers_multiple(self, mock_settings):
        """Test getting Kafka brokers when multiple configured."""
        mock_settings.kafka_bootstrap_servers = "host1:9092, host2:9092, host3:9092"

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        brokers = worker._get_kafka_brokers()
        assert brokers == ["host1:9092", "host2:9092", "host3:9092"]

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_process_message_invalid(self, mock_settings):
        """Test processing invalid message."""
        mock_settings.elasticsearch_enabled = True

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        message = MagicMock()
        message.entity_id = None
        message.revision_id = None

        await worker.process_message(message)

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_process_message_delete(self, mock_settings):
        """Test processing delete message."""
        mock_settings.elasticsearch_enabled = True

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        message = MagicMock()
        message.entity_id = "Q42"
        message.revision_id = 12345
        message.change_type = "delete"

        with patch.object(worker, "elasticsearch_client") as mock_es:
            mock_es.delete_document.return_value = True

            await worker.process_message(message)

            mock_es.delete_document.assert_called_once_with("Q42")

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_process_message_exception(self, mock_settings):
        """Test processing message with exception."""
        mock_settings.elasticsearch_enabled = True

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        message = MagicMock()
        message.entity_id = "Q42"
        message.revision_id = 12345
        message.change_type = "update"
        message.side_effect = Exception("Test exception")

        await worker.process_message(message)

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_handle_delete(self, mock_settings):
        """Test delete handler."""
        mock_settings.elasticsearch_enabled = True

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        with patch.object(worker, "elasticsearch_client") as mock_es:
            mock_es.delete_document.return_value = True

            await worker._handle_delete("Q42")

            mock_es.delete_document.assert_called_once_with("Q42")

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_handle_change_no_clients(self, mock_settings):
        """Test handle change with no clients."""
        mock_settings.elasticsearch_enabled = True

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        await worker._handle_change("Q42", 12345, "update")

    @pytest.mark.asyncio
    @patch(
        "models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.transform_to_elasticsearch"
    )
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_handle_change_success(self, mock_settings, mock_transform):
        """Test handle change with success."""
        mock_settings.elasticsearch_enabled = True
        mock_transform.return_value = {"entity_id": "Q42", "labels": {}}

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        worker.s3_client = MagicMock()
        worker.elasticsearch_client = MagicMock()
        worker.elasticsearch_client.index_document.return_value = True

        entity_json = {
            "entities": {
                "Q42": {
                    "type": "item",
                    "id": "Q42",
                    "labels": {},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                }
            }
        }

        with patch.object(
            worker,
            "_fetch_entity_from_s3",
            return_value=entity_json,
        ):
            await worker._handle_change("Q42", 12345, "update")

        worker.elasticsearch_client.index_document.assert_called_once()

    @pytest.mark.asyncio
    @patch(
        "models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.transform_to_elasticsearch"
    )
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_handle_change_index_failure(self, mock_settings, mock_transform):
        """Test handle change with indexing failure."""
        mock_settings.elasticsearch_enabled = True
        mock_transform.return_value = {"entity_id": "Q42", "labels": {}}

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        worker.s3_client = MagicMock()
        worker.elasticsearch_client = MagicMock()
        worker.elasticsearch_client.index_document.return_value = False

        entity_json = {
            "entities": {
                "Q42": {
                    "type": "item",
                    "id": "Q42",
                    "labels": {},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                }
            }
        }

        with patch.object(
            worker,
            "_fetch_entity_from_s3",
            return_value=entity_json,
        ):
            await worker._handle_change("Q42", 12345, "update")

    @pytest.mark.asyncio
    @patch(
        "models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.transform_to_elasticsearch"
    )
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_handle_change_fetch_failure(self, mock_settings, mock_transform):
        """Test handle change when S3 fetch fails."""
        mock_settings.elasticsearch_enabled = True
        mock_transform.return_value = {"entity_id": "Q42", "labels": {}}

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        worker.s3_client = MagicMock()
        worker.elasticsearch_client = MagicMock()

        with patch.object(
            worker,
            "_fetch_entity_from_s3",
            return_value=None,
        ):
            await worker._handle_change("Q42", 12345, "update")

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_fetch_entity_from_s3_no_client(self, mock_settings):
        """Test fetch entity with no S3 client."""
        mock_settings.elasticsearch_enabled = True

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        result = await worker._fetch_entity_from_s3("Q42", 12345)

        assert result is None

    @pytest.mark.asyncio
    @patch("models.workers.elasticsearch_indexer.elasticsearch_indexer_worker.settings")
    async def test_run_no_consumer(self, mock_settings):
        """Test run method without consumer."""
        mock_settings.elasticsearch_enabled = True

        worker = ElasticsearchIndexerWorker(
            worker_id="test-worker",
            worker_enabled=True,
        )

        await worker.run()
