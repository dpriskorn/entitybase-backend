"""Unit tests for base_storage."""

import json
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from models.infrastructure.s3.base_storage import BaseS3Storage, LoadResponse
from models.infrastructure.s3.exceptions import S3ConnectionError, S3NotFoundError, S3StorageError


class ConcreteBaseS3Storage(BaseS3Storage):
    """Concrete test implementation of BaseS3Storage."""

    bucket: str = "test-bucket"


class TestBaseStorageUnit:
    """Unit tests for BaseS3Storage class."""

    def test_store_success(self) -> None:
        """Test successful data storage."""
        storage = ConcreteBaseS3Storage()
        # Mock the connection manager
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Mock successful put_object
        mock_boto_client.put_object.return_value = {}

        test_data = {"key": "value"}
        result = storage.store("test-key", test_data)

        assert result.success is True
        mock_boto_client.put_object.assert_called_once()
        call_args = mock_boto_client.put_object.call_args
        assert call_args[1]["Bucket"] == "test-bucket"
        assert call_args[1]["Key"] == "test-key"
        assert json.loads(call_args[1]["Body"]) == test_data

    def test_store_string_data(self) -> None:
        """Test storing string data."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.put_object.return_value = {}

        test_string = "plain text content"
        result = storage.store("test-key", test_string)

        assert result.success is True
        call_args = mock_boto_client.put_object.call_args
        assert call_args[1]["ContentType"] == "text/plain"
        assert call_args[1]["Body"] == test_string.encode("utf-8")

    def test_store_no_connection(self) -> None:
        """Test store operation when connection is not available."""
        storage = ConcreteBaseS3Storage()
        storage.connection_manager = None  # No connection

        with pytest.raises(S3ConnectionError, match="S3 service unavailable"):
            storage.store("test-key", {"data": "value"})

    def test_load_success_json(self) -> None:
        """Test successful JSON data loading."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        test_data = {"loaded": "data"}
        mock_response = {
            "Body": MagicMock(),
            "ContentType": "application/json"
        }
        mock_response["Body"].read.return_value = json.dumps(test_data).encode("utf-8")
        mock_boto_client.get_object.return_value = mock_response

        result = storage.load("test-key")

        assert result is not None
        assert isinstance(result, LoadResponse)
        assert result.data == test_data
        mock_boto_client.get_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")

    def test_load_success_text(self) -> None:
        """Test successful text data loading."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        test_text = "plain text content"
        mock_response = {
            "Body": MagicMock(),
            "ContentType": "text/plain"
        }
        mock_response["Body"].read.return_value = test_text.encode("utf-8")
        mock_boto_client.get_object.return_value = mock_response

        result = storage.load("test-key")

        assert result is not None
        assert isinstance(result, LoadResponse)
        assert result.data == test_text

    def test_load_no_connection(self) -> None:
        """Test load operation when connection is not available."""
        storage = ConcreteBaseS3Storage()
        storage.connection_manager = None  # No connection

        with pytest.raises(S3ConnectionError, match="S3 service unavailable"):
            storage.load("test-key")

    def test_load_not_found(self) -> None:
        """Test loading non-existent key."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Simulate NoSuchKey error
        error_response = {"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist."}}
        mock_boto_client.get_object.side_effect = ClientError(error_response, "GetObject")

        with pytest.raises(S3NotFoundError):
            storage.load("non-existent-key")

    def test_load_client_error_other(self) -> None:
        """Test load operation with other client errors."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Simulate AccessDenied error
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied."}}
        mock_boto_client.get_object.side_effect = ClientError(error_response, "GetObject")

        with pytest.raises(S3StorageError):
            storage.load("test-key")

    def test_delete_success(self) -> None:
        """Test successful data deletion."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.delete_object.return_value = {}

        result = storage.delete("test-key")

        assert result.success is True
        mock_boto_client.delete_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")

    def test_delete_no_connection(self) -> None:
        """Test delete operation when connection is not available."""
        storage = ConcreteBaseS3Storage()
        storage.connection_manager = None  # No connection

        with pytest.raises(S3ConnectionError, match="S3 service unavailable"):
            storage.delete("test-key")

    def test_delete_not_found(self) -> None:
        """Test deleting non-existent key."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Simulate NoSuchKey error
        error_response = {"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist."}}
        mock_boto_client.delete_object.side_effect = ClientError(error_response, "DeleteObject")

        result = storage.delete("non-existent-key")
        assert result.success is False

    def test_ensure_connection_success(self) -> None:
        """Test successful connection validation."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        storage.connection_manager = mock_connection_manager

        # Should not raise any exception
        storage._ensure_connection()

    def test_ensure_connection_no_manager(self) -> None:
        """Test connection validation with no connection manager."""
        storage = ConcreteBaseS3Storage()
        storage.connection_manager = None

        with pytest.raises(S3ConnectionError, match="S3 service unavailable"):
            storage._ensure_connection()

    def test_ensure_connection_no_client(self) -> None:
        """Test connection validation with connection manager but no client."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = None
        storage.connection_manager = mock_connection_manager

        with pytest.raises(S3ConnectionError, match="S3 service unavailable"):
            storage._ensure_connection()

    def test_store_with_metadata(self) -> None:
        """Test storing data with metadata."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.put_object.return_value = {}

        metadata = {"source": "test", "version": "1.0"}
        result = storage.store("test-key", {"data": "value"}, metadata=metadata)

        assert result.success is True
        call_args = mock_boto_client.put_object.call_args
        assert call_args[1]["Metadata"] == metadata

    def test_load_with_json_parsing_error(self) -> None:
        """Test load operation when JSON parsing fails."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_response = {
            "Body": MagicMock(),
            "ContentType": "application/json"
        }
        mock_response["Body"].read.return_value = b"invalid json content"
        mock_boto_client.get_object.return_value = mock_response

        with pytest.raises(S3StorageError):
            storage.load("test-key")

    def test_store_client_error(self) -> None:
        """Test store operation with ClientError."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Simulate AccessDenied error
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied."}}
        mock_boto_client.put_object.side_effect = ClientError(error_response, "PutObject")

        with pytest.raises(S3StorageError):
            storage.store("test-key", {"data": "value"})

    def test_store_general_exception(self) -> None:
        """Test store operation with general exception."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.put_object.side_effect = Exception("Network error")

        with pytest.raises(S3StorageError, match="Store failed: Network error"):
            storage.store("test-key", {"data": "value"})

    def test_load_general_exception(self) -> None:
        """Test load operation with general exception."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.get_object.side_effect = Exception("Network error")

        with pytest.raises(S3StorageError, match="Load failed: Network error"):
            storage.load("test-key")

    def test_delete_client_error(self) -> None:
        """Test delete operation with ClientError."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Simulate AccessDenied error
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied."}}
        mock_boto_client.delete_object.side_effect = ClientError(error_response, "DeleteObject")

        with pytest.raises(S3StorageError):
            storage.delete("test-key")

    def test_delete_general_exception(self) -> None:
        """Test delete operation with general exception."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.delete_object.side_effect = Exception("Network error")

        with pytest.raises(S3StorageError, match="Delete failed: Network error"):
            storage.delete("test-key")

    def test_exists_success(self) -> None:
        """Test exists operation success."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.head_object.return_value = {}

        result = storage.exists("test-key")

        assert result is True
        mock_boto_client.head_object.assert_called_once_with(Bucket="test-bucket", Key="test-key")

    def test_exists_not_found(self) -> None:
        """Test exists operation when key not found."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Simulate NoSuchKey error
        error_response = {"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist."}}
        mock_boto_client.head_object.side_effect = ClientError(error_response, "HeadObject")

        result = storage.exists("test-key")

        assert result is False

    def test_exists_error(self) -> None:
        """Test exists operation with other errors."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        # Simulate AccessDenied error
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied."}}
        mock_boto_client.head_object.side_effect = ClientError(error_response, "HeadObject")

        with pytest.raises(S3StorageError):
            storage.exists("test-key")

    def test_store_with_pydantic_model(self) -> None:
        """Test storing data with Pydantic model."""
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str
            value: int

        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.put_object.return_value = {}

        test_model = TestModel(name="test", value=42)
        result = storage.store("test-key", test_model)

        assert result.success is True
        call_args = mock_boto_client.put_object.call_args
        assert json.loads(call_args[1]["Body"]) == {"name": "test", "value": 42}

    def test_store_with_unknown_data_type(self) -> None:
        """Test storing data with unknown type."""
        storage = ConcreteBaseS3Storage()
        mock_connection_manager = MagicMock()
        mock_boto_client = MagicMock()
        mock_connection_manager.boto_client = mock_boto_client
        storage.connection_manager = mock_connection_manager

        mock_boto_client.put_object.return_value = {}

        # Custom object without model_dump
        class CustomObject:
            def __str__(self):
                return "custom string"

        result = storage.store("test-key", CustomObject())

        assert result.success is True
        call_args = mock_boto_client.put_object.call_args
        assert call_args[1]["Body"] == b"custom string"