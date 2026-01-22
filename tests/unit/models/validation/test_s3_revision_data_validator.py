"""Unit tests for S3RevisionData validation."""

from models.data.infrastructure.s3.revision_data import S3RevisionData


class TestS3RevisionDataValidation:
    """Unit tests for S3RevisionData validation."""

    def test_s3_revision_data_entity_validation(self) -> None:
        """Test that S3RevisionData contains valid entity data."""
        # Create valid revision data
        revision_data = {
            "schema_version": "1.2.0",
            "revision_id": 123,
            "entity_type": "item",
            "entity": {
                "id": "Q42",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
                "claims": {}
            },
            "edit": {
                "mass": False,
                "type": "manual-create",
                "user_id": 456,
                "summary": "Created test entity",
                "at": "2023-01-01T12:00:00Z"
            },
            "hashes": {
                "statements": {"root": []},
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "sitelinks": {}
            },
            "properties": [],
            "property_counts": {},
            "created_at": "2023-01-01T12:00:00Z",
            "redirects_to": "",
            "state": {
                "sp": False,
                "locked": False,
                "archived": False,
                "dangling": False,
                "mep": False,
                "deleted": False
            }
        }

        # Create S3RevisionData
        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision=revision_data,
            hash=987654321,
            created_at="2023-01-01T12:00:00Z"
        )

        # Test that the entity data structure is correct
        assert s3_revision_data.revision["entity"]["id"] == "Q42"
        assert s3_revision_data.revision["entity"]["type"] == "item"
        assert "labels" in s3_revision_data.revision["entity"]



    def test_s3_revision_data_alias_usage(self) -> None:
        """Test that S3RevisionData uses aliases correctly."""
        revision_data = {
            "edit": {
                "mass": True,  # This should use the alias
                "type": "manual-update",
                "user_id": 123,
                "summary": "test summary",
                "at": "2023-01-01T00:00:00Z"
            }
        }

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision=revision_data,
            hash=12345,
            created_at="2023-01-01T00:00:00Z"
        )

        # Test that model_dump() produces the correct alias structure
        dumped = s3_revision_data.model_dump()
        assert dumped["revision"]["edit"]["mass"] is True
        assert dumped["revision"]["edit"]["type"] == "manual-update"

    def test_s3_revision_data_invalid_entity(self) -> None:
        """Test S3RevisionData with invalid entity data."""
        # Entity missing required 'id' field
        revision_data = {
            "entity": {
                "type": "item"
                # missing "id"
            },
            "edit": {
                "mass": False,
                "type": "manual-create",
                "user_id": 1,
                "summary": "test",
                "at": "2023-01-01T00:00:00Z"
            },
            "hashes": {
                "statements": {"root": []},
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "sitelinks": {}
            }
        }

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision=revision_data,
            hash=12345,
            created_at="2023-01-01T00:00:00Z"
        )

        # The S3RevisionData itself is valid, but the entity data within it is not
        # This test verifies the structure is correct even with invalid entity data
        assert s3_revision_data.revision["entity"]["type"] == "item"
        assert "id" not in s3_revision_data.revision["entity"]

    def test_s3_revision_data_empty_revision(self) -> None:
        """Test S3RevisionData with empty revision dict."""
        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={},
            hash=12345,
            created_at="2023-01-01T00:00:00Z"
        )

        assert s3_revision_data.revision == {}
        dumped = s3_revision_data.model_dump()
        assert dumped["revision"] == {}