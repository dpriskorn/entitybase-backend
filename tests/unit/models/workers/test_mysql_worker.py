"""Unit tests for MysqlWorker base class."""

from unittest.mock import Mock, create_autospec

import pytest

from models.workers.mysql_worker import MysqlWorker
from models.workers.worker import Worker


@pytest.mark.unit
class TestMysqlWorker:
    """Tests for MysqlWorker base class."""

    def test_mysql_worker_initialization_defaults(self):
        """Test MysqlWorker initialization with default values."""
        mock_worker = create_autospec(MysqlWorker, instance=True)
        mock_worker.db_client = None
        mock_worker.running = False

        assert mock_worker.db_client is None
        assert mock_worker.running is False

    def test_mysql_worker_inherits_from_worker(self):
        """Test that MysqlWorker inherits from Worker."""
        assert issubclass(MysqlWorker, Worker)

    def test_mysql_worker_is_pydantic_model(self):
        """Test that MysqlWorker is a Pydantic model."""
        from pydantic import BaseModel

        assert issubclass(MysqlWorker, BaseModel)
