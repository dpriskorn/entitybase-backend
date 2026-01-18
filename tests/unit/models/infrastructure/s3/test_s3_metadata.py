from typing import Any, Dict
from unittest.mock import Mock, patch
from models.infrastructure.s3.s3_client import MyS3Client
from models.s3_models import S3Config


class TestS3MetadataStorage:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = S3Config(
            endpoint_url="http://minio:9000",
            access_key="test",
            secret_key="test",
            bucket="test",
        )
        with (
            patch("models.infrastructure.s3.s3_client.BotoSession"),
            patch(
                "models.infrastructure.s3.connection.S3ConnectionManager"
            ) as mock_conn_mgr,
        ):
            mock_conn_mgr.return_value.connect = Mock()
            mock_conn_mgr.return_value.boto_client = Mock()
            self.s3_client = MyS3Client(self.config)

    def test_store_metadata(self) -> None:
        """Test storing metadata in S3."""
        metadata = {"en": {"language": "en", "value": "Test"}}

        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            self.s3_client.store_metadata("labels", 12345, metadata)

            mock_boto.put_object.assert_called_once_with(
                Bucket="test",
                Key="metadata/labels/12345.json",
                Body='{"en": {"language": "en", "value": "Test"}}',
                Metadata={"content_type": "labels", "content_hash": "12345"},
            )

    def test_load_metadata_success(self) -> None:
        """Test loading existing metadata from S3."""
        mock_response = {"Body": Mock()}
        mock_response[
            "Body"
        ].read.return_value = b'{"en": {"language": "en", "value": "Test"}}'

        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            mock_boto.get_object.return_value = mock_response

            result = self.s3_client.load_metadata("labels", 12345)

            mock_boto.get_object.assert_called_once_with(
                Bucket="test", Key="metadata/labels/12345.json"
            )
            assert result == {"en": {"language": "en", "value": "Test"}}

    def test_load_metadata_not_found(self) -> None:
        """Test loading non-existent metadata from S3."""
        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            mock_boto.get_object.side_effect = (
                self.s3_client.connection_manager.boto_client.exceptions.NoSuchKey({})
            )

            result = self.s3_client.load_metadata("labels", 12345)

            assert result == {}

    def test_load_metadata_error(self) -> None:
        """Test loading metadata with general error."""
        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            mock_boto.get_object.side_effect = Exception("Network error")

            result = self.s3_client.load_metadata("labels", 12345)

            assert result == {}

    def test_delete_metadata(self) -> None:
        """Test deleting metadata from S3."""
        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            self.s3_client.delete_metadata("labels", 12345)

            mock_boto.delete_object.assert_called_once_with(
                Bucket="test", Key="metadata/labels/12345.json"
            )

    def test_delete_metadata_error(self) -> None:
        """Test deleting metadata with error (should not raise)."""
        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            mock_boto.delete_object.side_effect = Exception("Delete failed")

            # Should not raise
            self.s3_client.delete_metadata("labels", 12345)

            mock_boto.delete_object.assert_called_once()

    def test_store_metadata_empty(self) -> None:
        """Test storing empty metadata."""
        metadata: Dict[str, Any] = {}

        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            self.s3_client.store_metadata("labels", 12345, metadata)

            mock_boto.put_object.assert_called_once_with(
                Bucket="test",
                Key="metadata/labels/12345.json",
                Body="{}",
                Metadata={"content_type": "labels", "content_hash": "12345"},
            )

    def test_load_metadata_malformed_json(self) -> None:
        """Test loading metadata with malformed JSON."""
        mock_response = {"Body": Mock()}
        mock_response["Body"].read.return_value = b"invalid json"

        with patch.object(
            self.s3_client.connection_manager, "boto_client"
        ) as mock_boto:
            mock_boto.get_object.return_value = mock_response

            result = self.s3_client.load_metadata("labels", 12345)

            assert result == {}  # Should return empty dict on error
