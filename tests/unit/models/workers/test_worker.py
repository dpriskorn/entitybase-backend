"""Unit tests for Worker base class."""

import os

import pytest

from models.workers.worker import Worker


@pytest.mark.unit
class TestWorker:
    """Tests for Worker base class."""

    def test_worker_initialization_with_defaults(self):
        """Test Worker initialization with default values."""
        worker = Worker()
        
        assert worker.worker_id == f"worker-{os.getpid()}"
        assert worker.running is False

    def test_worker_initialization_with_custom_worker_id(self):
        """Test Worker initialization with custom worker_id."""
        worker = Worker(worker_id="custom-worker-123")
        
        assert worker.worker_id == "custom-worker-123"
        assert worker.running is False

    def test_worker_initialization_with_running_true(self):
        """Test Worker initialization with running=True."""
        worker = Worker(running=True)
        
        assert worker.running is True

    def test_worker_initialization_with_all_params(self):
        """Test Worker initialization with all parameters."""
        worker = Worker(worker_id="test-worker", running=True)
        
        assert worker.worker_id == "test-worker"
        assert worker.running is True

    def test_worker_initialization_defaults_with_env_var(self):
        """Test Worker reads WORKER_ID from environment."""
        original_worker_id = os.getenv("WORKER_ID")
        try:
            os.environ["WORKER_ID"] = "env-worker-456"
            worker = Worker()
            
            assert worker.worker_id == "env-worker-456"
        finally:
            if original_worker_id is None:
                os.environ.pop("WORKER_ID", None)
            else:
                os.environ["WORKER_ID"] = original_worker_id

    def test_worker_custom_id_takes_precedence_over_env(self):
        """Test that custom worker_id takes precedence over env var."""
        original_worker_id = os.getenv("WORKER_ID")
        try:
            os.environ["WORKER_ID"] = "env-worker"
            worker = Worker(worker_id="custom-worker")
            
            assert worker.worker_id == "custom-worker"
        finally:
            if original_worker_id is None:
                os.environ.pop("WORKER_ID", None)
            else:
                os.environ["WORKER_ID"] = original_worker_id

    def test_worker_running_state_can_be_modified(self):
        """Test that running state can be modified."""
        worker = Worker()
        
        assert worker.running is False
        worker.running = True
        assert worker.running is True
        worker.running = False
        assert worker.running is False

    def test_worker_is_pydantic_model(self):
        """Test that Worker is a Pydantic model."""
        from pydantic import BaseModel
        
        assert issubclass(Worker, BaseModel)

    def test_worker_model_dump(self):
        """Test that Worker can be dumped to dict."""
        worker = Worker(worker_id="test-worker", running=True)
        data = worker.model_dump()
        
        assert data["worker_id"] == "test-worker"
        assert data["running"] is True

    def test_worker_model_dump_json(self):
        """Test that Worker can be dumped to JSON."""
        worker = Worker(worker_id="test-worker", running=True)
        json_str = worker.model_dump_json()
        
        assert "test-worker" in json_str
        assert "true" in json_str
