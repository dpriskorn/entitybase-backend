"""Entity CRUD operation handlers."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field, ConfigDict

from models.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType, EditData, EntityType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.revision_data import S3RevisionData

from models.data.infrastructure.stream.change_type import ChangeType
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.stream.event import EntityChangeEvent
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.data.rest_api.v1.entitybase.request import AddPropertyRequest
from models.data.rest_api.v1.entitybase.request import (
    PatchStatementRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
)
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.data.rest_api.v1.entitybase.response import RevisionIdResult
from models.rest_api.entitybase.v1.services.hash_service import HashService
from models.rest_api.utils import raise_validation_error
from .entity_hashing_service import EntityHashingService
from .entity_validation_service import EntityValidationService

from ...handler import Handler
from ...result import RevisionResult
from ...services.statement_service import StatementService

logger = logging.getLogger(__name__)


def edit_type_to_change_type(edit_type: EditType | str) -> ChangeType:
    """Map EditType to ChangeType for event streaming."""
    logger.debug(f"Mapping edit type {edit_type} to change type")
    edit_type_str = str(edit_type)

    if edit_type_str in (EditType.MANUAL_CREATE.value, "manual-create"):
        return ChangeType.CREATION
    elif edit_type_str in (EditType.MANUAL_UPDATE.value, "manual-update"):
        return ChangeType.EDIT
    elif edit_type_str in (EditType.REDIRECT_CREATE.value, "redirect-create"):
        return ChangeType.REDIRECT
    elif edit_type_str in (EditType.REDIRECT_REVERT.value, "redirect-revert"):
        return ChangeType.UNREDIRECT
    elif edit_type_str in (EditType.ARCHIVE_ADDED.value, "archive-added"):
        return ChangeType.ARCHIVAL
    elif edit_type_str in (EditType.ARCHIVE_REMOVED.value, "archive-removed"):
        return ChangeType.UNARCHIVAL
    elif edit_type_str in (EditType.LOCK_ADDED.value, "lock-added"):
        return ChangeType.LOCK
    elif edit_type_str in (EditType.LOCK_REMOVED.value, "lock-removed"):
        return ChangeType.UNLOCK
    elif edit_type_str in (EditType.SOFT_DELETE.value, "soft-delete"):
        return ChangeType.SOFT_DELETE
    elif edit_type_str in (EditType.HARD_DELETE.value, "hard-delete"):
        return ChangeType.HARD_DELETE
    else:
        return ChangeType.EDIT


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
        edit_summary: str,
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
            edit_summary=edit_summary,
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
            ctx.request_data,
            ctx.s3_client,
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
                content_hash,
                new_revision_id,
            )

            # Store in database
            ctx.vitess_client.create_revision(
                entity_id=ctx.entity_id,
                entity_data=revision_data,
                revision_id=new_revision_id,
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
        return await hashing_service.hash_terms(
            ctx.request_data, ctx.s3_client, ctx.vitess_client
        )

    async def _hash_sitelinks_new(self, ctx: RevisionContext) -> SitelinksHashes:
        """Hash entity sitelinks."""
        hashing_service = EntityHashingService(state=self.state)
        return await hashing_service.hash_sitelinks(ctx.request_data, ctx.s3_client)

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

    async def _store_revision_s3_new(
        self, ctx: RevisionContext, revision_data: RevisionData
    ) -> None:
        """Store revision data in S3."""
        # Placeholder - would implement S3 storage logic
        pass

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
        request_data: Dict[str, Any],
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

    async def create_and_store_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: Dict[str, Any],
        entity_type: EntityType,
        hash_result: StatementHashResult,
        is_mass_edit: bool | None,
        edit_type: EditType,
        is_semi_protected: bool | None,
        is_locked: bool | None,
        is_archived: bool | None,
        is_dangling: bool | None,
        is_mass_edit_protected: bool | None,
        is_creation: bool,
        edit_summary: str,
        user_id: int,
    ) -> OperationResult:
        """Create revision data, store it, and publish events."""
        # Process sitelinks: hash titles and store metadata
        hs = HashService(state=self.state)
        sitelinks_hashes = hs.hash_sitelinks(request_data.get("sitelinks", {}))
        # Replace sitelinks with hashes in entity data
        request_data["sitelinks"] = sitelinks_hashes.root

        # Process terms: hash labels, descriptions, aliases and store metadata
        labels_hashes = hs.hash_labels(request_data.get("labels", {}))
        descriptions_hashes = hs.hash_descriptions(request_data.get("descriptions", {}))
        aliases_hashes = hs.hash_aliases(request_data.get("aliases", {}))

        # Create revision data
        created_at = datetime.now(timezone.utc).isoformat()
        revision_is_mass_edit = is_mass_edit if is_mass_edit is not None else False
        revision_edit_type = edit_type if edit_type else EditType.UNSPECIFIED

        revision_data = RevisionData(
            schema_version=settings.s3_schema_revision_version,
            revision_id=new_revision_id,
            entity_type=entity_type,
            entity=request_data,
            properties=hash_result.properties,
            property_counts=hash_result.property_counts,
            hashes=HashMaps(
                statements=StatementsHashes(root=hash_result.statements),
                sitelinks=sitelinks_hashes,
                labels=labels_hashes,
                descriptions=descriptions_hashes,
                aliases=aliases_hashes,
            ),
            edit=EditData(
                mass=revision_is_mass_edit,
                type=revision_edit_type,
                user_id=user_id,
                summary=edit_summary,
                at=created_at,
            ),
            state=EntityState(
                sp=is_semi_protected,
                locked=is_locked,
                archived=is_archived,
                dangling=is_dangling,
                mep=is_mass_edit_protected,
                deleted=False,
            ),
        )

        # Create S3 revision data for storage
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor

        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=created_at,
        )

        # Store revision in S3 and update head
        logger.info(f"Entity {entity_id}: Creating revision {new_revision_id}")
        try:
            self.state.vitess_client.create_revision(
                entity_id=entity_id,
                entity_data=revision_data,
                revision_id=new_revision_id,
            )

            # Store in S3 using S3RevisionData
            self.state.s3_client.store_revision(content_hash, s3_revision_data)

            logger.info(
                f"Entity {entity_id}: Successfully created revision {new_revision_id}"
            )
        except Exception as e:
            logger.error(
                f"Entity {entity_id}: Failed to create revision {new_revision_id}",
                extra={
                    "entity_id": entity_id,
                    "revision_id": new_revision_id,
                    "error": str(e),
                    "operation": "revision_creation_failed",
                },
            )
            if "concurrent" in str(e).lower():
                raise_validation_error(
                    f"Revision creation failed: {e}", status_code=409
                )
            else:
                raise_validation_error(
                    f"Revision creation failed: {e}", status_code=500
                )

        # Publish change event
        if self.state.stream_producer:
            try:
                change_type = (
                    ChangeType.CREATION
                    if is_creation
                    else edit_type_to_change_type(revision_edit_type)
                )
                await self.state.stream_producer.publish_change(
                    EntityChangeEvent(
                        id=entity_id,
                        rev=new_revision_id,
                        type=change_type,
                        from_rev=head_revision_id if head_revision_id != 0 else None,
                        at=datetime.now(timezone.utc),
                        summary=edit_summary,
                    )
                )
                logger.debug(
                    f"Entity {entity_id}: Published change event for revision {new_revision_id}"
                )
            except Exception as e:
                logger.warning(
                    f"Entity {entity_id}: Failed to publish change event: {e}",
                    extra={
                        "entity_id": entity_id,
                        "revision_id": new_revision_id,
                        "error": str(e),
                        "operation": "change_event_publish_failed",
                    },
                )

        # Type guards for boolean fields
        is_semi_protected = (
            is_semi_protected if isinstance(is_semi_protected, bool) else False
        )
        is_locked = is_locked if isinstance(is_locked, bool) else False
        is_archived = is_archived if isinstance(is_archived, bool) else False
        is_dangling = is_dangling if isinstance(is_dangling, bool) else False
        is_mass_edit_protected = (
            is_mass_edit_protected
            if isinstance(is_mass_edit_protected, bool)
            else False
        )

        # Return response
        return OperationResult(
            success=True,
            data=EntityResponse(
                id=entity_id,
                rev_id=new_revision_id,
                data=request_data,
                state=EntityState(
                    sp=is_semi_protected or False,
                    locked=is_locked or False,
                    archived=is_archived or False,
                    dangling=is_dangling or False,
                    mep=is_mass_edit_protected or False,
                ),
            ),
        )

    async def add_property(
        self,
        entity_id: str,
        property_id: str,
        request: AddPropertyRequest,
        validator: Any | None = None,
        # user_id: int = 0,
    ) -> OperationResult[RevisionIdResult]:
        """Add claims for a single property to an existing entity."""
        logger.info(
            f"Entity {entity_id}: Adding property {property_id} with {len(request.claims)} claims"
        )

        # Validate property_id format
        if not property_id.startswith("P") or not property_id[1:].isdigit():
            return OperationResult(success=False, error="Invalid property ID format")

        # Check if property exists and is a property
        try:
            read_handler = EntityReadHandler(state=self.state)
            property_response = read_handler.get_entity(property_id)
            if property_response.entity_type != "property":
                return OperationResult(success=False, error="Entity is not a property")
        except Exception:
            return OperationResult(success=False, error="Property does not exist")

        # Fetch current entity data
        try:
            read_handler = EntityReadHandler(state=self.state)
            entity_response = read_handler.get_entity(entity_id)
            current_data = entity_response.entity_data
        except Exception as e:
            return OperationResult(success=False, error=f"Failed to fetch entity: {e}")

        # Merge claims
        if "claims" not in current_data:
            current_data["claims"] = {}
        if property_id not in current_data["claims"]:
            current_data["claims"][property_id] = []
        current_data["claims"][property_id].extend(request.claims)

        # Process as update using new architecture
        try:
            entity_response_new = await self.process_entity_revision_new(
                entity_id=entity_id,
                request_data=current_data,
                entity_type=entity_response.entity_type,
                edit_type=EditType.UNSPECIFIED,
                edit_summary=request.edit_summary,
                is_creation=False,
                stream_producer=None,  # TODO: add if needed
                validator=validator,
            )

            return OperationResult(
                success=True,
                data=RevisionIdResult(revision_id=entity_response_new.rev_id),
            )
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def remove_statement(
        self,
        entity_id: str,
        statement_hash: str,
        edit_summary: str,
        # validator: Any | None = None,
        user_id: int = 0,
    ) -> OperationResult[RevisionIdResult]:
        """Remove a statement by hash from an entity."""
        logger.info(f"Entity {entity_id}: Removing statement {statement_hash}")

        # Fetch current revision
        head_revision_id = self.state.vitess_client.get_head(entity_id)
        try:
            revision_data = self.state.s3_client.read_revision(
                entity_id, head_revision_id
            )

            from models.data.rest_api.v1.entitybase.response import RevisionReadResponse
            assert isinstance(revision_data, RevisionReadResponse)
        except Exception as e:
            return OperationResult(
                success=False, error=f"Failed to fetch revision: {e}"
            )

        # Find and remove the statement hash
        if (
            hasattr(revision_data.hashes, "statements")
            and revision_data.hashes.statements
        ):
            try:
                hash_int = int(statement_hash)
                if hash_int in revision_data.hashes.statements.root:
                    index = revision_data.hashes.statements.root.index(hash_int)
                    revision_data.hashes.statements.root.pop(index)

                    # Recalculate property counts
                    start = 0
                    new_properties = []
                    new_property_counts = {}
                    for prop in revision_data.properties:
                        count = revision_data.property_counts.get(prop, 0)
                        if start <= index < start + count:
                            # This is the property of the removed statement
                            count -= 1
                        if count > 0:
                            new_properties.append(prop)
                            new_property_counts[prop] = count
                        start += count

                    revision_data.properties = new_properties
                    revision_data.property_counts = new_property_counts
                else:
                    return OperationResult(
                        success=False, error="Statement hash not found"
                    )
            except ValueError:
                return OperationResult(
                    success=False, error="Invalid statement hash format"
                )
        else:
            return OperationResult(
                success=False, error="No statements found in revision"
            )

        # Decrement ref_count for the statement
        from models.infrastructure.vitess.repositories.statement import (
            StatementRepository,
        )

        stmt_repo = StatementRepository(state=self.state)
        result = stmt_repo.decrement_ref_count(int(statement_hash))
        if not result.success:
            raise_validation_error(
                f"Failed to decrement ref_count for statement {statement_hash}: {result.error}",
                status_code=500,
            )

        # Update the revision with modified hashes
        new_revision_id = revision_data.revision_id + 1
        revision_data.revision_id = new_revision_id
        revision_data.edit.summary = edit_summary
        revision_data.edit.at = datetime.now(timezone.utc).isoformat()
        revision_data.edit.user_id = user_id

        # Store the updated revision
        try:
            self.state.s3_client.write_revision(
                revision_data.data
            )
            self.state.vitess_client.update_head_revision(entity_id, new_revision_id)
        except Exception as e:
            return OperationResult(
                success=False, error=f"Failed to store updated revision: {e}"
            )

        return OperationResult(
            success=True, data=RevisionIdResult(revision_id=new_revision_id)
        )

    async def patch_statement(
        self,
        entity_id: str,
        statement_hash: str,
        request: PatchStatementRequest,
        validator: Any | None = None,
        user_id: int = 0,
    ) -> OperationResult[RevisionIdResult]:
        """Replace a statement by hash with new claim data."""
        logger.info(f"Entity {entity_id}: Patching statement {statement_hash}")

        # Fetch current entity data
        try:
            read_handler = EntityReadHandler(state=self.state)
            entity_response = read_handler.get_entity(entity_id)
            current_data = entity_response.entity_data
        except Exception as e:
            return OperationResult(success=False, error=f"Failed to fetch entity: {e}")

        # Find and replace the statement
        replaced = False
        if "claims" in current_data:
            for property_id, claim_list in current_data["claims"].items():
                for i, stmt in enumerate(claim_list):
                    # Compute hash to match
                    from models.internal_representation.statement_hasher import (
                        StatementHasher,
                    )

                    stmt_hash = StatementHasher.compute_hash(stmt)
                    if str(stmt_hash) == statement_hash:
                        claim_list[i] = request.claim
                        replaced = True
                        break
                if replaced:
                    break

        if not replaced:
            return OperationResult(success=False, error="Statement not found in entity")

        # Process as update using old method for now (new method is async)
        revision_result = await self.create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=entity_response.revision_id + 1,
            head_revision_id=entity_response.revision_id,
            request_data=current_data,
            entity_type=entity_response.entity_data.get("type", "item"),
            hash_result=self.process_statements(entity_id, current_data, validator),
            is_mass_edit=False,
            edit_type=EditType.UNSPECIFIED,
            is_semi_protected=entity_response.state.sp
            if entity_response.state
            else False,
            is_locked=entity_response.state.is_locked
            if entity_response.state
            else False,
            is_archived=entity_response.state.archived
            if entity_response.state
            else False,
            is_dangling=entity_response.state.dangling
            if entity_response.state
            else False,
            is_mass_edit_protected=entity_response.state.mep
            if entity_response.state
            else False,
            is_creation=False,
            edit_summary=request.edit_summary,
            user_id=user_id,
        )
        assert isinstance(revision_result, OperationResult)
        if not revision_result.success:
            return revision_result

        return OperationResult(
            success=True, data=RevisionIdResult(revision_id=revision_result.data.rev_id)
        )
