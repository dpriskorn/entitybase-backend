import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError

pytestmark = pytest.mark.unit

from models.infrastructure.s3.s3_client import S3Client
from models.s3_models import S3Config


class TestS3Client:
    @pytest.fixture
    def config(self):
        return S3Config(
            endpoint_url="http://localhost:9000",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

    @pytest.fixture
    def mock_connection_manager(self):
        return MagicMock()

    @patch("models.infrastructure.s3.s3_client.S3ConnectionManager")
    def test_init_success(self, mock_manager_class, config, mock_connection_manager):
        """Test S3Client initialization success."""
        mock_manager_class.return_value = mock_connection_manager

        client = S3Client(config)

        assert client.config == config
        assert client.connection_manager == mock_connection_manager
        mock_manager_class.assert_called_once_with(config=config)
        mock_connection_manager.connect.assert_called_once()
        # _ensure_bucket_exists would be called

    @patch("models.infrastructure.s3.s3_client.S3ConnectionManager")
    def test_ensure_bucket_exists_bucket_exists(
        self, mock_manager_class, config, mock_connection_manager
    ):
        """Test _ensure_bucket_exists when bucket exists."""
        mock_manager_class.return_value = mock_connection_manager
        mock_connection_manager.boto_client.head_bucket.return_value = None

        client = S3Client(config)

        mock_connection_manager.boto_client.head_bucket.assert_called_once_with(
            Bucket="test-bucket"
        )

    @patch("models.infrastructure.s3.s3_client.S3ConnectionManager")
    @patch("models.infrastructure.s3.s3_client.raise_validation_error")
    def test_ensure_bucket_exists_bucket_missing(
        self, mock_raise, mock_manager_class, config, mock_connection_manager
    ):
        """Test _ensure_bucket_exists when bucket doesn't exist."""
        mock_manager_class.return_value = mock_connection_manager
        error = ClientError({"Error": {"Code": "NoSuchBucket"}}, "HeadBucket")
        mock_connection_manager.boto_client.head_bucket.side_effect = error
        mock_connection_manager.boto_client.create_bucket.return_value = None

        client = S3Client(config)

        mock_connection_manager.boto_client.create_bucket.assert_called_once_with(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "us-east-1"},
        )

    @patch("models.infrastructure.s3.s3_client.S3ConnectionManager")
    def test_ensure_bucket_exists_no_client(self, mock_manager_class, config):
        """Test _ensure_bucket_exists when no boto client."""
        mock_manager_class.return_value = None

        with pytest.raises(ValueError) as exc_info:
            S3Client(config)

        assert "S3 service unavailable" in str(exc_info.value)

    def test_read_revision(self, config, mock_connection_manager):
        """Test read_revision method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager
            mock_connection_manager.boto_client.get_object.return_value = {
                "Body": MagicMock(),
                "Metadata": {"schema_version": "1.0", "created_at": "2023-01-01"},
            }
            mock_body = MagicMock()
            mock_body.read.return_value = (
                b'{"schema_version": "1.0", "entity": {"id": "Q42", "type": "item"}}'
            )
            mock_connection_manager.boto_client.get_object.return_value["Body"] = (
                mock_body
            )

            client = S3Client(config)
            result = client.read_revision("Q42", 123)

            assert result.content == {"id": "Q42", "type": "item"}
            assert result.schema_version == "1.0"
            assert result.created_at == "2023-01-01"
            mock_connection_manager.boto_client.get_object.assert_called_once_with(
                Bucket="test-bucket", Key="entities/Q42/123.json"
            )

    def test_read_statement(self, config, mock_connection_manager):
        """Test read_statement method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager
            mock_connection_manager.boto_client.get_object.return_value = {
                "Body": MagicMock(),
                "Metadata": {"schema_version": "1.0", "created_at": "2023-01-01"},
            }
            mock_body = MagicMock()
            mock_body.read.return_value = b'{"schema_version": "1.0", "content_hash": 456, "statement": {"id": "P31"}, "created_at": "2023-01-01"}'
            mock_connection_manager.boto_client.get_object.return_value["Body"] = (
                mock_body
            )

            client = S3Client(config)
            result = client.read_statement(456)

            assert result.statement == {"id": "P31"}
            assert result.schema_version == "1.0"
            assert result.created_at == "2023-01-01"
            mock_connection_manager.boto_client.get_object.assert_called_once_with(
                Bucket="test-bucket", Key="statements/456.json"
            )

    def test_write_revision(self, config, mock_connection_manager):
        """Test write_revision method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.write_revision("Q42", 123, {"entity": {"id": "Q42"}}, "1.0")

            mock_connection_manager.boto_client.put_object.assert_called_once()
            call_args = mock_connection_manager.boto_client.put_object.call_args
            assert call_args[1]["Bucket"] == "test-bucket"
            assert call_args[1]["Key"] == "entities/Q42/123.json"
            assert call_args[1]["Metadata"]["schema_version"] == "1.0"
            assert "Body" in call_args[1]

    def test_write_statement(self, config, mock_connection_manager):
        """Test write_statement method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            # Mock the verification get_object
            mock_connection_manager.boto_client.get_object.return_value = {
                "Body": MagicMock()
            }
            mock_verify_body = MagicMock()
            mock_verify_body.read.return_value = b'{"schema_version": "1.0", "content_hash": 456, "statement": {"id": "P31"}, "created_at": "2023-01-01T12:00:00"}'
            mock_connection_manager.boto_client.get_object.return_value["Body"] = (
                mock_verify_body
            )

            client = S3Client(config)
            client.write_statement(456, {"statement": {"id": "P31"}}, "1.0")

            mock_connection_manager.boto_client.put_object.assert_called_once()
            call_args = mock_connection_manager.boto_client.put_object.call_args
            assert call_args[1]["Bucket"] == "test-bucket"
            assert call_args[1]["Key"] == "statements/456.json"
            assert call_args[1]["Metadata"]["schema_version"] == "1.0"

    @patch("models.infrastructure.s3.s3_client.datetime")
    def test_write_revision_with_timestamp(
        self, mock_datetime, config, mock_connection_manager
    ):
        """Test write_revision includes created_at timestamp."""
        mock_datetime.now.return_value = MagicMock()
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"

        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.write_revision("Q42", 123, {"entity": {"id": "Q42"}}, "1.0")

            call_args = mock_connection_manager.boto_client.put_object.call_args
            assert call_args[1]["Metadata"]["created_at"] == "2023-01-01T12:00:00"

    def test_load_metadata(self, config, mock_connection_manager):
        """Test load_metadata method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager
            mock_connection_manager.boto_client.get_object.return_value = {
                "Body": MagicMock()
            }
            mock_body = MagicMock()
            mock_body.read.return_value = b"test label"
            mock_connection_manager.boto_client.get_object.return_value["Body"] = (
                mock_body
            )

            client = S3Client(config)
            result = client.load_metadata("labels", 789)

            assert result == "test label"
            mock_connection_manager.boto_client.get_object.assert_called_once_with(
                Bucket="wikibase-terms", Key="789"
            )

    def test_mark_published(self, config, mock_connection_manager):
        """Test mark_published method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.mark_published("Q42", 123, "published")

            mock_connection_manager.boto_client.copy_object.assert_called_once()
            call_args = mock_connection_manager.boto_client.copy_object.call_args
            assert call_args[1]["Bucket"] == "test-bucket"
            assert call_args[1]["Key"] == "entities/Q42/123.json"
            assert call_args[1]["CopySource"] == {
                "Bucket": "test-bucket",
                "Key": "entities/Q42/123.json",
            }
            assert call_args[1]["Metadata"] == {"publication_state": "published"}
            assert call_args[1]["MetadataDirective"] == "REPLACE"

    def test_read_full_revision(self, config, mock_connection_manager):
        """Test read_full_revision method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager
            mock_connection_manager.boto_client.get_object.return_value = {
                "Body": MagicMock(),
                "Metadata": {"schema_version": "1.0", "created_at": "2023-01-01"},
            }
            mock_body = MagicMock()
            mock_body.read.return_value = b'{"schema_version": "1.0", "entity": {"id": "Q42"}, "redirects_to": null}'
            mock_connection_manager.boto_client.get_object.return_value["Body"] = (
                mock_body
            )

            client = S3Client(config)
            result = client.read_full_revision("Q42", 123)

            assert result["entity"]["id"] == "Q42"
            assert result["redirects_to"] is None
            mock_connection_manager.boto_client.get_object.assert_called_once_with(
                Bucket="test-bucket", Key="entities/Q42/123.json"
            )

    def test_delete_statement(self, config, mock_connection_manager):
        """Test delete_statement method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.delete_statement(456)

            mock_connection_manager.boto_client.delete_object.assert_called_once_with(
                Bucket="test-bucket", Key="statements/456.json"
            )

    def test_write_entity_revision(self, config, mock_connection_manager):
        """Test write_entity_revision method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.write_entity_revision("Q42", 123, {"entity": {"id": "Q42"}}, "1.0")

            mock_connection_manager.boto_client.put_object.assert_called_once()
            call_args = mock_connection_manager.boto_client.put_object.call_args
            assert call_args[1]["Bucket"] == "test-bucket"
            assert call_args[1]["Key"] == "entities/Q42/123.json"
            assert call_args[1]["Metadata"]["schema_version"] == "1.0"

    def test_delete_metadata(self, config, mock_connection_manager):
        """Test delete_metadata method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.delete_metadata("labels", 789)

            mock_connection_manager.boto_client.delete_object.assert_called_once_with(
                Bucket="wikibase-terms", Key="labels/789"
            )

    def test_store_term_metadata(self, config, mock_connection_manager):
        """Test store_term_metadata method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.store_term_metadata("test label", 789)

            mock_connection_manager.boto_client.put_object.assert_called_once()
            call_args = mock_connection_manager.boto_client.put_object.call_args
            assert call_args[1]["Bucket"] == "wikibase-terms"
            assert call_args[1]["Key"] == "789"
            assert call_args[1]["Body"] == b"test label"

    def test_load_term_metadata(self, config, mock_connection_manager):
        """Test load_term_metadata method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager
            mock_connection_manager.boto_client.get_object.return_value = {
                "Body": MagicMock()
            }
            mock_body = MagicMock()
            mock_body.read.return_value = b"test label"
            mock_connection_manager.boto_client.get_object.return_value["Body"] = (
                mock_body
            )

            client = S3Client(config)
            result = client.load_term_metadata(789)

            assert result == "test label"
            mock_connection_manager.boto_client.get_object.assert_called_once_with(
                Bucket="wikibase-terms", Key="789"
            )

    def test_store_sitelink_metadata(self, config, mock_connection_manager):
        """Test store_sitelink_metadata method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager

            client = S3Client(config)
            client.store_sitelink_metadata("test title", 789)

            mock_connection_manager.boto_client.put_object.assert_called_once()
            call_args = mock_connection_manager.boto_client.put_object.call_args
            assert call_args[1]["Bucket"] == "wikibase-terms"
            assert call_args[1]["Key"] == "sitelinks/789"
            assert call_args[1]["Body"] == b"test title"

    def test_load_sitelink_metadata(self, config, mock_connection_manager):
        """Test load_sitelink_metadata method."""
        with patch(
            "models.infrastructure.s3.s3_client.S3ConnectionManager"
        ) as mock_manager_class:
            mock_manager_class.return_value = mock_connection_manager
            mock_connection_manager.boto_client.get_object.return_value = {
                "Body": MagicMock()
            }
            mock_body = MagicMock()
            mock_body.read.return_value = b"test title"
            mock_connection_manager.boto_client.get_object.return_value["Body"] = (
                mock_body
            )

            client = S3Client(config)
            result = client.load_sitelink_metadata(789)

            assert result == "test title"
            mock_connection_manager.boto_client.get_object.assert_called_once_with(
                Bucket="wikibase-terms", Key="sitelinks/789"
            )
