"""Unit tests for S3 client revision methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.config.s3 import S3Config
from models.data.infrastructure.s3 import S3RevisionData
from models.infrastructure.s3.client import MyS3Client


class TestS3ClientRevisions:
    """Unit tests for S3 client revision methods."""

    def test_write_revision_success(self):
        """Test successful revision write via S3 client."""
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

            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage
            mock_revision_storage.store_revision.return_value = MagicMock(success=True)

            with patch(
                "models.infrastructure.s3.client.RevisionData"
            ) as mock_revision_data_class:
                with patch(
                    "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string"
                ) as mock_hash:
                    mock_hash.return_value = 1234567890

                    mock_revision_instance = MagicMock()
                    mock_revision_data_class.return_value = mock_revision_instance
                    mock_revision_instance.model_dump.return_value = {
                        "entity": {"id": "Q42"}
                    }
                    mock_revision_instance.schema_version = "1.0.0"
                    mock_revision_instance.created_at = "2023-01-01T00:00:00Z"

                    client.write_revision(mock_revision_instance)

                    mock_hash.assert_called_once()
                    mock_revision_storage.store_revision.assert_called_once()

    def test_store_revision_success(self) -> None:
        """Test successful revision storage via S3 client."""
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
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

            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage
            mock_revision_storage.store_revision.return_value = MagicMock(success=True)

            revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z",
            )

            client.store_revision(12345, revision_data)

            mock_revision_storage.store_revision.assert_called_once_with(
                12345, revision_data
            )

    def test_load_revision_success(self) -> None:
        """Test successful revision loading via S3 client."""
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
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

            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage

            expected_revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z",
            )
            mock_revision_storage.load_revision.return_value = expected_revision_data

            result = client.load_revision(12345)

            assert result == expected_revision_data
            mock_revision_storage.load_revision.assert_called_once_with(12345)

    def test_read_revision_with_content_hash(self):
        """Test read_revision queries content_hash and loads from S3."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            mock_revision_repo = MagicMock()
            mock_revision_repo.get_content_hash.return_value = 12345678901234567890

            mock_revision_storage = MagicMock()
            expected_revision_data = {"entity": {"id": "Q42"}}
            mock_revision_storage.load_revision.return_value = expected_revision_data
            client.revisions = mock_revision_storage

            with patch(
                "models.infrastructure.s3.client.RevisionRepository",
                return_value=mock_revision_repo,
            ):
                result = client.read_revision("Q42", 1)

            assert result == expected_revision_data
            mock_id_resolver.resolve_id.assert_called_once_with("Q42")
            mock_revision_repo.get_content_hash.assert_called_once_with(123, 1)
            mock_revision_storage.load_revision.assert_called_once_with(
                12345678901234567890
            )

    def test_read_revision_entity_not_found(self):
        """Test read_revision raises 404 when entity not found."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            with pytest.raises(Exception):
                client.read_revision("Q999", 1)

    def test_read_revision_revision_not_found(self):
        """Test read_revision raises 404 when revision not found."""
        mock_connection_manager = MagicMock()
        config = S3Config(
            endpoint_url="http://localhost:4566",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.id_resolver = mock_id_resolver

        with patch(
            "models.infrastructure.s3.client.S3ConnectionManager",
            return_value=mock_connection_manager,
        ):
            client = MyS3Client(config=config, vitess_client=mock_vitess_client)

            mock_revision_repo = MagicMock()
            mock_revision_repo.get_content_hash.return_value = 0

            with patch(
                "models.infrastructure.s3.client.RevisionRepository",
                return_value=mock_revision_repo,
            ):
                with pytest.raises(Exception):
                    client.read_revision("Q42", 999)

    def test_read_revision_vitess_client_none(self):
        """Test read_revision raises 503 when vitess_client is None."""
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
            client = MyS3Client(config=config, vitess_client=None)

            with pytest.raises(Exception):
                client.read_revision("Q42", 1)

    def test_store_revision_revisions_none(self):
        """Test store_revision initializes revisions when None."""
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
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
            client.revisions = None

            with patch(
                "models.infrastructure.s3.storage.revision_storage.RevisionStorage"
            ) as mock_storage_class:
                mock_storage = MagicMock()
                mock_storage.store_revision.return_value = MagicMock(success=True)
                mock_storage_class.return_value = mock_storage

                revision_data = S3RevisionData(
                    schema="1.0.0",
                    revision={"entity": {"id": "Q42"}},
                    hash=12345,
                    created_at="2023-01-01T12:00:00Z",
                )

                client.store_revision(12345, revision_data)

                mock_storage_class.assert_called_once()

    def test_store_revision_failure(self):
        """Test store_revision raises error when storage fails."""
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
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

            mock_revision_storage = MagicMock()
            client.revisions = mock_revision_storage
            mock_revision_storage.store_revision.return_value = MagicMock(
                success=False, error="Storage full"
            )

            revision_data = S3RevisionData(
                schema="1.0.0",
                revision={"entity": {"id": "Q42"}},
                hash=12345,
                created_at="2023-01-01T12:00:00Z",
            )

            with pytest.raises(Exception):
                client.store_revision(12345, revision_data)

    def test_load_revision_revisions_none(self):
        """Test load_revision initializes revisions when None."""
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
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
            client.revisions = None

            with patch(
                "models.infrastructure.s3.storage.revision_storage.RevisionStorage"
            ) as mock_storage_class:
                mock_storage = MagicMock()
                mock_storage.load_revision.return_value = S3RevisionData(
                    schema="1.0.0",
                    revision={"entity": {"id": "Q42"}},
                    hash=12345,
                    created_at="2023-01-01T12:00:00Z",
                )
                mock_storage_class.return_value = mock_storage

                result = client.load_revision(12345)

                assert result is not None
                mock_storage_class.assert_called_once()
