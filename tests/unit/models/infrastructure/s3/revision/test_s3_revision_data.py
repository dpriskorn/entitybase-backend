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

