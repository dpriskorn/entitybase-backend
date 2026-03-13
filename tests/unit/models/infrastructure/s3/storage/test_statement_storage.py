"""Unit tests for statement_storage."""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from models.data.infrastructure.s3 import DictLoadResponse
from models.infrastructure.s3.storage.statement_storage import StatementStorage
from models.infrastructure.s3.exceptions import S3NotFoundError, S3StorageError


class TestStatementStorage:
    """Unit tests for StatementStorage class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_connection_manager = MagicMock()
        self.mock_boto_client = MagicMock()
        self.mock_connection_manager.boto_client = self.mock_boto_client

    def test_store_statement_success(self) -> None:
        """Test successful statement storage."""
        with patch(
            "models.infrastructure.s3.storage.statement_storage.settings"
        ) as mock_settings:
            mock_settings.s3_statements_bucket = "test-statements"
            storage = StatementStorage(connection_manager=self.mock_connection_manager)

            statement_data = {
                "statement": {"type": "statement", "value": "test"}
            }
            result = storage.store_statement(
                content_hash=12345,
                statement_data=statement_data,
                schema_version="1.0.0",
            )

            assert result.success is True
            self.mock_boto_client.put_object.assert_called_once()

    def test_store_statement_failure(self) -> None:
        """Test statement storage failure."""
        self.mock_boto_client.put_object.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Server error"}},
            "PutObject",
        )

        with patch(
            "models.infrastructure.s3.storage.statement_storage.settings"
        ) as mock_settings:
            mock_settings.s3_statements_bucket = "test-statements"
            storage = StatementStorage(connection_manager=self.mock_connection_manager)

            statement_data = {
                "statement": {"type": "statement", "value": "test"}
            }
            with pytest.raises(S3StorageError):
                storage.store_statement(
                    content_hash=12345,
                    statement_data=statement_data,
                    schema_version="1.0.0",
                )

    def test_load_statement_success(self) -> None:
        """Test successful statement loading."""
        import json
        test_data = {
            "hash": 12345,
            "schema": "1.0.0",
            "statement": {"type": "statement", "value": "test"},
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        body_mock = MagicMock()
        body_mock.read.return_value = json.dumps(test_data).encode('utf-8')
        
        self.mock_boto_client.get_object.return_value = {
            "ContentType": "application/json",
            "Body": body_mock,
        }

        with patch(
            "models.infrastructure.s3.storage.statement_storage.settings"
        ) as mock_settings:
            mock_settings.s3_statements_bucket = "test-statements"
            storage = StatementStorage(connection_manager=self.mock_connection_manager)

            result = storage.load_statement(content_hash=12345)

            assert result.content_hash == 12345
            assert result.schema_version == "1.0.0"
            assert result.statement == {"type": "statement", "value": "test"}

    def test_load_statement_not_found(self) -> None:
        """Test loading non-existent statement."""
        self.mock_boto_client.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Not found"}}, "GetObject"
        )

        with patch(
            "models.infrastructure.s3.storage.statement_storage.settings"
        ) as mock_settings:
            mock_settings.s3_statements_bucket = "test-statements"
            storage = StatementStorage(connection_manager=self.mock_connection_manager)

            with pytest.raises(S3NotFoundError):
                storage.load_statement(content_hash=99999)

    def test_load_statement_unexpected_error(self) -> None:
        """Test loading statement with unexpected error."""
        self.mock_boto_client.get_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Denied"}}, "GetObject"
        )

        with patch(
            "models.infrastructure.s3.storage.statement_storage.settings"
        ) as mock_settings:
            mock_settings.s3_statements_bucket = "test-statements"
            storage = StatementStorage(connection_manager=self.mock_connection_manager)

            with pytest.raises(S3StorageError):
                storage.load_statement(content_hash=12345)

    def test_delete_statement_success(self) -> None:
        """Test successful statement deletion."""
        with patch(
            "models.infrastructure.s3.storage.statement_storage.settings"
        ) as mock_settings:
            mock_settings.s3_statements_bucket = "test-statements"
            storage = StatementStorage(connection_manager=self.mock_connection_manager)

            result = storage.delete_statement(content_hash=12345)

            assert result.success is True
            self.mock_boto_client.delete_object.assert_called_once()

    def test_delete_statement_failure(self) -> None:
        """Test statement deletion failure."""
        self.mock_boto_client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Server error"}},
            "DeleteObject",
        )

        with patch(
            "models.infrastructure.s3.storage.statement_storage.settings"
        ) as mock_settings:
            mock_settings.s3_statements_bucket = "test-statements"
            storage = StatementStorage(connection_manager=self.mock_connection_manager)

            with pytest.raises(S3StorageError):
                storage.delete_statement(content_hash=12345)
