"""Integration tests for entity revision S3 storage."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.integration
class TestEntityRevisionS3Storage:
    """Integration tests for entity revision S3 storage."""

    def test_entity_creation_stores_s3_revision_data(self, api_client, base_url) -> None:
        """Test that creating an entity stores S3RevisionData in S3."""
        # Mock S3 client to capture S3RevisionData storage
        with patch("models.rest_api.entitybase.v1.handlers.entity.wikidata_import.MyS3Client") as mock_s3_client_class:
            mock_s3_client = MagicMock()
            mock_s3_client_class.return_value = mock_s3_client

            # Create entity with statement
            entity_data = {
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
                "claims": {
                    "P31": [
                        {
                            "mainsnak": {
                                "snaktype": "value",
                                "property": "P31",
                                "datavalue": {
                                    "value": {
                                        "id": "Q5",
                                        "entity-type": "item",
                                        "numeric-id": 5,
                                    },
                                    "type": "wikibase-entityid",
                                },
                            },
                            "type": "statement",
                            "rank": "normal",
                        }
                    ]
                },
            }

            # Create entity
            response = await client.post("/v1/entitybase/entities/base/v1/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
            assert response.status_code == 201

            # Verify S3RevisionData was stored
            mock_s3_client.store_revision.assert_called_once()

            # Check the arguments
            call_args = mock_s3_client.store_revision.call_args
            content_hash = call_args[0][0]  # First argument
            s3_revision_data = call_args[0][1]  # Second argument

            # Verify the S3RevisionData structure
            assert hasattr(s3_revision_data, 'schema_version')
            assert hasattr(s3_revision_data, 'revision')
            assert hasattr(s3_revision_data, 'content_hash')
            assert hasattr(s3_revision_data, 'created_at')

            assert s3_revision_data.schema_version == "4.0.0"  # From settings
            assert isinstance(s3_revision_data.revision, dict)
            assert "entity" in s3_revision_data.revision
            assert "revision_id" in s3_revision_data.revision
            assert s3_revision_data.content_hash == content_hash

    def test_s3_revision_data_content_hash_consistency(self, api_client, base_url) -> None:
        """Test that S3RevisionData content hash is computed correctly."""
        with patch("models.rest_api.entitybase.v1.handlers.entity.wikidata_import.MyS3Client") as mock_s3_client_class:
            mock_s3_client = MagicMock()
            mock_s3_client_class.return_value = mock_s3_client

            entity_data = {
                "labels": {"en": {"language": "en", "value": "Hash Test"}},
            }

            response = await client.post("/v1/entitybase/entities/base/v1/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
            assert response.status_code == 201

            # Get the stored S3RevisionData
            call_args = mock_s3_client.store_revision.call_args
            stored_hash = call_args[0][0]
            stored_data = call_args[0][1]

            # Verify hash is an integer
            assert isinstance(stored_hash, int)
            assert stored_hash == stored_data.content_hash

            # The hash should be deterministic for the same data
            # (This is a basic check - in practice we'd verify against the actual hash function)

    def test_s3_revision_data_structure_completeness(self, api_client, base_url) -> None:
        """Test that S3RevisionData.revision contains complete revision data."""
        with patch("models.rest_api.entitybase.v1.handlers.entity.wikidata_import.MyS3Client") as mock_s3_client_class:
            mock_s3_client = MagicMock()
            mock_s3_client_class.return_value = mock_s3_client

            entity_data = {
                "labels": {"en": {"language": "en", "value": "Complete Test"}},
                "descriptions": {"en": {"language": "en", "value": "Test description"}},
            }

            response = await client.post("/v1/entitybase/entities/base/v1/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
            assert response.status_code == 201

            # Get the stored S3RevisionData
            call_args = mock_s3_client.store_revision.call_args
            s3_revision_data = call_args[0][1]

            revision = s3_revision_data.revision

            # Check that all expected fields are present
            required_fields = [
                "schema_version", "revision_id", "entity_type", "entity",
                "edit", "hashes", "properties", "property_counts",
                "created_at", "redirects_to", "state"
            ]

            for field in required_fields:
                assert field in revision, f"Missing field: {field}"

            # Check entity structure
            assert "id" in revision["entity"]
            assert "type" in revision["entity"]
            assert "labels" in revision["entity"]

            # Check edit structure (with aliases)
            edit = revision["edit"]
            assert "mass" in edit  # Alias for is_mass_edit
            assert "type" in edit  # Alias for edit_type
            assert "user_id" in edit
            assert "summary" in edit  # Alias for edit_summary
            assert "at" in edit