import pytest
from unittest.mock import MagicMock, patch

pytestmark = pytest.mark.unit

from models.rest_api.entitybase.v1.handlers.statement import StatementHandler
from models.rest_api.entitybase.v1.request.statement import StatementBatchRequest


class TestStatementHandler:
    def test_get_statement_s3_none(self) -> None:
        """Test get_statement raises error when s3_client is None"""
        handler = StatementHandler()
        with patch(
            "models.rest_api.entitybase.v1.handlers.statement.raise_validation_error"
        ) as mock_raise:
            handler.get_statement(123, None)
            mock_raise.assert_called_with("Statement 123 not found", status_code=404)

    def test_get_statement_success(self) -> None:
        """Test get_statement success"""
        handler = StatementHandler()
        mock_s3 = MagicMock()
        mock_statement_data = MagicMock()
        mock_statement_data.schema_version = "1.0"
        mock_statement_data.statement = {"id": "P31"}
        mock_statement_data.created_at = "2023-01-01"
        mock_s3.read_statement.return_value = mock_statement_data

        with patch(
            "models.rest_api.entitybase.v1.handlers.statement.StatementResponse"
        ) as mock_response:
            mock_response_instance = MagicMock()
            mock_response.return_value = mock_response_instance

            result = handler.get_statement(123, mock_s3)

            assert result == mock_response_instance
            mock_s3.read_statement.assert_called_once_with(123)
            mock_response.assert_called_once_with(
                schema="1.0",
                hash=123,
                statement={"id": "P31"},
                created_at="2023-01-01",
            )

    def test_get_statement_exception(self) -> None:
        """Test get_statement handles exceptions"""
        handler = StatementHandler()
        mock_s3 = MagicMock()
        mock_s3.read_statement.side_effect = Exception("S3 error")

        with patch(
            "models.rest_api.entitybase.v1.handlers.statement.raise_validation_error"
        ) as mock_raise:
            handler.get_statement(123, mock_s3)
            mock_raise.assert_called_once_with(
                "Statement 123 not found", status_code=404
            )

    def test_get_statements_batch_s3_none(self) -> None:
        """Test get_statements_batch raises error when s3_client is None"""
        handler = StatementHandler()
        request = StatementBatchRequest(hashes=[123, 456])
        with pytest.raises(ValueError) as exc_info:
            handler.get_statements_batch(request, None)
        assert "Statement 123 not found" in str(exc_info.value)

    def test_get_statements_batch_success(self) -> None:
        """Test get_statements_batch success"""
        handler = StatementHandler()
        request = StatementBatchRequest(hashes=[123, 456])
        mock_s3 = MagicMock()

        # Mock for hash 123
        mock_data_123 = MagicMock()
        mock_data_123.schema_version = "1.0"
        mock_data_123.statement = {"id": "P31"}
        mock_data_123.created_at = "2023-01-01"

        # Mock for hash 456 - not found
        mock_s3.read_statement.side_effect = mock_data_123

        with (
            patch(
                "models.rest_api.entitybase.v1.handlers.statement.StatementResponse"
            ) as mock_response,
            patch(
                "models.rest_api.entitybase.v1.handlers.statement.StatementBatchResponse"
            ) as mock_batch_response,
        ):
            mock_response_instance = MagicMock()
            mock_response.return_value = mock_response_instance
            mock_batch_instance = MagicMock()
            mock_batch_response.return_value = mock_batch_instance

            result = handler.get_statements_batch(request, mock_s3)

            assert result == mock_batch_instance
            mock_batch_response.assert_called_once_with(
                statements=[mock_response_instance, mock_response_instance],
                not_found=[],
            )

    def test_get_statements_batch_all_found(self) -> None:
        """Test get_statements_batch when all statements found"""
        handler = StatementHandler()
        request = StatementBatchRequest(hashes=[123])
        mock_s3 = MagicMock()

        mock_data = MagicMock()
        mock_data.schema_version = "1.0"
        mock_data.statement = {"id": "P31"}
        mock_data.created_at = "2023-01-01"
        mock_s3.read_statement.return_value = mock_data

        with (
            patch(
                "models.rest_api.entitybase.v1.handlers.statement.StatementResponse"
            ) as mock_response,
            patch(
                "models.rest_api.entitybase.v1.handlers.statement.StatementBatchResponse"
            ) as mock_batch_response,
        ):
            mock_response_instance = MagicMock()
            mock_response.return_value = mock_response_instance
            mock_batch_instance = MagicMock()
            mock_batch_response.return_value = mock_batch_instance

            result = handler.get_statements_batch(request, mock_s3)

            assert result == mock_batch_instance
            mock_batch_response.assert_called_once_with(
                statements=[mock_response_instance], not_found=[]
            )
