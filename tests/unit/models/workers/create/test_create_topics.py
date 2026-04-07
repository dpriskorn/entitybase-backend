"""Unit tests for create_topics."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from models.workers.create.create_topics import CreateTopics


class TestCreateTopics:
    """Unit tests for CreateTopics class."""

    def test_initialization_defaults(self):
        """Test CreateTopics initialization with defaults."""
        with patch.dict("os.environ", {}, clear=False):
            with patch("models.workers.create.create_topics.os.getenv") as mock_getenv:
                mock_getenv.side_effect = lambda k, d=None: {
                    "KAFKA_BOOTSTRAP_SERVERS": "redpanda:9092",
                    "KAFKA_ENTITY_CHANGE_TOPIC": "entitybase.entity_change",
                    "KAFKA_ENTITY_DIFF_TOPIC": "entitybase.entity_diff",
                }.get(k, d)

                topics = CreateTopics()
                assert topics.kafka_bootstrap_servers == "redpanda:9092"
                assert len(topics.required_topics) == 2

    def test_initialization_with_env_vars(self):
        """Test CreateTopics initialization with environment variables."""
        with patch("models.workers.create.create_topics.os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda k, d=None: {
                "KAFKA_BOOTSTRAP_SERVERS": "custom:9092",
                "KAFKA_ENTITY_CHANGE_TOPIC": "custom.entity_change",
                "KAFKA_ENTITY_DIFF_TOPIC": "custom.entity_diff",
            }.get(k, d)

            topics = CreateTopics()
            assert topics.kafka_bootstrap_servers == "custom:9092"

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_no_servers(self):
        """Test ensure_topics_exist when no servers configured."""
        topics = CreateTopics()
        topics.kafka_bootstrap_servers = ""

        results = await topics.ensure_topics_exist()
        assert results == {}

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_all_exist(self):
        """Test ensure_topics_exist when all topics already exist."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(
                return_value=["entitybase.entity_change", "entitybase.entity_diff"]
            )
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            results = await topics.ensure_topics_exist()

            assert "entitybase.entity_change" in results
            assert results["entitybase.entity_change"] == "exists"
            assert "entitybase.entity_diff" in results
            assert results["entitybase.entity_diff"] == "exists"

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_create_new(self):
        """Test ensure_topics_exist when topics need to be created."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(return_value=[])
            mock_admin.create_topics = AsyncMock()
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            results = await topics.ensure_topics_exist()

            assert "entitybase.entity_change" in results
            assert results["entitybase.entity_change"] == "created"
            mock_admin.create_topics.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_topics_exist_partial(self):
        """Test ensure_topics_exist when some topics exist."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(
                return_value=["entitybase.entity_change"]
            )
            mock_admin.create_topics = AsyncMock()
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            results = await topics.ensure_topics_exist()

            assert results["entitybase.entity_change"] == "exists"
            assert results["entitybase.entity_diff"] == "created"
            mock_admin.create_topics.assert_called_once()

    @pytest.mark.asyncio
    async def test_topic_health_check_no_servers(self):
        """Test topic_health_check when no servers configured."""
        topics = CreateTopics()
        topics.kafka_bootstrap_servers = ""

        result = await topics.topic_health_check()

        assert result["overall_status"] == "skipped"
        assert len(result["issues"]) == 1

    @pytest.mark.asyncio
    async def test_topic_health_check_healthy(self):
        """Test topic_health_check when all topics exist."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(
                return_value=["entitybase.entity_change", "entitybase.entity_diff"]
            )
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            result = await topics.topic_health_check()

            assert result["overall_status"] == "healthy"
            assert len(result["issues"]) == 0

    @pytest.mark.asyncio
    async def test_topic_health_check_unhealthy(self):
        """Test topic_health_check when some topics are missing."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(return_value=[])
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            result = await topics.topic_health_check()

            assert result["overall_status"] == "unhealthy"
            assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_topic_health_check_error(self):
        """Test topic_health_check when an error occurs."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(
                side_effect=Exception("Connection error")
            )
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            result = await topics.topic_health_check()

            assert result["overall_status"] == "unhealthy"
            assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_run_setup_success(self):
        """Test run_setup when setup succeeds."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(
                return_value=["entitybase.entity_change", "entitybase.entity_diff"]
            )
            mock_admin.create_topics = AsyncMock()
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            result = await topics.run_setup()

            assert result["setup_status"] == "completed"
            assert result["health_check"]["overall_status"] == "healthy"

    @pytest.mark.asyncio
    async def test_run_setup_failure(self):
        """Test run_setup when setup fails."""
        with patch(
            "models.workers.create.create_topics.AIOKafkaAdminClient"
        ) as mock_admin_class:
            mock_admin = MagicMock()
            mock_admin.start = AsyncMock()
            mock_admin.close = AsyncMock()
            mock_admin.list_topics = AsyncMock(return_value=[])
            mock_admin.create_topics = AsyncMock()
            mock_admin_class.return_value = mock_admin

            topics = CreateTopics()
            topics.kafka_bootstrap_servers = "redpanda:9092"

            result = await topics.run_setup()

            assert result["setup_status"] == "failed"
            assert result["health_check"]["overall_status"] == "unhealthy"
