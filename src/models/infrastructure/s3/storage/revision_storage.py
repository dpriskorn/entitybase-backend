"""Revision storage operations."""

import logging

from typing import TYPE_CHECKING

from models.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.infrastructure.s3.base_storage import BaseS3Storage

if TYPE_CHECKING:
    from models.infrastructure.s3.revision.revision_data import RevisionData
    from models.rest_api.entitybase.v1.response.entity.revision_read_response import RevisionReadResponse

logger = logging.getLogger(__name__)


class RevisionStorage(BaseS3Storage):
    """Storage operations for revisions."""

    bucket: str = settings.s3_revisions_bucket

    def store_revision(
        self, entity_id: str, revision_id: int, revision_data: "RevisionData"
    ) -> OperationResult[None]:
        """Store a revision by entity and revision ID."""
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor

        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=revision_data.schema_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=revision_data.created_at,
        )

        key = f"{entity_id}/{revision_id}"
        metadata = {"content_hash": str(content_hash)}
        return self.store(key, s3_revision_data, metadata=metadata)

    def load_revision(self, entity_id: str, revision_id: int) -> "RevisionReadResponse":
        """Load a revision by entity and revision ID."""
        from models.rest_api.entitybase.v1.response.entity.revision_read_response import RevisionReadResponse

        key = f"{entity_id}/{revision_id}"
        loaded = self.load(key)
        s3_data = loaded.data
        assert isinstance(s3_data, S3RevisionData)

        # Construct RevisionData from the revision dict
        from models.infrastructure.s3.revision.revision_data import RevisionData
        revision_data = RevisionData(**s3_data.revision)

        return RevisionReadResponse(
            entity_id=entity_id,
            revision_id=revision_id,
            data=revision_data,
            content=s3_data.revision,
            schema_version=s3_data.schema_version,
            created_at=s3_data.created_at,
            user_id=0,  # Not stored, default
            edit_summary="",  # Not stored, default
            redirects_to="",  # Not stored, default
        )
