"""Tests for the DevWorker CLI interface."""

import pytest

pytestmark = pytest.mark.unit
from unittest.mock import patch, MagicMock, AsyncMock
from models.workers.dev.__main__ import main


class TestDevWorkerCLI:
    """Test cases for DevWorker CLI commands."""

    @patch("models.workers.dev.__main__.run_setup")
    @patch("sys.argv", ["devworker", "setup"])
    def test_setup_command(self, mock_run_setup):
        """Test setup command execution."""
        mock_run_setup.return_value = True

        result = main()

        assert result == 0
        mock_run_setup.assert_called_once()

    @patch("models.workers.dev.__main__.run_health_check")
    @patch("sys.argv", ["devworker", "health"])
    def test_health_command(self, mock_run_health):
        """Test health check command execution."""
        mock_run_health.return_value = True

        result = main()

        assert result == 0
        mock_run_health.assert_called_once()

    @patch("models.workers.dev.__main__.run_cleanup")
    @patch("sys.argv", ["devworker", "cleanup", "--force"])
    def test_cleanup_command_force(self, mock_run_cleanup):
        """Test cleanup command with force flag."""
        mock_run_cleanup.return_value = True

        result = main()

        assert result == 0
        mock_run_cleanup.assert_called_once()

    @patch("builtins.input", return_value="yes")
    @patch("models.workers.dev.create_buckets.CreateBuckets.cleanup_buckets")
    @patch("sys.argv", ["devworker", "cleanup"])
    def test_cleanup_command_with_confirmation(self, mock_cleanup, mock_input):
        """Test cleanup command with user confirmation."""
        mock_cleanup.return_value = {"bucket1": "deleted"}

        result = main()

        assert result == 0
        mock_cleanup.assert_called_once()
        mock_input.assert_called_once_with("Are you sure? Type 'yes' to confirm: ")

    @patch("builtins.input", return_value="no")
    @patch("models.workers.dev.create_buckets.CreateBuckets.cleanup_buckets")
    @patch("sys.argv", ["devworker", "cleanup"])
    def test_cleanup_command_cancelled(self, mock_cleanup, mock_input):
        """Test cleanup command cancellation."""
        result = main()

        assert result == 1
        mock_cleanup.assert_not_called()
        mock_input.assert_called_once_with("Are you sure? Type 'yes' to confirm: ")

    @patch("sys.argv", ["devworker"])
    def test_no_command_error(self, capsys):
        """Test error when no command is provided."""
        result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "usage:" in captured.out

    @patch(
        "models.workers.dev.create_buckets.CreateBuckets.cleanup_buckets",
        new_callable=AsyncMock,
        return_value={"bucket": "deleted"},
    )
    @patch("models.workers.dev.create_buckets.CreateBuckets")
    @patch("asyncio.run")
    @patch("models.workers.dev.__main__.run_setup")
    @patch(
        "sys.argv",
        ["devworker", "--endpoint", "http://custom:9000", "setup"],
    )
    def test_custom_arguments(
        self, mock_run_setup, mock_asyncio_run, mock_dev_worker_class
    ):
        """Test CLI with custom arguments."""
        mock_worker = MagicMock()
        mock_dev_worker_class.return_value = mock_worker

        mock_asyncio_run.return_value = True

        result = main()

        assert result == 0
        mock_dev_worker_class.assert_called_once_with(
            minio_endpoint="http://custom:9000",
            minio_access_key="minioadmin",
            minio_secret_key="minioadmin",
        )

    @patch("models.workers.dev.__main__.run_setup")
    @patch("sys.argv", ["devworker", "setup"])
    def test_command_failure(self, mock_run_setup):
        """Test handling of command failure."""
        mock_run_setup.return_value = False  # Command failed

        result = main()

        assert result == 1
        mock_run_setup.assert_called_once()

    @patch("sys.argv", ["devworker", "invalid_command"])
    def test_invalid_command(self, capsys):
        """Test error for invalid command."""
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert (
            "invalid choice" in captured.err or "unrecognized arguments" in captured.err
        )
