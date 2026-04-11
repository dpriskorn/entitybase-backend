"""Unit tests for VitessWorker base class."""

from unittest.mock import Mock, create_autospec

import pytest

from models.workers.vitess_worker import VitessWorker
from models.workers.worker import Worker


@pytest.mark.unit
class TestVitessWorker:
    """Tests for VitessWorker base class."""

    def test_vitess_worker_initialization_defaults(self):
        """Test VitessWorker initialization with default values."""
        mock_worker = create_autospec(VitessWorker, instance=True)
        mock_worker.vitess_client = None
        mock_worker.running = False

        assert mock_worker.vitess_client is None
        assert mock_worker.running is False

    def test_vitess_worker_inherits_from_worker(self):
        """Test that VitessWorker inherits from Worker."""
        assert issubclass(VitessWorker, Worker)

    def test_vitess_worker_is_pydantic_model(self):
        """Test that VitessWorker is a Pydantic model."""
        from pydantic import BaseModel

        assert issubclass(VitessWorker, BaseModel)
