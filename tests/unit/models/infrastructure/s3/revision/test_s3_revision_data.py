"""Unit tests for S3RevisionData model."""

import pytest

from models.data.infrastructure.s3.revision_data import S3RevisionData


class TestS3RevisionData:
    """Unit tests for S3RevisionData model."""

    def test_s3_revision_data_creation(self) -> None:
        """Test S3RevisionData model instantiation with all required fields."""
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
            "edit": {"mass": False, "type": "manual-create", "user_id": 456, "summary": "test", "at": "2023-01-01T00:00:00Z"},
            "hashes": {"statements": {"root": []}, "labels": {}, "descriptions": {}, "aliases": {}, "sitelinks": {}},
            "properties": [],
            "property_counts": {},
            "created_at": "2023-01-01T00:00:00Z",
            "redirects_to": "",
            "state": {"sp": False, "locked": False, "archived": False, "dangling": False, "mep": False, "deleted": False}
        }

        s3_revision = S3RevisionData(
            schema="1.0.0",
            revision=revision_data,
            hash=987654321,
            created_at="2023-01-01T12:00:00Z"
        )

        assert s3_revision.schema_version == "1.0.0"
        assert s3_revision.revision == revision_data
        assert s3_revision.content_hash == 987654321
        assert s3_revision.created_at == "2023-01-01T12:00:00Z"

    def test_s3_revision_data_aliases(self) -> None:
        """Test that S3RevisionData uses aliases in serialization."""
        revision_data = {"test": "data"}

        s3_revision = S3RevisionData(
            schema="1.0.0",
            revision=revision_data,
            hash=12345,
            created_at="2023-01-01T00:00:00Z"
        )

        # Test model_dump uses aliases
        dumped = s3_revision.model_dump()
        assert "schema" in dumped
        assert "hash" in dumped
        assert "revision" in dumped
        assert "created_at" in dumped

        # Test by_alias mode
        dumped_by_alias = s3_revision.model_dump(by_alias=True)
        assert "schema" in dumped_by_alias
        assert "hash" in dumped_by_alias
        assert "revision" in dumped_by_alias
        assert "created_at" in dumped_by_alias

    def test_s3_revision_data_validation_required_fields(self) -> None:
        """Test that required fields are validated."""
        # Missing revision field should fail
        with pytest.raises(Exception):
            S3RevisionData(
                schema="1.0.0",
                hash=12345,
                created_at="2023-01-01T00:00:00Z"
                # missing revision
            )

    def test_s3_revision_data_serialization(self) -> None:
        """Test S3RevisionData serialization produces expected structure."""
        revision_data = {"entity": {"id": "Q1", "type": "item"}}

        s3_revision = S3RevisionData(
            schema="1.0.0",
            revision=revision_data,
            hash=12345,
            created_at="2023-01-01T00:00:00Z"
        )

        serialized = s3_revision.model_dump()
        expected = {
            "schema": "1.0.0",
            "revision": revision_data,
            "hash": 12345,
            "created_at": "2023-01-01T00:00:00Z"
        }

        assert serialized == expected

    def test_s3_revision_data_empty_revision(self) -> None:
        """Test S3RevisionData with empty revision data."""
        s3_revision = S3RevisionData(
            schema="1.0.0",
            revision={},
            hash=0,
            created_at="2023-01-01T00:00:00Z"
        )

        assert s3_revision.revision == {}
        assert s3_revision.content_hash == 0