"""Entity CRUD operation handlers."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field, ConfigDict

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.config.settings import settings
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType, EditData, EntityType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
)
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.stream.event import EntityChangeEvent
from models.rest_api.utils import raise_validation_error
from .entity_hashing_service import EntityHashingService
from .entity_validation_service import EntityValidationService
from ...handler import Handler
from ...result import RevisionResult
from ...services.statement_service import StatementService

logger = logging.getLogger(__name__)

EDIT_TYPE_TO_CHANGE_TYPE = {
    EditType.MANUAL_CREATE.value: ChangeType.CREATION,
    "manual-create": ChangeType.CREATION,
    EditType.MANUAL_UPDATE.value: ChangeType.EDIT,
    "manual-update": ChangeType.EDIT,
    EditType.REDIRECT_CREATE.value: ChangeType.REDIRECT,
    "redirect-create": ChangeType.REDIRECT,
    EditType.REDIRECT_REVERT.value: ChangeType.UNREDIRECT,
    "redirect-revert": ChangeType.UNREDIRECT,
    EditType.ARCHIVE_ADDED.value: ChangeType.ARCHIVAL,
    "archive-added": ChangeType.ARCHIVAL,
    EditType.ARCHIVE_REMOVED.value: ChangeType.UNARCHIVAL,
    "archive-removed": ChangeType.UNARCHIVAL,
    EditType.LOCK_ADDED.value: ChangeType.LOCK,
    "lock-added": ChangeType.LOCK,
    EditType.LOCK_REMOVED.value: ChangeType.UNLOCK,
    "lock-removed": ChangeType.UNLOCK,
    EditType.SOFT_DELETE.value: ChangeType.SOFT_DELETE,
    "soft-delete": ChangeType.SOFT_DELETE,
    EditType.HARD_DELETE.value: ChangeType.HARD_DELETE,
    "hard-delete": ChangeType.HARD_DELETE,
}


def edit_type_to_change_type(edit_type: EditType | str) -> ChangeType:
    """Map EditType to ChangeType for event streaming."""
    logger.debug(f"Mapping edit type {edit_type} to change type")
    edit_type_str = str(edit_type)

    return EDIT_TYPE_TO_CHANGE_TYPE.get(edit_type_str, ChangeType.EDIT)


class RevisionContext(BaseModel):
    """Context for revision processing operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity_id: str
    request_data: Dict[str, Any]
    entity_type: EntityType
    edit_type: EditType | None = Field(default=None)
    edit_summary: str = ""
    is_creation: bool = False
    vitess_client: Any
    s3_client: Any
    stream_producer: Any = Field(default=None)
    validator: Any | None = Field(default=None)


# noinspection PyArgumentList
class EntityHandler(Handler):
    """Base entity handler with common functionality"""

    # New simplified method using context and services
    async def process_entity_revision_new(
        self,
        entity_id: str,
        request_data: Dict[str, Any],
        entity_type: EntityType,
        edit_type: EditType | None,
        edit_headers: EditHeaders,
        is_creation: bool,
        validator: Any | None,
    ) -> EntityResponse:
        """New simplified entity revision processing using services."""
        logger.debug(f"Starting entity revision processing for {entity_id}")

        ctx = RevisionContext(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=entity_type,
            edit_type=edit_type,
            edit_summary=edit_headers.x_edit_summary,
            is_creation=is_creation,
            validator=validator,
        )

        # 1. Validate request
        self._validate_revision_request(ctx)
        logger.debug(f"Request validation passed for {entity_id}")

        # 2. Check idempotency
        if cached := await self._check_idempotency_new(ctx):
            logger.debug(f"Returning cached revision for {entity_id}")
            assert isinstance(cached, EntityResponse)
            return cached
        logger.debug(f"Idempotency check passed for {entity_id}")

        # 3. Process entity data
        hash_result = await self._process_entity_data_new(ctx)
        logger.debug(f"Entity data processed for {entity_id}")

        # 4. Create revision
        result = await self._create_revision_new(ctx, hash_result)
        logger.debug(f"Revision created for {entity_id}: {result.revision_id}")

        # 5. Publish events
        await self._publish_events_new(ctx, result)
        logger.debug(f"Events published for {entity_id}")

        if not result.success:
            raise_validation_error(result.error or "Revision creation failed")

        # Build response
        response = await self._build_entity_response(ctx, result)
        logger.info(f"Entity revision created successfully for {entity_id}: revision {result.revision_id}")
        return response

    @staticmethod
    def _validate_revision_request(ctx: RevisionContext) -> None:
        """Validate the revision request."""
        # Basic validation
        if not ctx.entity_id:
            raise_validation_error("Entity ID is required", 400)

    async def _check_idempotency_new(
        self, ctx: RevisionContext
    ) -> EntityResponse | None:
        """Check if request is idempotent using validation service."""
        validation_service = EntityValidationService(state=self.state)
        return validation_service.validate_idempotency(
            ctx.entity_id,
            ctx.vitess_client.get_head(ctx.entity_id),
            0,  # content_hash - need to calculate
        )

    async def _process_entity_data_new(
        self, ctx: RevisionContext
    ) -> StatementHashResult:
        """Process entity data using hashing service."""
        hashing_service = EntityHashingService(state=self.state)
        return await hashing_service.hash_statements(ctx.request_data)

    async def _create_revision_new(
        self, ctx: RevisionContext, hash_result: StatementHashResult
    ) -> RevisionResult:
        """Create revision using simplified logic."""
        try:
            # Get current head revision
            head_revision_id = ctx.vitess_client.get_head(ctx.entity_id)

            # Calculate content hash
            import json
            from rapidhash import rapidhash

            entity_json = json.dumps(ctx.request_data, sort_keys=True)
            content_hash = rapidhash(entity_json.encode())

            # Calculate new revision ID
            new_revision_id = head_revision_id + 1 if head_revision_id else 1

            # Process terms and sitelinks
            term_hashes = await self._hash_terms_new(ctx)
            sitelink_hashes = await self._hash_sitelinks_new(ctx)

            # Build revision data
            revision_data = self._build_revision_data_new(
                ctx,
                hash_result,
                term_hashes,
                sitelink_hashes,
                new_revision_id,
            )

            # Store in database
            ctx.vitess_client.create_revision(
                entity_id=ctx.entity_id,
                entity_data=revision_data,
                revision_id=new_revision_id,
                content_hash=content_hash,
            )

            # Store in S3
            await self._store_revision_s3_new(ctx, revision_data)

            return RevisionResult(success=True, revision_id=new_revision_id)

        except Exception as e:
            logger.error(f"Failed to create revision for {ctx.entity_id}: {e}")
            return RevisionResult(success=False, error=str(e))

    async def _hash_terms_new(self, ctx: RevisionContext) -> HashMaps:
        """Hash entity terms (labels, descriptions, aliases)."""
        hashing_service = EntityHashingService(state=self.state)
        return await hashing_service.hash_terms(ctx.request_data)

    async def _hash_sitelinks_new(self, ctx: RevisionContext) -> SitelinksHashes:
        """Hash entity sitelinks."""
        hashing_service = EntityHashingService(state=self.state)
        return await hashing_service.hash_sitelinks(ctx.request_data)

    @staticmethod
    def _build_revision_data_new(
        ctx: RevisionContext,
        hash_result: StatementHashResult,
        term_hashes: HashMaps,
        sitelink_hashes: Any,
        # content_hash: int,
        new_revision_id: int,
    ) -> RevisionData:
        """Build RevisionData object."""
        logger.debug(
            f"Building revision data for {ctx.entity_id} revision {new_revision_id}"
        )


        created_at = datetime.now(timezone.utc).isoformat()

        return RevisionData(
            revision_id=new_revision_id,
            entity_type=ctx.entity_type,
            properties=hash_result.properties,
            property_counts=hash_result.property_counts,
            hashes=HashMaps(
                statements=StatementsHashes(root=hash_result.statements),
                labels=term_hashes.labels,
                descriptions=term_hashes.descriptions,
                aliases=term_hashes.aliases,
                sitelinks=sitelink_hashes,
            ),
            edit=EditData(
                mass=False,  # Default for now
                type=ctx.edit_type or EditType.UNSPECIFIED,
                user_id=0,  # TODO: Get from context
                summary=ctx.edit_summary,
                at=created_at,
            ),
            state=EntityState(),  # Default state
            schema_version=settings.s3_schema_revision_version,
        )

    @staticmethod
    async def _store_revision_s3_new(
            ctx: RevisionContext, revision_data: RevisionData
    ) -> None:
        """Store revision data in S3."""
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        ctx.s3_client.store_revision(content_hash, s3_revision_data)

    @staticmethod
    async def _publish_events_new(
            ctx: RevisionContext, result: RevisionResult
    ) -> None:
        """Publish revision events."""
        if ctx.stream_producer and result.revision_id:
            try:
                change_type = edit_type_to_change_type(
                    ctx.edit_type or EditType.UNSPECIFIED
                )
                event = EntityChangeEvent(
                    id=ctx.entity_id,
                    rev=result.revision_id,
                    type=change_type,
                    at=datetime.now(timezone.utc),
                    summary=ctx.edit_summary,
                )
                # TODO: Actually publish the event
                logger.debug(f"Would publish event: {event}")
            except Exception as e:
                logger.warning(f"Failed to publish event for {ctx.entity_id}: {e}")

    @staticmethod
    async def _build_entity_response(
            ctx: RevisionContext, result: RevisionResult
    ) -> EntityResponse:
        """Build EntityResponse from revision result."""
        if not result.success or not result.revision_id:
            raise_validation_error(result.error or "Revision creation failed")

        # Read the created revision to build response
        try:
            revision = ctx.s3_client.read_revision(ctx.entity_id, result.revision_id)
            return EntityResponse(
                id=ctx.entity_id,
                rev_id=result.revision_id,
                data=revision.entity,
                state=EntityState(
                    sp=revision.data.get("is_semi_protected", False),
                    locked=revision.data.get("is_locked", False),
                    archived=revision.data.get("is_archived", False),
                    dangling=revision.data.get("is_dangling", False),
                    mep=revision.data.get("is_mass_edit_protected", False),
                ),
            )
        except Exception as e:
            logger.error(f"Failed to build response for {ctx.entity_id}: {e}")
            raise_validation_error("Failed to retrieve created revision")

    def process_statements(
        self,
        entity_id: str,
        request_data: PreparedRequestData,
        validator: Any | None,
    ) -> StatementHashResult:
        """Process and store statements for the entity."""
        logger.debug("Starting statement hashing process")
        logger.info(f"Entity {entity_id}: Starting statement hashing")
        ss = StatementService(state=self.state)
        try:
            hash_operation = ss.hash_entity_statements(request_data)
            if not hash_operation.success:
                raise_validation_error(
                    hash_operation.error or "Failed to hash statements", status_code=500
                )
            hash_result = hash_operation.data
            assert isinstance(hash_result, StatementHashResult)
            logger.info(
                f"Entity {entity_id}: Statement hashing complete: {len(hash_result.statements)} hashes generated",
                extra={
                    "entity_id": entity_id,
                    "statements_count": len(hash_result.statements),
                    "properties": hash_result.properties,
                    "property_counts": hash_result.property_counts,
                    "operation": "statement_hashing_complete",
                },
            )
        except Exception as e:
            logger.error(
                f"Entity {entity_id}: Statement hashing failed",
                extra={
                    "entity_id": entity_id,
                    "error": str(e),
                    "operation": "statement_hashing_failed",
                },
            )
            raise_validation_error(f"Statement processing failed: {e}", status_code=400)

        # Deduplicate and store statements
        logger.info(f"Entity {entity_id}: Starting statement deduplication and storage")
        store_result = ss.deduplicate_and_store_statements(
            hash_result=hash_result,
            validator=validator,
            schema_version=settings.s3_statement_version,
        )
        if not store_result.success:
            raise_validation_error(
                store_result.error or "Failed to store statements", status_code=500
            )
        logger.info(
            f"Entity {entity_id}: Successfully completed statement deduplication and storage"
        )
        logger.info(
            f"Entity {entity_id}: Stored {len(hash_result.statements)} statements with hashes: {hash_result.statements}"
        )
        return hash_result