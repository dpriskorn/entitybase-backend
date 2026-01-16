"""Entity CRUD operation handlers."""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import HTTPException
from pydantic import BaseModel
from rapidhash import rapidhash

from models.config.settings import settings
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import (
    ChangeType,
    StreamProducerClient,
    EntityChangeEvent,
)
from models.infrastructure.vitess_client import VitessClient
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.misc import EditType
from models.rest_api.entitybase.request import EntityCreateRequest
from models.rest_api.entitybase.response import (
    EntityRevisionResponse,
    EntityResponse,
)
from models.rest_api.entitybase.response import StatementHashResult
from models.rest_api.entitybase.services.statement_service import (
    hash_entity_statements,
    deduplicate_and_store_statements,
)
from models.validation.utils import raise_validation_error

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
        edit_summary: str | None,
        editor: str | None,
        is_semi_protected: bool | None,
        is_locked: bool | None,
        is_archived: bool | None,
        is_dangling: bool | None,
        is_mass_edit_protected: bool | None,
        is_not_autoconfirmed_user: bool | None,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None,
        is_creation: bool,
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
        revision_response = await self._create_and_store_revision(
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
            editor=editor,
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

        return revision_response

    def _check_idempotency(
        self,
        entity_id: str,
        head_revision_id: int,
        content_hash: int,
        request_data: Dict[str, Any],
        s3_client: S3Client,
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
                    revision_id=head_revision_id,
                    is_semi_protected=head_revision.data.get(
                        "is_semi_protected", False
                    ),
                    is_locked=head_revision.data.get("is_locked", False),
                    is_archived=head_revision.data.get("is_archived", False),
                    is_dangling=head_revision.data.get("is_dangling", False),
                    is_mass_edit_protected=head_revision.data.get(
                        "is_mass_edit_protected", False
                    ),
                    entity_data=head_revision.data.get("entity_data", {}),
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
                    "Item is archived and cannot be edited", status_code=403
                )

            # Locked items block all edits
            if protection_info and protection_info.is_locked:
                raise_validation_error("Item is locked from all edits", status_code=403)

            # Mass-edit protection blocks mass edits only
            if (
                protection_info
                and protection_info.is_mass_edit_protected
                and is_mass_edit
            ):
                raise_validation_error(
                    "Mass edits blocked on this item", status_code=403
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
        s3_client: S3Client,
        validator: Any | None,
    ) -> StatementHashResult:
        """Process and store statements for the entity."""
        logger.debug("Starting statement hashing process")
        logger.info(f"Entity {entity_id}: Starting statement hashing")
        try:
            hash_result = hash_entity_statements(request_data)
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
        try:
            deduplicate_and_store_statements(
                hash_result=hash_result,
                vitess_client=vitess_client,
                s3_client=s3_client,
                validator=validator,
                schema_version=settings.s3_statement_version,
            )
            logger.info(
                f"Entity {entity_id}: Successfully completed statement deduplication and storage"
            )
            logger.info(
                f"Entity {entity_id}: Stored {len(hash_result.statements)} statements with hashes: {hash_result.statements}"
            )
        except Exception as e:
            logger.error(
                f"Entity {entity_id}: Statement deduplication and storage failed",
                extra={
                    "entity_id": entity_id,
                    "error": str(e),
                    "operation": "statement_storage_failed",
                },
            )
            raise_validation_error(f"Statement storage failed: {e}", status_code=500)

        return hash_result

    async def _create_and_store_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: Dict[str, Any],
        entity_type: str,
        hash_result: StatementHashResult,
        content_hash: int,
        is_mass_edit: bool | None,
        edit_type: EditType | None,
        edit_summary: str | None,
        editor: str | None,
        is_semi_protected: bool | None,
        is_locked: bool | None,
        is_archived: bool | None,
        is_dangling: bool | None,
        is_mass_edit_protected: bool | None,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        is_creation: bool,
    ) -> EntityRevisionResponse:
        """Create revision data, store it, and publish events."""
        # Process sitelinks: hash titles and store metadata
        sitelinks_hashes = {}
        if "sitelinks" in request_data:
            for wiki, sitelink_data in request_data["sitelinks"].items():
                if "title" in sitelink_data:
                    title = sitelink_data["title"]
                    hash_value = MetadataExtractor.hash_string(title)
                    sitelinks_hashes[wiki] = hash_value
                    # Store metadata in S3
                    s3_client.store_sitelink_metadata(title, hash_value)
            # Replace sitelinks with hashes in entity data
            request_data["sitelinks"] = sitelinks_hashes

        # Create revision data
        created_at = datetime.now(timezone.utc).isoformat() + "Z"
        revision_is_mass_edit = is_mass_edit if is_mass_edit is not None else False
        revision_edit_type = (
            edit_type.value if edit_type else EditType.UNSPECIFIED.value
        )

        revision_data = {
            "schema_version": settings.s3_revision_version,
            "revision_id": new_revision_id,
            "created_at": created_at,
            "created_by": "rest-api",
            "entity_type": entity_type,
            "entity": request_data,
            "statements": hash_result.statements,
            "properties": hash_result.properties,
            "property_counts": hash_result.property_counts,
            "sitelinks_hashes": sitelinks_hashes,
            "content_hash": content_hash,
            "edit_summary": edit_summary,
            "editor": editor,
            "is_mass_edit": revision_is_mass_edit,
            "edit_type": revision_edit_type,
            "is_semi_protected": is_semi_protected,
            "is_locked": is_locked,
            "is_archived": is_archived,
            "is_dangling": is_dangling,
            "is_mass_edit_protected": is_mass_edit_protected,
            "is_deleted": False,
            "is_redirect": False,
        }

        # Store revision in S3 and update head
        logger.info(f"Entity {entity_id}: Creating revision {new_revision_id}")
        try:
            vitess_client.create_revision(
                entity_id=entity_id,
                revision_id=new_revision_id,
                expected_revision_id=head_revision_id,
                entity_data=request_data,
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
                        entity_id=entity_id,
                        revision_id=new_revision_id,
                        change_type=change_type,
                        from_revision_id=head_revision_id
                        if head_revision_id != 0
                        else None,
                        changed_at=datetime.now(timezone.utc),
                        editor=editor,
                        edit_summary=edit_summary,
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

        # Return response
        return EntityResponse(
            id=entity_id,
            revision_id=new_revision_id,
            entity_data=request_data,
            is_semi_protected=is_semi_protected or False,
            is_locked=is_locked or False,
            is_archived=is_archived or False,
            is_dangling=is_dangling or False,
            is_mass_edit_protected=is_mass_edit_protected or False,
        )


class EntityCreateHandler(EntityHandler):
    """Handler for entity creation operations"""

    async def create_entity(
        self,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
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
            editor=request.editor,
            is_semi_protected=request.is_semi_protected,
            is_locked=request.is_locked,
            is_archived=request.is_archived,
            is_dangling=request.is_dangling,
            is_mass_edit_protected=request.is_mass_edit_protected,
            is_not_autoconfirmed_user=request.is_not_autoconfirmed_user,
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
        s3_client: S3Client,
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
            editor=request.editor,
            is_semi_protected=request.is_semi_protected,
            is_locked=request.is_locked,
            is_archived=request.is_archived,
            is_dangling=request.is_dangling,
            is_mass_edit_protected=request.is_mass_edit_protected,
            is_not_autoconfirmed_user=request.is_not_autoconfirmed_user,
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            validator=validator,
            is_creation=False,
        )
