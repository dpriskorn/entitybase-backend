"""Entity CRUD operation handlers."""

import logging
from datetime import datetime, timezone
from typing import Any

from models.config.settings import settings
from models.data.infrastructure.s3 import SitelinkHashes
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType, EditData
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.entity.context import (
    ProcessEntityRevisionContext,
    RevisionContext,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
)
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.s3.exceptions import S3NotFoundError
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


# noinspection PyArgumentList
class EntityHandler(Handler):
    """Base entity handler with common functionality"""

    # New simplified method using context and services
    async def process_entity_revision_new(
        self,
        ctx: ProcessEntityRevisionContext,
    ) -> EntityResponse:
        """New simplified entity revision processing using services."""
        logger.debug(f"Starting entity revision processing for {ctx.entity_id}")

        rev_ctx = RevisionContext(
            entity_id=ctx.entity_id,
            request_data=ctx.request_data,
            entity_type=ctx.entity_type,
            edit_type=ctx.edit_type,
            edit_summary=ctx.edit_headers.x_edit_summary,
            is_creation=ctx.is_creation,
            vitess_client=self.state.vitess_client,
            s3_client=self.state.s3_client,
            stream_producer=self.state.stream_producer
            if hasattr(self.state, "stream_producer")
            else None,
            validator=ctx.validator,
        )

        # 1. Validate request
        self._validate_revision_request(rev_ctx)
        logger.debug(f"Request validation passed for {ctx.entity_id}")

        # 2. Check idempotency
        if cached := await self._check_idempotency_new(rev_ctx):
            logger.debug(f"Returning cached revision for {ctx.entity_id}")
            return cached
        logger.debug(f"Idempotency check passed for {ctx.entity_id}")

        # 3. Process entity data
        hash_result = await self._process_entity_data_new(rev_ctx)
        logger.debug(f"Entity data processed for {ctx.entity_id}")

        # 4. Create revision
        result = await self._create_revision_new(rev_ctx, hash_result)
        logger.debug(f"Revision created for {ctx.entity_id}: {result.revision_id}")

        # 5. Publish events
        await self._publish_events_new(rev_ctx, result)
        logger.debug(f"Events published for {ctx.entity_id}")

        if not result.success:
            raise_validation_error(result.error or "Revision creation failed")

        # Build response
        response = await self._build_entity_response(rev_ctx, result)
        logger.info(
            f"Entity revision created successfully for {ctx.entity_id}: revision {result.revision_id}"
        )
        return response

    @staticmethod
    def _validate_revision_request(ctx: RevisionContext) -> None:
        """Validate the revision request."""
        # Basic validation
        if not ctx.entity_id:
            raise_validation_error("Entity ID is required", 400)

    @staticmethod
    async def _check_idempotency_new(ctx: RevisionContext) -> EntityResponse | None:
        """Check if request is idempotent using validation service."""
        validation_service = EntityValidationService()
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
        logger.info(f"_create_revision_new START: entity_id={ctx.entity_id}")
        try:
            # Get current head revision
            head_revision_id = ctx.vitess_client.get_head(ctx.entity_id)
            logger.debug(f"_create_revision_new: head_revision_id={head_revision_id}")

            # Calculate new revision ID
            new_revision_id = head_revision_id + 1 if head_revision_id else 1
            logger.debug(f"_create_revision_new: new_revision_id={new_revision_id}")

            # Process terms and sitelinks
            logger.debug(f"_create_revision_new: hashing terms for {ctx.entity_id}")
            term_hashes = await self._hash_terms_new(ctx)
            logger.debug(
                f"_create_revision_new: term_hashes keys: {term_hashes.model_dump().keys() if term_hashes else 'None'}"
            )

            logger.debug(f"_create_revision_new: hashing sitelinks for {ctx.entity_id}")
            sitelink_hashes = await self._hash_sitelinks_new(ctx)

            # Build revision data
            logger.debug(
                f"_create_revision_new: building revision data for {ctx.entity_id}"
            )
            revision_data = self._build_revision_data(
                ctx,
                hash_result,
                term_hashes,
                sitelink_hashes,
                new_revision_id,
            )

            # Store in database and S3 with same content hash
            logger.debug(
                f"_create_revision_new: storing revision in S3 for {ctx.entity_id}"
            )
            content_hash = await self._store_revision_s3_new(ctx, revision_data)
            logger.debug(f"_create_revision_new: content_hash={content_hash}")

            logger.debug(
                f"_create_revision_new: creating revision in Vitess for {ctx.entity_id}"
            )
            ctx.vitess_client.create_revision(
                entity_id=ctx.entity_id,
                entity_data=revision_data,
                revision_id=new_revision_id,
                content_hash=content_hash,
            )

            logger.info(
                f"_create_revision_new SUCCESS: entity_id={ctx.entity_id}, rev={new_revision_id}"
            )
            return RevisionResult(success=True, revision_id=new_revision_id)

        except Exception as e:
            logger.error(
                f"Failed to create revision for {ctx.entity_id}: {e}", exc_info=True
            )
            return RevisionResult(success=False, error=str(e))

    async def _hash_terms_new(self, ctx: RevisionContext) -> HashMaps:
        """Hash entity terms (labels, descriptions, aliases)."""
        hashing_service = EntityHashingService(state=self.state)
        return await hashing_service.hash_terms(ctx.request_data)

    async def _hash_sitelinks_new(self, ctx: RevisionContext) -> SitelinkHashes:
        """Hash entity sitelinks."""
        hashing_service = EntityHashingService(state=self.state)
        return await hashing_service.hash_sitelinks(ctx.request_data)

    @staticmethod
    def _get_forms_with_ids(ctx: RevisionContext) -> list[Any]:
        """Get forms with IDs assigned for lexeme entities."""
        from models.data.infrastructure.s3.enums import EntityType
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
            assign_form_ids,
        )

        forms: list[Any] = ctx.request_data.get("forms", [])
        if not forms or ctx.entity_type != EntityType.LEXEME:
            return forms

        return assign_form_ids(ctx.entity_id, forms).get_json()  # type: ignore[no-any-return]

    @staticmethod
    def _get_senses_with_ids(ctx: RevisionContext) -> list[Any]:
        """Get senses with IDs assigned for lexeme entities."""
        from models.data.infrastructure.s3.enums import EntityType
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
            assign_sense_ids,
        )

        senses: list[Any] = ctx.request_data.get("senses", [])
        if not senses or ctx.entity_type != EntityType.LEXEME:
            return senses

        return assign_sense_ids(ctx.entity_id, senses).get_json()  # type: ignore[no-any-return]

    @staticmethod
    def _build_revision_data(
        ctx: RevisionContext,
        hash_result: StatementHashResult,
        term_hashes: HashMaps,
        sitelink_hashes: Any,
        new_revision_id: int,
    ) -> RevisionData:
        """Build RevisionData object."""
        logger.debug(
            f"Building revision data for {ctx.entity_id} revision {new_revision_id}"
        )

        created_at = datetime.now(timezone.utc).isoformat()

        # Extract state fields from request data
        entity_state = EntityState(
            sp=ctx.request_data.get("is_semi_protected", False),
            locked=ctx.request_data.get("is_locked", False),
            archived=ctx.request_data.get("is_archived", False),
            dangling=ctx.request_data.get("is_dangling", False),
            mep=ctx.request_data.get("is_mass_edit_protected", False),
        )

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
                mass=False,
                type=ctx.edit_type or EditType.UNSPECIFIED,
                user_id=0,
                summary=ctx.edit_summary,
                at=created_at,
            ),
            state=entity_state,
            schema_version=settings.s3_schema_revision_version,
            lemmas=ctx.request_data.get("lemmas", {}),
            forms=EntityHandler._get_forms_with_ids(ctx),
            senses=EntityHandler._get_senses_with_ids(ctx),
            language=ctx.request_data.get("language", ""),
            lexical_category=ctx.request_data.get("lexical_category", ""),
        )

    @staticmethod
    async def _store_revision_s3_new(
        ctx: RevisionContext, revision_data: RevisionData
    ) -> int:
        """Store revision data in S3 and return content hash."""
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
        return content_hash

    @staticmethod
    async def _publish_events_new(ctx: RevisionContext, result: RevisionResult) -> None:
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
                logger.debug(
                    f"Publishing event to stream for entity {ctx.entity_id} revision {result.revision_id}"
                )
                await ctx.stream_producer.publish_change(event)
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
                data=revision,
                state=EntityState(
                    sp=revision.revision.get("state", {}).get(
                        "is_semi_protected", False
                    ),
                    locked=revision.revision.get("state", {}).get("is_locked", False),
                    archived=revision.revision.get("state", {}).get(
                        "is_archived", False
                    ),
                    dangling=revision.revision.get("state", {}).get(
                        "is_dangling", False
                    ),
                    mep=revision.revision.get("state", {}).get(
                        "is_mass_edit_protected", False
                    ),
                ),
            )
        except S3NotFoundError:
            logger.warning(
                f"Created revision not found for {ctx.entity_id}, revision {result.revision_id}"
            )
            raise_validation_error(
                f"Revision not found: {ctx.entity_id}", status_code=404
            )
        except Exception as e:
            logger.error(f"Failed to build response for {ctx.entity_id}: {e}")
            raise_validation_error(
                "Failed to retrieve created revision", status_code=500
            )

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
            hash_result = hash_operation.get_data()
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
