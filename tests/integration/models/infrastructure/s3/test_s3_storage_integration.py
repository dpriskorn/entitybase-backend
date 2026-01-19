import pytest
from moto import mock_s3
import boto3
import json

from models.infrastructure.s3.storage.revision_storage import RevisionStorage
from models.infrastructure.s3.storage.statement_storage import StatementStorage
from models.infrastructure.s3.storage.metadata_storage import MetadataStorage
from models.infrastructure.s3.storage.qualifier_storage import QualifierStorage
from models.infrastructure.s3.storage.reference_storage import ReferenceStorage
from models.infrastructure.s3.config import S3Config
from models.infrastructure.s3.enums import EntityType, EditType
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.s3.hashes.hash_maps import HashMaps
from models.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes


@pytest.fixture
def s3_config():
    """S3 configuration for testing."""
    return S3Config(
        endpoint_url="http://localhost:9000",
        access_key="test",
        secret_key="test",
        bucket="test-wikibase-revisions",
        region="us-east-1",
    )


@pytest.fixture
def s3_connection_manager(s3_config):
    """S3 connection manager for testing."""
    from models.infrastructure.s3.connection import S3ConnectionManager
    return S3ConnectionManager(s3_config)


@mock_s3
class TestRevisionStorageIntegration:
    """Integration tests for RevisionStorage."""

    @pytest.fixture(autouse=True)
    def setup_s3(self, s3_config):
        """Set up moto S3 mock."""
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region,
        )
        s3_client.create_bucket(Bucket=s3_config.bucket)

    def test_write_and_read_revision(self, s3_connection_manager):
        """Test writing and reading revision data."""
        storage = RevisionStorage(s3_connection_manager)

        revision_data = RevisionData(
            entity_id="Q42",
            revision_id=1,
            type=EntityType.ITEM,
            statements=[],
            statements_hashes=StatementsHashes(hashes={}),
            qualifiers=[],
            references=[],
            sitelinks=[],
            edit_type=EditType.CREATE,
            labels_hashes=LabelsHashes(hashes={}),
            descriptions_hashes=DescriptionsHashes(hashes={}),
            aliases_hashes=AliasesHashes(hashes={}),
            sitelinks_hashes=SitelinksHashes(hashes={}),
            hash_maps=HashMaps(
                statements=StatementsHashes(hashes={}),
                labels=LabelsHashes(hashes={}),
                descriptions=DescriptionsHashes(hashes={}),
                aliases=AliasesHashes(hashes={}),
                sitelinks=SitelinksHashes(hashes={}),
            ),
        )

        # Write revision
        result = storage.write("Q42", 1, revision_data)
        assert result.success is True

        # Read revision
        read_result = storage.read("Q42", 1)
        assert read_result is not None
        assert read_result.entity_id == "Q42"
        assert read_result.revision_id == 1

    def test_read_nonexistent_revision(self, s3_connection_manager):
        """Test reading non-existent revision."""
        storage = RevisionStorage(s3_connection_manager)

        result = storage.read("Q999", 999)
        assert result is None


@mock_s3
class TestStatementStorageIntegration:
    """Integration tests for StatementStorage."""

    @pytest.fixture(autouse=True)
    def setup_s3(self, s3_config):
        """Set up moto S3 mock."""
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region,
        )
        s3_client.create_bucket(Bucket=s3_config.bucket)

    def test_write_and_read_statements(self, s3_connection_manager):
        """Test writing and reading statements."""
        storage = StatementStorage(s3_connection_manager)

        statements = [
            {
                "id": "S1",
                "rank": "normal",
                "mainsnak": {"property": "P31", "value": "Q5"},
                "qualifiers": [],
                "references": [],
            }
        ]

        # Write statements
        result = storage.write("Q42", 1, statements)
        assert result.success is True

        # Read statements
        read_result = storage.read("Q42", 1)
        assert read_result is not None
        assert len(read_result) == 1
        assert read_result[0]["id"] == "S1"


@mock_s3
class TestMetadataStorageIntegration:
    """Integration tests for MetadataStorage."""

    @pytest.fixture(autouse=True)
    def setup_s3(self, s3_config):
        """Set up moto S3 mock."""
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region,
        )
        s3_client.create_bucket(Bucket=s3_config.bucket)

    def test_write_and_read_metadata(self, s3_connection_manager):
        """Test writing and reading metadata."""
        storage = MetadataStorage(s3_connection_manager)

        metadata = {
            "labels": {"en": "Test Item", "de": "Testartikel"},
            "descriptions": {"en": "A test item"},
            "aliases": {"en": ["test", "example"]},
        }

        # Write metadata
        result = storage.write("Q42", 1, metadata)
        assert result.success is True

        # Read metadata
        read_result = storage.read("Q42", 1)
        assert read_result is not None
        assert read_result["labels"]["en"] == "Test Item"


@mock_s3
class TestQualifierStorageIntegration:
    """Integration tests for QualifierStorage."""

    @pytest.fixture(autouse=True)
    def setup_s3(self, s3_config):
        """Set up moto S3 mock."""
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region,
        )
        s3_client.create_bucket(Bucket=s3_config.bucket)

    def test_write_and_read_qualifiers(self, s3_connection_manager):
        """Test writing and reading qualifiers."""
        storage = QualifierStorage(s3_connection_manager)

        qualifiers = [
            {
                "property": "P580",
                "value": "2020-01-01",
                "hash": "qualifier_hash_1",
            }
        ]

        # Write qualifiers
        result = storage.write("Q42", 1, qualifiers)
        assert result.success is True

        # Read qualifiers
        read_result = storage.read("Q42", 1)
        assert read_result is not None
        assert len(read_result) == 1
        assert read_result[0]["property"] == "P580"


@mock_s3
class TestReferenceStorageIntegration:
    """Integration tests for ReferenceStorage."""

    @pytest.fixture(autouse=True)
    def setup_s3(self, s3_config):
        """Set up moto S3 mock."""
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region,
        )
        s3_client.create_bucket(Bucket=s3_config.bucket)

    def test_write_and_read_references(self, s3_connection_manager):
        """Test writing and reading references."""
        storage = ReferenceStorage(s3_connection_manager)

        references = [
            {
                "snaks": {"P854": ["http://example.com"]},
                "hash": "reference_hash_1",
            }
        ]

        # Write references
        result = storage.write("Q42", 1, references)
        assert result.success is True

        # Read references
        read_result = storage.read("Q42", 1)
        assert read_result is not None
        assert len(read_result) == 1
        assert "snaks" in read_result[0]


@mock_s3
class TestS3StorageErrorHandling:
    """Test error handling in S3 storage operations."""

    def test_bucket_not_exists(self, s3_config):
        """Test operations when bucket doesn't exist."""
        # Don't create bucket
        from models.infrastructure.s3.connection import S3ConnectionManager
        manager = S3ConnectionManager(s3_config)

        storage = RevisionStorage(manager)

        # This should handle the error gracefully
        result = storage.read("Q42", 1)
        assert result is None

    def test_invalid_json_handling(self, s3_config):
        """Test handling of invalid JSON in stored data."""
        # Set up S3 with invalid JSON
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region,
        )
        s3_client.create_bucket(Bucket=s3_config.bucket)

        # Put invalid JSON directly
        key = f"revisions/Q42/1.json"
        s3_client.put_object(Bucket=s3_config.bucket, Key=key, Body="invalid json")

        from models.infrastructure.s3.connection import S3ConnectionManager
        manager = S3ConnectionManager(s3_config)
        storage = RevisionStorage(manager)

        # Reading should handle the error
        result = storage.read("Q42", 1)
        assert result is None  # Should return None on parse error</content>
<parameter name="filePath">/home/dpriskorn/src/python/wikibase-backend/tests/integration/models/infrastructure/s3/test_s3_storage_integration.py