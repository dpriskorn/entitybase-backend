"""Unit tests for S3 client statement methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientStatements:
    """Unit tests for S3 client statement methods."""

    def test_delete_statement_success(self):
        """Test successful statement deletion."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.delete_statement.return_value = MagicMock(
                success=True
            )

            client.delete_statement(12345)

            client.vitess_statements.delete_statement.assert_called_once_with(12345)

    def test_delete_statement_not_configured(self):
        """Test delete_statement raises error when Vitess not configured."""
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=MagicMock(),
        ):
            client = MyS3Client(config=config)

            with pytest.raises(Exception):
                client.delete_statement(12345)

    def test_write_statement_success(self):
        """Test successful statement write."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.store_statement.return_value = MagicMock(
                success=True
            )

            client.write_statement(12345, {"statement": {"id": "Q1"}}, "1.0.0")

            client.vitess_statements.store_statement.assert_called_once()

    def test_read_statement_success(self):
        """Test successful statement read."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.load_statement.return_value = {"id": "statement1"}

            result = client.read_statement(12345)

            assert result == {"id": "statement1"}

    def test_read_statement_not_found(self):
        """Test read_statement raises error when not found."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config)
            client.vitess_statements = MagicMock()
            client.vitess_statements.load_statement.return_value = None

            with pytest.raises(Exception):
                client.read_statement(12345)
