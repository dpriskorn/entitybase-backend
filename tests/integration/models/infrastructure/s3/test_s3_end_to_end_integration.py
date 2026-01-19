import pytest
from moto import mock_s3
import boto3

from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.s3.config import S3Config
from models.infrastructure.s3.enums import EntityType, EditType, EditData
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


@mock_s3
class TestS3EndToEndIntegration:
    """End-to-end integration tests for S3 operations."""

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

    def test_full_entity_lifecycle_s3_operations(self, s3_config):
        """Test complete entity lifecycle with S3 operations."""
        client = MyS3Client(s3_config)

        entity_id = "Q12345"
        revision_id = 1

        # 1. Create revision data
        revision_data = RevisionData(
            entity_id=entity_id,
            revision_id=revision_id,
            type=EntityType.ITEM,
            statements=[
                {
                    "id": "S1",
                    "rank": "normal",
                    "mainsnak": {"property": "P31", "value": "Q5"},
                    "qualifiers": [
                        {
                            "property": "P580",
                            "value": "2020-01-01",
                            "hash": "qual_hash_1",
                        }
                    ],
                    "references": [
                        {
                            "snaks": {"P854": ["http://example.com"]},
                            "hash": "ref_hash_1",
                        }
                    ],
                }
            ],
            statements_hashes=StatementsHashes(hashes={"S1": "stmt_hash_1"}),
            qualifiers=[
                {
                    "property": "P580",
                    "value": "2020-01-01",
                    "hash": "qual_hash_1",
                }
            ],
            references=[
                {
                    "snaks": {"P854": ["http://example.com"]},
                    "hash": "ref_hash_1",
                }
            ],
            sitelinks=[
                {
                    "site": "enwiki",
                    "title": "Test Article",
                    "badges": [],
                }
            ],
            edit_type=EditType.CREATE,
            labels_hashes=LabelsHashes(hashes={"en": "label_hash_1"}),
            descriptions_hashes=DescriptionsHashes(hashes={"en": "desc_hash_1"}),
            aliases_hashes=AliasesHashes(hashes={"en": ["alias_hash_1"]}),
            sitelinks_hashes=SitelinksHashes(hashes={"enwiki": "sitelink_hash_1"}),
            hash_maps=HashMaps(
                statements=StatementsHashes(hashes={"S1": "stmt_hash_1"}),
                labels=LabelsHashes(hashes={"en": "label_hash_1"}),
                descriptions=DescriptionsHashes(hashes={"en": "desc_hash_1"}),
                aliases=AliasesHashes(hashes={"en": ["alias_hash_1"]}),
                sitelinks=SitelinksHashes(hashes={"enwiki": "sitelink_hash_1"}),
            ),
        )

        # 2. Write revision
        write_result = client.write_revision(entity_id, revision_id, revision_data)
        assert write_result.success is True

        # 3. Write metadata
        metadata = {
            "labels": {"en": "Test Item", "de": "Testartikel"},
            "descriptions": {"en": "A test item for integration testing"},
            "aliases": {"en": ["test item", "integration test"]},
        }
        metadata_result = client.write_metadata(entity_id, revision_id, metadata)
        assert metadata_result.success is True

        # 4. Read revision back
        read_revision = client.read_revision(entity_id, revision_id)
        assert read_revision is not None
        assert read_revision.entity_id == entity_id
        assert read_revision.revision_id == revision_id
        assert read_revision.type == EntityType.ITEM
        assert len(read_revision.statements) == 1

        # 5. Read metadata back
        read_metadata = client.load_metadata(entity_id, revision_id)
        assert read_metadata is not None
        assert read_metadata["labels"]["en"] == "Test Item"
        assert read_metadata["descriptions"]["en"] == "A test item for integration testing"

        # 6. Read statements
        read_statements = client.read_statements(entity_id, revision_id)
        assert read_statements is not None
        assert len(read_statements) == 1
        assert read_statements[0]["id"] == "S1"

        # 7. Read qualifiers
        read_qualifiers = client.read_qualifiers(entity_id, revision_id)
        assert read_qualifiers is not None
        assert len(read_qualifiers) == 1
        assert read_qualifiers[0]["property"] == "P580"

        # 8. Read references
        read_references = client.read_references(entity_id, revision_id)
        assert read_references is not None
        assert len(read_references) == 1
        assert "snaks" in read_references[0]

    def test_s3_data_consistency(self, s3_config):
        """Test data consistency across multiple revisions."""
        client = MyS3Client(s3_config)

        entity_id = "Q67890"

        # Revision 1
        rev1_data = RevisionData(
            entity_id=entity_id,
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

        # Write revision 1
        client.write_revision(entity_id, 1, rev1_data)

        # Revision 2 with changes
        rev2_data = RevisionData(
            entity_id=entity_id,
            revision_id=2,
            type=EntityType.ITEM,
            statements=[
                {
                    "id": "S1",
                    "rank": "normal",
                    "mainsnak": {"property": "P31", "value": "Q5"},
                    "qualifiers": [],
                    "references": [],
                }
            ],
            statements_hashes=StatementsHashes(hashes={"S1": "stmt_hash_1"}),
            qualifiers=[],
            references=[],
            sitelinks=[],
            edit_type=EditType.UPDATE,
            labels_hashes=LabelsHashes(hashes={}),
            descriptions_hashes=DescriptionsHashes(hashes={}),
            aliases_hashes=AliasesHashes(hashes={}),
            sitelinks_hashes=SitelinksHashes(hashes={}),
            hash_maps=HashMaps(
                statements=StatementsHashes(hashes={"S1": "stmt_hash_1"}),
                labels=LabelsHashes(hashes={}),
                descriptions=DescriptionsHashes(hashes={}),
                aliases=AliasesHashes(hashes={}),
                sitelinks=SitelinksHashes(hashes={}),
            ),
        )

        # Write revision 2
        client.write_revision(entity_id, 2, rev2_data)

        # Verify both revisions are accessible
        rev1_read = client.read_revision(entity_id, 1)
        rev2_read = client.read_revision(entity_id, 2)

        assert rev1_read is not None
        assert rev1_read.revision_id == 1
        assert len(rev1_read.statements) == 0

        assert rev2_read is not None
        assert rev2_read.revision_id == 2
        assert len(rev2_read.statements) == 1

    def test_s3_error_recovery(self, s3_config):
        """Test error recovery and graceful failure handling."""
        client = MyS3Client(s3_config)

        # Test reading non-existent data
        result = client.read_revision("Q-nonexistent", 999)
        assert result is None

        result = client.read_statements("Q-nonexistent", 999)
        assert result is None

        result = client.load_metadata("Q-nonexistent", 999)
        assert result is None

        # Test writing to non-existent bucket (simulate connection issues)
        # This should be handled gracefully by the client
        bad_config = S3Config(
            endpoint_url="http://bad-endpoint:9999",
            access_key="test",
            secret_key="test",
            bucket="nonexistent-bucket",
            region="us-east-1",
        )

        bad_client = MyS3Client(bad_config)
        # Operations should fail gracefully, not crash
        write_result = bad_client.write_revision("Q42", 1, RevisionData(
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
        ))
        # Should return OperationResult with success=False
        assert write_result.success is False</content>
<parameter name="filePath">/home/dpriskorn/src/python/wikibase-backend/tests/integration/models/infrastructure/s3/test_s3_end_to_end_integration.py