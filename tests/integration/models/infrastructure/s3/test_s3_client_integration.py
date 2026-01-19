import pytest
from moto import mock_s3
import boto3
from unittest.mock import MagicMock

from models.common import OperationResult
from models.infrastructure.s3.s3_client import MyS3Client
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
def mock_vitess_client():
    """Mock vitess client for integration tests."""
    client = MagicMock()
    client.get_head_revision.return_value = OperationResult(success=True, data=0)
    return client


@mock_s3
class TestS3ClientIntegration:
    """Integration tests for MyS3Client using moto S3 mock."""

    @pytest.fixture(autouse=True)
    def setup_s3(self, s3_config):
        """Set up moto S3 mock."""
        # Create the bucket
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            region_name=s3_config.region,
        )
        s3_client.create_bucket(Bucket=s3_config.bucket)

    def test_s3_client_initialization(self, s3_config):
        """Test S3 client initializes correctly."""
        client = MyS3Client(s3_config)

        assert client.config == s3_config
        assert client.connection_manager is not None
        assert client.revisions is not None
        assert client.statements is not None
        assert client.metadata is not None
        assert client.references is not None
        assert client.qualifiers is not None

    def test_write_and_read_revision(self, s3_config):
        """Test writing and reading a revision."""
        client = MyS3Client(s3_config)

        # Create test revision data
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
        result = client.write_revision("Q42", 1, revision_data)
        assert result.success is True

        # Read revision back
        read_result = client.read_revision("Q42", 1)
        assert read_result is not None
        assert read_result.entity_id == "Q42"
        assert read_result.revision_id == 1
        assert read_result.type == EntityType.ITEM

    def test_write_and_read_statements(self, s3_config):
        """Test writing and reading statements."""
        client = MyS3Client(s3_config)

        statements_data = [
            {
                "id": "S1",
                "rank": "normal",
                "mainsnak": {"property": "P31", "value": "Q5"},
                "qualifiers": [],
                "references": [],
            }
        ]

        # Write statements
        result = client.write_statements("Q42", 1, statements_data)
        assert result.success is True

        # Read statements back
        read_result = client.read_statements("Q42", 1)
        assert read_result is not None
        assert len(read_result) == 1
        assert read_result[0]["id"] == "S1"

    def test_write_and_read_qualifiers(self, s3_config):
        """Test writing and reading qualifiers."""
        client = MyS3Client(s3_config)

        qualifiers_data = [
            {
                "property": "P580",
                "value": "2020-01-01",
                "hash": "qualifier_hash_1",
            }
        ]

        # Write qualifiers
        result = client.write_qualifiers("Q42", 1, qualifiers_data)
        assert result.success is True

        # Read qualifiers back
        read_result = client.read_qualifiers("Q42", 1)
        assert read_result is not None
        assert len(read_result) == 1
        assert read_result[0]["property"] == "P580"

    def test_write_and_read_references(self, s3_config):
        """Test writing and reading references."""
        client = MyS3Client(s3_config)

        references_data = [
            {
                "snaks": {"P854": ["http://example.com"]},
                "hash": "reference_hash_1",
            }
        ]

        # Write references
        result = client.write_references("Q42", 1, references_data)
        assert result.success is True

        # Read references back
        read_result = client.read_references("Q42", 1)
        assert read_result is not None
        assert len(read_result) == 1
        assert "snaks" in read_result[0]

    def test_write_and_read_metadata(self, s3_config):
        """Test writing and reading metadata."""
        client = MyS3Client(s3_config)

        metadata = {
            "labels": {"en": "Test Item"},
            "descriptions": {"en": "A test item"},
        }

        # Write metadata
        result = client.write_metadata("Q42", 1, metadata)
        assert result.success is True

        # Read metadata back
        read_result = client.load_metadata("Q42", 1)
        assert read_result is not None
        assert read_result.get("labels", {}).get("en") == "Test Item"

    def test_nonexistent_revision(self, s3_config):
        """Test reading non-existent revision."""
        client = MyS3Client(s3_config)

        read_result = client.read_revision("Q999", 999)
        assert read_result is None

    def test_bucket_operations(self, s3_config):
        """Test bucket existence and operations."""
        client = MyS3Client(s3_config)

        # Test bucket exists
        assert client.bucket_exists()

        # Test getting bucket name
        assert client.get_bucket_name() == s3_config.bucket

    def test_s3_connection_error_handling(self, s3_config):
        """Test error handling when S3 is unavailable."""
        # Create config with invalid endpoint
        bad_config = S3Config(
            endpoint_url="http://nonexistent:9999",
            access_key="test",
            secret_key="test",
            bucket="test-bucket",
            region="us-east-1",
        )

        # This should handle connection errors gracefully
        client = MyS3Client(bad_config)
        # The client should still initialize but operations may fail
        assert client.config == bad_config