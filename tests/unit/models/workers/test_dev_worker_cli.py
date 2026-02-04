"""Tests for the DevWorker CLI interface."""

import pytest

from unittest.mock import patch, MagicMock, AsyncMock
from models.workers.dev.__main__ import main
pytestmark = pytest.mark.unit


class TestDevWorkerCLI:
    """Test cases for DevWorker CLI commands."""

    @patch("models.workers.dev.__main__.run_buckets_setup")
    @patch("sys.argv", ["devworker", "buckets", "setup"])
    def test_buckets_setup_command(self, mock_run_setup) -> None:
        """Test buckets setup command execution."""
        mock_run_setup.return_value = True

        result = main()

        assert result == 0
        mock_run_setup.assert_called_once()

    @patch("models.workers.dev.__main__.run_buckets_health")
    @patch("sys.argv", ["devworker", "buckets", "health"])
    def test_buckets_health_command(self, mock_run_health) -> None:
        """Test buckets health check command execution."""
        mock_run_health.return_value = True

        result = main()

        assert result == 0
        mock_run_health.assert_called_once()

    @patch("sys.argv", ["devworker"])
    def test_no_command_error(self, capsys) -> None:
        """Test error when no command is provided."""
        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "usage:" in captured.out

    @patch(
        "sys.argv",
        ["devworker", "--endpoint", "http://custom:9000", "buckets", "setup"],
    )
    @patch("models.workers.dev.__main__.CreateBuckets")
    def test_custom_arguments(
        self,
        mock_create_buckets,
    ):
        """Test CLI with custom arguments."""
        mock_worker = MagicMock()
        mock_worker.run_setup = AsyncMock()
        mock_worker.run_setup.return_value = {
            "setup_status": "completed",
            "buckets_created": {},
            "health_check": {"overall_status": "healthy", "issues": []},
        }
        mock_worker.bucket_health_check = AsyncMock()
        mock_worker.bucket_health_check.return_value = {
            "overall_status": "healthy",
            "issues": [],
            "buckets": {},
        }
        mock_create_buckets.return_value = mock_worker

        result = main()

        assert result == 0
        mock_create_buckets.assert_called_once_with(
            minio_endpoint="http://custom:9000",
            minio_access_key="minioadmin",
            minio_secret_key="minioadmin",
        )

    @patch("models.workers.dev.__main__.run_buckets_setup")
    @patch("sys.argv", ["devworker", "buckets", "setup"])
    def test_command_failure(self, mock_run_setup) -> None:
        """Test handling of command failure."""
        mock_run_setup.return_value = False  # Command failed

        result = main()

        assert result == 1
        mock_run_setup.assert_called_once()

    @patch("models.workers.dev.__main__.run_tables_setup")
    @patch("sys.argv", ["devworker", "tables", "setup"])
    def test_tables_setup_command(self, mock_run_setup) -> None:
        """Test tables setup command execution."""
        mock_run_setup.return_value = True

        result = main()

        assert result == 0
        mock_run_setup.assert_called_once()

    @patch("models.workers.dev.__main__.run_tables_health")
    @patch("sys.argv", ["devworker", "tables", "health"])
    def test_tables_health_command(self, mock_run_health) -> None:
        """Test tables health check command execution."""
        mock_run_health.return_value = True

        result = main()

        assert result == 0
        mock_run_health.assert_called_once()

    @patch("sys.argv", ["devworker", "invalid_component"])
    def test_invalid_component(self, capsys) -> None:
        """Test error for invalid component."""
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert (
            "invalid choice" in captured.err or "unrecognized arguments" in captured.err
        )
