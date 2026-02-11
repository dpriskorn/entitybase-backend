"""Unit tests for VitessWorker base class."""

import pytest

from models.workers.vitess_worker import VitessWorker
from models.workers.worker import Worker


@pytest.mark.unit
class TestVitessWorker:
    """Tests for VitessWorker base class."""

    def test_vitess_worker_initialization_defaults(self):
        """Test VitessWorker initialization with default values."""
        worker = VitessWorker()

        assert worker.vitess_client is None
        assert worker.worker_id is not None
        assert worker.running is False

    def test_vitess_worker_inherits_from_worker(self):
        """Test that VitessWorker inherits from Worker."""
        assert issubclass(VitessWorker, Worker)

    def test_vitess_worker_with_custom_vitess_client(self):
        """Test VitessWorker initialization with custom vitess_client."""
        mock_client = object()
        worker = VitessWorker(vitess_client=mock_client)

        assert worker.vitess_client is mock_client

    def test_vitess_worker_with_custom_params(self):
        """Test VitessWorker initialization with custom parameters."""
        mock_client = object()
        worker = VitessWorker(
            worker_id="test-vitess-worker", running=True, vitess_client=mock_client
        )

        assert worker.worker_id == "test-vitess-worker"
        assert worker.running is True
        assert worker.vitess_client is mock_client

    def test_vitess_worker_is_pydantic_model(self):
        """Test that VitessWorker is a Pydantic model."""
        from pydantic import BaseModel

        assert issubclass(VitessWorker, BaseModel)

    def test_vitess_worker_model_dump(self):
        """Test that VitessWorker can be dumped to dict."""
        worker = VitessWorker(worker_id="test-worker", running=True)
        data = worker.model_dump()

        assert data["worker_id"] == "test-worker"
        assert data["running"] is True
        assert data["vitess_client"] is None

    def test_vitess_worker_model_dump_with_client(self):
        """Test that VitessWorker dumps with vitess_client."""
        mock_client = object()
        worker = VitessWorker(worker_id="test-worker", vitess_client=mock_client)
        data = worker.model_dump()

        assert data["worker_id"] == "test-worker"
        assert data["vitess_client"] is mock_client

    def test_vitess_worker_running_state_can_be_modified(self):
        """Test that running state can be modified."""
        worker = VitessWorker()

        assert worker.running is False
        worker.running = True
        assert worker.running is True
        worker.running = False
        assert worker.running is False

    def test_vitess_worker_vitess_client_can_be_set(self):
        """Test that vitess_client can be set."""
        worker = VitessWorker()
        assert worker.vitess_client is None

        mock_client = object()
        worker.vitess_client = mock_client
        assert worker.vitess_client is mock_client
