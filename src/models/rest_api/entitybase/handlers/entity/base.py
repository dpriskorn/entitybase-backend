"""Entity CRUD operation handlers."""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import HTTPException
from pydantic import BaseModel
from rapidhash import rapidhash

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.data import RevisionData
from models.infrastructure.s3.hashmaps import StatementsHashes, HashMaps
from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import EntityChangeEvent
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.entitybase.request import EntityCreateRequest
from models.rest_api.entitybase.request.entity.add_property import AddPropertyRequest
from models.rest_api.entitybase.request.entity.patch import LabelPatchRequest
from models.rest_api.entitybase.request.entity.patch_statement import (
    PatchStatementRequest,
)
from models.rest_api.entitybase.response import (
    EntityResponse,
)
from models.rest_api.entitybase.response import StatementHashResult
from models.rest_api.entitybase.response.entity import EntityState
from models.rest_api.entitybase.services.statement_service import (
    hash_entity_statements,
    deduplicate_and_store_statements,
)
from models.infrastructure.s3.enums import EditType, EditData, EntityType
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.services.hash_service import HashService
from models.rest_api.utils import raise_validation_error

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


class EntityHandler(BaseModel):
    """Base entity handler with common functionality"""

    async def _process_entity_revision(
        self,
        entity_id: str,
        request_data: Dict[str, Any],
        entity_type: str,
        is_mass_edit: bool | None,
        edit_type: EditType | None,
        is_semi_protected: bool | None,
        is_locked: bool | None,
        is_archived: bool | None,
        is_dangling: bool | None,
        is_mass_edit_protected: bool | None,
        is_not_autoconfirmed_user: bool | None,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None,
        is_creation: bool,
        edit_summary: str = "",
    ) -> EntityResponse:
        """Common logic for processing entity revisions after validation."""
        # Get current head revision
        head_revision_id = vitess_client.get_head(entity_id)
        logger.debug(f"Current head revision for {entity_id}: {head_revision_id}")

        # Calculate content hash for deduplication
        entity_json = json.dumps(request_data, sort_keys=True)
        content_hash = rapidhash(entity_json.encode())
        logger.debug(f"Entity content hash: {content_hash}")

        # Check idempotency
        idempotent_response = self._check_idempotency(
            entity_id, head_revision_id, content_hash, request_data, s3_client
        )
        if idempotent_response:
            return idempotent_response

        # Check protection settings
        self._check_protection_settings(
            entity_id, is_mass_edit, is_not_autoconfirmed_user, vitess_client
        )

        # Calculate new revision ID
        new_revision_id = head_revision_id + 1 if head_revision_id else 1
        logger.debug(f"New revision ID will be: {new_revision_id}")

        # Process statements
        hash_result = self.process_statements(
            entity_id, request_data, vitess_client, s3_client, validator
        )

        # Create and store revision
        revision_result = await self._create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=new_revision_id,
            head_revision_id=head_revision_id,
            request_data=request_data,
            entity_type=entity_type,
            hash_result=hash_result,
            content_hash=content_hash,
            is_mass_edit=is_mass_edit,
            edit_type=edit_type,
            edit_summary=edit_summary,
            is_semi_protected=is_semi_protected,
            is_locked=is_locked,
            is_archived=is_archived,
            is_dangling=is_dangling,
            is_mass_edit_protected=is_mass_edit_protected,
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            is_creation=is_creation,
        )

        if not revision_result.success:
            raise_validation_error(revision_result.error or "Failed to create revision")
        assert isinstance(revision_result.data, EntityResponse)
        return revision_result.data

    def _check_idempotency(
        self,
        entity_id: str,
        head_revision_id: int,
        content_hash: int,
        request_data: Dict[str, Any],
        s3_client: MyS3Client,
    ) -> EntityResponse | None:
        """Check if the request is idempotent and return existing revision if so."""
        if head_revision_id == 0:
            return None

        logger.debug(f"Checking idempotency against head revision {head_revision_id}")
        try:
            head_revision = s3_client.read_revision(entity_id, head_revision_id)
            head_content_hash = head_revision.data.get("content_hash")
            logger.debug(f"Head revision content hash: {head_content_hash}")

            if head_content_hash == content_hash:
                logger.debug(
                    f"Content unchanged, returning existing revision {head_revision_id}"
                )
                return EntityResponse(
                    id=entity_id,
                    rev_id=head_revision_id,
                    data=head_revision.entity,
                    state=EntityState(
                        sp=head_revision.data.get("is_semi_protected", False),
                        is_locked=head_revision.data.get("is_locked", False),
                        archived=head_revision.data.get("is_archived", False),
                        dangling=head_revision.data.get("is_dangling", False),
                        mep=head_revision.data.get("is_mass_edit_protected", False),
                    ),
                )
        except Exception as e:
            logger.warning(f"Failed to read head revision for idempotency check: {e}")

        return None

    def _check_protection_settings(
        self,
        entity_id: str,
        is_mass_edit: bool | None,
        is_not_autoconfirmed_user: bool | None,
        vitess_client: VitessClient,
    ) -> None:
        """Check protection settings and raise exceptions if editing is blocked."""
        protection_info = vitess_client.get_protection_info(entity_id)
        logger.debug(f"Protection info for {entity_id}: {protection_info}")

        try:
            # Archived items block all edits
            if protection_info and protection_info.is_archived:
                raise_validation_error(
                    "Entity is archived and cannot be edited", status_code=403
                )

            # Locked items block all edits
            if protection_info and protection_info.is_locked:
                raise_validation_error(
                    "Entity is locked from all edits", status_code=403
                )

            # Mass-edit protection blocks mass edits only
            if (
                protection_info
                and protection_info.is_mass_edit_protected
                and is_mass_edit
            ):
                raise_validation_error(
                    "Mass edits blocked on this entity", status_code=403
                )

            # Semi-protection blocks not-autoconfirmed users
            if (
                protection_info
                and protection_info.is_semi_protected
                and is_not_autoconfirmed_user
            ):
                raise_validation_error(
                    "Semi-protected items cannot be edited by new or unconfirmed users",
                    status_code=403,
                )
        except (HTTPException, ValueError):
            raise
        except Exception as e:
            logger.warning(f"Failed to check protection for entity {entity_id}: {e}")
            pass

    def process_statements(
        self,
        entity_id: str,
        request_data: Dict[str, Any],
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        validator: Any | None,
    ) -> StatementHashResult:
        """Process and store statements for the entity."""
        logger.debug("Starting statement hashing process")
        logger.info(f"Entity {entity_id}: Starting statement hashing")
        try:
            hash_operation = hash_entity_statements(request_data)
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
        store_result = deduplicate_and_store_statements(
            hash_result=hash_result,
            vitess_client=vitess_client,
            s3_client=s3_client,
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

    async def _create_and_store_revision(
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
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        is_creation: bool,
        edit_summary: str,
        user_id: int,
    ) -> OperationResult:
        """Create revision data, store it, and publish events."""
        # Process sitelinks: hash titles and store metadata
        sitelinks_hashes = HashService.hash_sitelinks(
            request_data.get("sitelinks", {}), s3_client
        )
        # Replace sitelinks with hashes in entity data
        request_data["sitelinks"] = sitelinks_hashes.root

        # Process terms: hash labels, descriptions, aliases and store metadata
        labels_hashes = HashService.hash_labels(
            request_data.get("labels", {}), s3_client, vitess_client
        )
        descriptions_hashes = HashService.hash_descriptions(
            request_data.get("descriptions", {}), s3_client, vitess_client
        )
        aliases_hashes = HashService.hash_aliases(
            request_data.get("aliases", {}), s3_client, vitess_client
        )

        # Create revision data
        created_at = datetime.now(timezone.utc).isoformat()
        revision_is_mass_edit = is_mass_edit if is_mass_edit is not None else False
        revision_edit_type = edit_type if edit_type else EditType.UNSPECIFIED

        revision_data = RevisionData(
            schema_version=settings.s3_schema_revision_version,
            revision_id=new_revision_id,
            entity_type=entity_type,
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

        # Store revision in S3 and update head
        logger.info(f"Entity {entity_id}: Creating revision {new_revision_id}")
        try:
            vitess_client.create_revision(
                entity_id=entity_id,
                entity_data=revision_data.model_dump(),
                revision_id=new_revision_id,
            )
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
        if stream_producer:
            try:
                change_type = (
                    ChangeType.CREATION
                    if is_creation
                    else edit_type_to_change_type(revision_edit_type)
                )
                await stream_producer.publish_change(
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
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        validator: Any | None = None,
        user_id: int = 0,
    ) -> OperationResult[dict]:
        """Add claims for a single property to an existing entity."""
        logger.info(
            f"Entity {entity_id}: Adding property {property_id} with {len(request.claims)} claims"
        )

        # Validate property_id format
        if not property_id.startswith("P") or not property_id[1:].isdigit():
            return OperationResult(success=False, error="Invalid property ID format")

        # Check if property exists and is a property
        try:
            read_handler = EntityReadHandler()
            property_response = read_handler.get_entity(
                property_id, vitess_client, s3_client
            )
            if property_response.entity_type != "property":
                return OperationResult(success=False, error="Entity is not a property")
        except Exception:
            return OperationResult(success=False, error="Property does not exist")

        # Fetch current entity data
        try:
            read_handler = EntityReadHandler()
            entity_response = read_handler.get_entity(
                entity_id, vitess_client, s3_client
            )
            current_data = entity_response.entity_data
        except Exception as e:
            return OperationResult(success=False, error=f"Failed to fetch entity: {e}")

        # Merge claims
        if "claims" not in current_data:
            current_data["claims"] = {}
        if property_id not in current_data["claims"]:
            current_data["claims"][property_id] = []
        current_data["claims"][property_id].extend(request.claims)

        # Process as update
        revision_result = await self._create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=entity_response.revision_id + 1,  # Assume increment
            head_revision_id=entity_response.revision_id,
            request_data=current_data,
            entity_type=entity_response.entity_type,
            hash_result=self.process_statements(
                entity_id, current_data, vitess_client, s3_client, validator
            ),
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
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=None,  # TODO: add if needed
            is_creation=False,
            edit_summary=request.edit_summary,
            user_id=user_id,
        )

        if not revision_result.success:
            return revision_result

        return OperationResult(
            success=True, data={"revision_id": revision_result.data.rev_id}
        )

    async def patch_labels(
        self,
        entity_id: str,
        request: LabelPatchRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        validator: Any | None = None,
        user_id: int = 0,
    ) -> OperationResult[dict]:
        """Patch entity labels using JSON Patch."""
        logger.info(f"Entity {entity_id}: Patching labels with 1 operation")

        # Fetch current entity data
        try:
            read_handler = EntityReadHandler()
            entity_response = read_handler.get_entity(
                entity_id, vitess_client, s3_client
            )
            current_data = entity_response.entity_data
        except Exception as e:
            return OperationResult(success=False, error=f"Failed to fetch entity: {e}")

        # Apply patch to labels
        if "labels" not in current_data:
            current_data["labels"] = {}
        try:
            op = request.patch.op
            path = request.patch.path
            if not path.startswith("/labels/"):
                return OperationResult(
                    success=False, error="Path must start with /labels/"
                )
            key = path[len("/labels/") :]
            if op == "add":
                if key in current_data["labels"]:
                    return OperationResult(
                        success=False, error=f"Label {key} already exists"
                    )
                current_data["labels"][key] = request.patch.value
            elif op == "replace":
                if key not in current_data["labels"]:
                    return OperationResult(
                        success=False, error=f"Label {key} does not exist"
                    )
                current_data["labels"][key] = request.patch.value
            elif op == "remove":
                if key not in current_data["labels"]:
                    return OperationResult(
                        success=False, error=f"Label {key} does not exist"
                    )
                del current_data["labels"][key]
            else:
                return OperationResult(
                    success=False, error=f"Unsupported operation: {op}"
                )
        except Exception as e:
            return OperationResult(success=False, error=f"Invalid patch: {e}")

        # Process as update
        revision_result = self._create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=entity_response.revision_id + 1,
            head_revision_id=entity_response.revision_id,
            request_data=current_data,
            entity_type=entity_response.entity_type,
            hash_result=self.process_statements(
                entity_id, current_data, vitess_client, s3_client, validator
            ),
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
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=None,
            is_creation=False,
            edit_summary=request.edit_summary,
            user_id=user_id,
        )
        assert isinstance(revision_result, OperationResult)
        if not revision_result.success:
            return revision_result

        return OperationResult(
            success=True, data={"revision_id": revision_result.data.rev_id}
        )

    def remove_statement(
        self,
        entity_id: str,
        statement_hash: str,
        edit_summary: str,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        validator: Any | None = None,
        user_id: int = 0,
    ) -> OperationResult[dict]:
        """Remove a statement by hash from an entity."""
        logger.info(f"Entity {entity_id}: Removing statement {statement_hash}")

        # Fetch current revision
        try:
            revision_data = s3_client.read_revision(entity_id)
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
        from models.infrastructure.vitess.statement_repository import (
            StatementRepository,
        )

        stmt_repo = StatementRepository(vitess_client.connection_manager)
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
            s3_client.write_revision(entity_id, new_revision_id, revision_data)
            vitess_client.update_head_revision(entity_id, new_revision_id)
        except Exception as e:
            return OperationResult(
                success=False, error=f"Failed to store updated revision: {e}"
            )

        return OperationResult(success=True, data={"revision_id": new_revision_id})

    def patch_statement(
        self,
        entity_id: str,
        statement_hash: str,
        request: PatchStatementRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        validator: Any | None = None,
        user_id: int = 0,
    ) -> OperationResult[dict]:
        """Replace a statement by hash with new claim data."""
        logger.info(f"Entity {entity_id}: Patching statement {statement_hash}")

        # Fetch current entity data
        try:
            read_handler = EntityReadHandler()
            entity_response = read_handler.get_entity(
                entity_id, vitess_client, s3_client
            )
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

        # Process as update
        revision_result = self._create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=entity_response.revision_id + 1,
            head_revision_id=entity_response.revision_id,
            request_data=current_data,
            entity_type=entity_response.entity_data.get("type", "item"),
            hash_result=self.process_statements(
                entity_id, current_data, vitess_client, s3_client, validator
            ),
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
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=None,
            is_creation=False,
            edit_summary=request.edit_summary,
            user_id=user_id,
        )
        assert isinstance(revision_result, OperationResult)
        if not revision_result.success:
            return revision_result

        return OperationResult(
            success=True, data={"revision_id": revision_result.data.rev_id}
        )


class EntityCreateHandler(EntityHandler):
    """Handler for entity creation operations"""

    async def create_entity(
        self,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Create a new entity. Fails if entity already exists."""
        entity_id = request.id

        logger.info(
            f"=== ENTITY CREATION START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "entity_type": request.type,
                "is_mass_edit": request.is_mass_edit,
                "edit_type": request.edit_type,
                "data_keys": list(request.data.keys()),
                "has_claims": bool(request.data.get("claims")),
                "operation": "create_entity_start",
            },
        )

        # Check if entity already exists - for create, this should fail
        entity_existed = vitess_client.entity_exists(entity_id)
        if entity_existed:
            logger.error(f"Entity {entity_id} already exists, cannot create")
            raise_validation_error("Entity already exists", status_code=409)

        # Register the new entity
        vitess_client.register_entity(entity_id)

        # Check deletion status
        is_deleted = vitess_client.is_entity_deleted(entity_id)
        if is_deleted:
            raise_validation_error(
                f"Entity {entity_id} has been deleted", status_code=410
            )

        # Common processing logic
        return await self._process_entity_revision(
            entity_id=entity_id,
            request_data=request.data,
            entity_type=request.type,
            is_mass_edit=request.is_mass_edit,
            edit_type=request.edit_type,
            edit_summary=request.edit_summary,
            is_semi_protected=request.is_semi_protected,
            is_locked=request.is_locked,
            is_archived=request.is_archived,
            is_dangling=request.is_dangling,
            is_mass_edit_protected=request.is_mass_edit_protected,
            is_not_autoconfirmed_user=request.is_autoconfirmed_user,
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            validator=validator,
            is_creation=True,
        )


class EntityUpdateHandler(EntityHandler):
    """Handler for entity update operations"""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update an existing entity. Fails if entity doesn't exist."""
        logger.info(
            f"=== ENTITY UPDATE START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "entity_type": request.type,
                "is_mass_edit": request.is_mass_edit,
                "edit_type": request.edit_type,
                "data_keys": list(request.data.keys()),
                "has_claims": bool(request.data.get("claims")),
                "operation": "update_entity_start",
            },
        )

        # Check if entity exists - for update, this is required
        entity_existed = vitess_client.entity_exists(entity_id)
        if not entity_existed:
            logger.error(f"Entity {entity_id} does not exist, cannot update")
            raise_validation_error("Entity not found", status_code=404)

        # Check deletion status
        is_deleted = vitess_client.is_entity_deleted(entity_id)
        if is_deleted:
            raise_validation_error(
                f"Entity {entity_id} has been deleted", status_code=410
            )

        # Add entity_id to request data for consistency
        request_data = request.data
        request_data["id"] = entity_id

        # Common processing logic
        return await self._process_entity_revision(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=request.type,
            is_mass_edit=request.is_mass_edit,
            edit_type=request.edit_type,
            edit_summary=request.edit_summary,
            is_semi_protected=request.is_semi_protected,
            is_locked=request.is_locked,
            is_archived=request.is_archived,
            is_dangling=request.is_dangling,
            is_mass_edit_protected=request.is_mass_edit_protected,
            is_not_autoconfirmed_user=request.is_autoconfirmed_user,
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            validator=validator,
            is_creation=False,
        )
