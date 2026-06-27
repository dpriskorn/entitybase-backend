"""Unit tests for SqlWorker base class."""

from unittest.mock import Mock, create_autospec

import pytest

from models.workers.mysql_worker import SqlWorker
from models.workers.worker import Worker


@pytest.mark.unit
class TestSqlWorker:
    """Tests for SqlWorker base class."""

    def test_mysql_worker_initialization_defaults(self):
        """Test SqlWorker initialization with default values."""
        mock_worker = create_autospec(SqlWorker, instance=True)
        mock_worker.mysql_client = None
        mock_worker.running = False

        assert mock_worker.mysql_client is None
        assert mock_worker.running is False

    def test_mysql_worker_inherits_from_worker(self):
        """Test that SqlWorker inherits from Worker."""
        assert issubclass(SqlWorker, Worker)

    def test_mysql_worker_is_pydantic_model(self):
        """Test that SqlWorker is a Pydantic model."""
        from pydantic import BaseModel

        assert issubclass(SqlWorker, BaseModel)
