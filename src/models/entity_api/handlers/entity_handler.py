import json
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List

from fastapi import HTTPException
from rapidhash import rapidhash

from models.config.settings import settings
from models.entity import (
    DeleteType,
    EditType,
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityDeleteResponse,
    EntityResponse,
    RevisionMetadata,
)
from models.infrastructure.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient
from models.entity_api.services.statement_service import (
    hash_entity_statements,
    deduplicate_and_store_statements,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class EntityHandler:
    """Handles all entity CRUD operations."""

    def create_entity(
        self, request: EntityCreateRequest, vitess_client: VitessClient, s3_client: S3Client
    ) -> EntityResponse:
        """Create or update an entity with statement deduplication."""
        entity_id = request.data.get("id", "unknown")

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

        logger.debug("=== ENTITY CREATION START ===")
        logger.debug(f"Request entity_id: {entity_id}")
        logger.debug(f"Request data keys: {list(request.data.keys())}")
        logger.debug(f"Request is_mass_edit: {request.is_mass_edit}")
        logger.debug(f"Request edit_type: {request.edit_type}")

        if vitess_client is None:
            logger.error("Vitess client not initialized")
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        entity_id = request.id
        is_mass_edit = request.is_mass_edit if request.is_mass_edit is not None else False
        edit_type = request.edit_type if request.edit_type is not None else ""

        if not entity_id:
            logger.error("Entity ID missing from request")
            raise HTTPException(status_code=400, detail="Entity must have 'id' field")

        logger.debug(f"Processing entity {entity_id}")

        # Register entity if doesn't exist
        entity_existed = vitess_client.entity_exists(entity_id)
        logger.debug(f"Entity {entity_id} exists: {entity_existed}")

        if not entity_existed:
            logger.debug(f"Registering new entity {entity_id}")
            vitess_client.register_entity(entity_id)
            logger.debug(f"Successfully registered entity {entity_id}")
        else:
            logger.debug(f"Entity {entity_id} already registered")

        # Check if entity is hard-deleted (block edits/undelete)
        is_deleted = vitess_client.is_entity_deleted(entity_id)
        logger.debug(f"Entity {entity_id} is_deleted: {is_deleted}")

        if is_deleted:
            logger.error(f"Entity {entity_id} is hard-deleted, blocking creation")
            raise HTTPException(
                status_code=410, detail=f"Entity {entity_id} has been deleted"
            )

        head_revision_id = vitess_client.get_head(entity_id)
        logger.debug(f"Current head revision for {entity_id}: {head_revision_id}")

        # Calculate content hash for deduplication
        entity_json = json.dumps(request.data, sort_keys=True)
        content_hash = rapidhash(entity_json.encode())
        logger.debug(f"Entity content hash: {content_hash}")

        # Check if head revision has same content (idempotency)
        if head_revision_id != 0:
            logger.debug(f"Checking idempotency against head revision {head_revision_id}")
            try:
                head_revision = s3_client.read_revision(entity_id, head_revision_id)
                head_content_hash = head_revision.data.get("content_hash")
                logger.debug(f"Head revision content hash: {head_content_hash}")

                if head_content_hash == content_hash:
                    logger.debug(
                        f"Content unchanged, returning existing revision {head_revision_id}"
                    )
                    # Content unchanged, return existing revision
                    return EntityResponse(
                        id=entity_id,
                        revision_id=head_revision_id,
                        data=request.data,
                        is_semi_protected=head_revision.data.get(
                            "is_semi_protected", False
                        ),
                        is_locked=head_revision.data.get("is_locked", False),
                        is_archived=head_revision.data.get("is_archived", False),
                        is_dangling=head_revision.data.get("is_dangling", False),
                    )
            except Exception as e:
                logger.warning(f"Failed to read head revision for idempotency check: {e}")
                # Head revision not found or invalid, proceed with creation
                pass

        # Check protection permissions
        if head_revision_id != 0:
            try:
                current = s3_client.read_revision(entity_id, head_revision_id)

                # Archived items block all edits
                if current.data.get("is_archived"):
                    raise HTTPException(403, "Item is archived and cannot be edited")

                # Locked items block all edits
                if current.data.get("is_locked"):
                    raise HTTPException(403, "Item is locked from all edits")

                # Mass-edit protection blocks mass edits only
                if current.data.get("is_mass_edit_protected") and request.is_mass_edit:
                    raise HTTPException(403, "Mass edits blocked on this item")

                # Semi-protection blocks not-autoconfirmed users
                if (
                    current.data.get("is_semi_protected")
                    and request.is_not_autoconfirmed_user
                ):
                    raise HTTPException(
                        403,
                        "Semi-protected items cannot be edited by new or unconfirmed users",
                    )
            except HTTPException:
                raise
            except Exception:
                pass

        new_revision_id = head_revision_id + 1 if head_revision_id else 1
        logger.debug(f"New revision ID will be: {new_revision_id}")

        # Calculate statement hashes FIRST
        logger.debug("Starting statement hashing process")
        logger.info(f"Entity {entity_id}: Starting statement hashing")
        try:
            hash_result = hash_entity_statements(request.data)
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
                    "error_type": type(e).__name__,
                    "operation": "statement_hashing_failed",
                },
            )
            raise
        logger.debug(
            f"Statement hashing complete: {len(hash_result.statements)} hashes generated"
        )

        # Store statements in S3
        logger.debug("Starting statement deduplication and storage process")
        logger.info(
            f"Entity {entity_id}: Processing {len(hash_result.statements)} statements for storage"
        )
        try:
            deduplicate_and_store_statements(
                hash_result=hash_result,
                vitess_client=vitess_client,
                s3_client=s3_client,
            )
            logger.info(
                f"Entity {entity_id}: Successfully completed statement deduplication and storage"
            )
            logger.info(
                f"Entity {entity_id}: Stored {len(hash_result.statements)} statements with hashes: {hash_result.statements}"
            )

            # High Priority: Add verification by attempting to read all statements back
            logger.debug(
                f"Entity {entity_id}: Verifying all statements can be read back from S3"
            )
            for verify_hash in hash_result.statements:
                try:
                    s3_client.read_statement(verify_hash)
                    logger.debug(
                        f"Entity {entity_id}: Verified statement {verify_hash} is readable from S3"
                    )
                except Exception as verify_error:
                    logger.error(
                        f"Entity {entity_id}: Statement {verify_hash} verification failed: {verify_error}"
                    )
                    # Don't raise here - we want to see which statements fail verification
        except Exception as e:
            logger.error(
                f"Entity {entity_id}: Statement deduplication and storage failed",
                extra={
                    "entity_id": entity_id,
                    "statements_count": len(hash_result.statements),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "operation": "statement_storage_failed",
                },
            )
            raise
        logger.debug("Statement deduplication and storage complete")

        # Construct full revision schema with statement metadata
        revision_data = {
            "schema_version": settings.s3_revision_schema_version,
            "revision_id": new_revision_id,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "created_by": "entity-api",
            "is_mass_edit": is_mass_edit,
            "edit_type": edit_type or EditType.UNSPECIFIED.value,
            "entity_type": request.type,
            "is_semi_protected": request.is_semi_protected,
            "is_locked": request.is_locked,
            "is_archived": request.is_archived,
            "is_dangling": request.is_dangling,
            "is_mass_edit_protected": request.is_mass_edit_protected,
            "is_deleted": False,
            "is_redirect": False,
            "statements": hash_result.statements,
            "properties": hash_result.properties,
            "property_counts": hash_result.property_counts,
            "entity": {
                "id": request.id,
                "type": request.type,
                "labels": request.labels,
                "descriptions": request.descriptions,
                "aliases": request.aliases,
                "sitelinks": request.sitelinks,
            },
            "content_hash": content_hash,
        }

        logger.debug(
            f"Revision data constructed with {len(hash_result.statements)} statements"
        )
        logger.debug(f"Revision properties: {hash_result.properties}")
        logger.debug(f"Revision property_counts: {hash_result.property_counts}")

        logger.debug(f"Writing revision {new_revision_id} for entity {entity_id} to S3")
        s3_client.write_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            data=revision_data,
            publication_state="pending",
        )
        logger.debug(f"Successfully wrote revision {new_revision_id} to S3")

        logger.debug(
            f"Inserting revision {new_revision_id} metadata into database for entity {entity_id}"
        )
        vitess_client.insert_revision(
            entity_id,
            new_revision_id,
            is_mass_edit,
            edit_type or EditType.UNSPECIFIED.value,
            statements=hash_result.statements,
            properties=hash_result.properties,
            property_counts=hash_result.property_counts,
        )
        logger.debug(
            f"Successfully inserted revision {new_revision_id} metadata into database"
        )

        if head_revision_id == 0:
            success = vitess_client.insert_head_with_status(
                entity_id,
                new_revision_id,
                request.is_semi_protected,
                request.is_locked,
                request.is_archived,
                request.is_dangling,
                request.is_mass_edit_protected,
                is_deleted=False,
            )
        else:
            success = vitess_client.cas_update_head_with_status(
                entity_id,
                head_revision_id,
                new_revision_id,
                request.is_semi_protected,
                request.is_locked,
                request.is_archived,
                request.is_dangling,
                request.is_mass_edit_protected,
                is_deleted=False,
            )

        if not success:
            logger.error(f"Concurrent modification detected for entity {entity_id}")
            raise HTTPException(status_code=409, detail="Concurrent modification detected")

        logger.debug(
            f"Marking revision {new_revision_id} for entity {entity_id} as published"
        )
        s3_client.mark_published(
            entity_id=entity_id,
            revision_id=new_revision_id,
            publication_state="published",
        )
        logger.debug(f"Successfully marked revision {new_revision_id} as published")

        logger.debug(f"Successfully created entity {entity_id} revision {new_revision_id}")
        logger.info(
            f"=== ENTITY CREATION SUCCESS: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "revision_id": new_revision_id,
                "statements_count": len(hash_result.statements),
                "properties_count": len(hash_result.properties),
                "operation": "create_entity_success",
            },
        )
        logger.debug("=== ENTITY CREATION END ===")
        return EntityResponse(
            id=entity_id,
            revision_id=new_revision_id,
            data=request.data,
            is_semi_protected=request.is_semi_protected,
            is_locked=request.is_locked,
            is_archived=request.is_archived,
            is_dangling=request.is_dangling,
            is_mass_edit_protected=request.is_mass_edit_protected,
        )

    def get_entity(
        self, entity_id: str, vitess_client: VitessClient, s3_client: S3Client
    ) -> EntityResponse:
        """Get entity by ID."""
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity has no revisions")

        # Check if entity is hard-deleted
        if vitess_client.is_entity_deleted(entity_id):
            raise HTTPException(
                status_code=410, detail=f"Entity {entity_id} has been deleted"
            )

        if s3_client is None:
            raise HTTPException(status_code=503, detail="S3 not initialized")

        revision = s3_client.read_revision(entity_id, head_revision_id)

        # Extract entity from full revision schema (data is already parsed dict)
        entity_data = revision.data["entity"]

        return EntityResponse(
            id=entity_id,
            revision_id=head_revision_id,
            data=entity_data,
            is_semi_protected=revision.data.get("is_semi_protected", False),
            is_locked=revision.data.get("is_locked", False),
            is_archived=revision.data.get("is_archived", False),
            is_dangling=revision.data.get("is_dangling", False),
            is_mass_edit_protected=revision.data.get("is_mass_edit_protected", False),
        )

    def get_entity_history(
        self,
        entity_id: str,
        vitess_client: VitessClient,
        limit: int = 20,
        offset: int = 0,
    ) -> List[RevisionMetadata]:
        """Get revision history for an entity with paging.

        Args:
            entity_id: Entity ID to fetch history for
            limit: Maximum number of revisions to return (default: 20)
            offset: Number of revisions to skip (default: 0)
            vitess_client: Vitess client instance

        Returns:
            List of revision metadata ordered by created_at DESC (newest first)
        """
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        history = vitess_client.get_history(entity_id, limit=limit, offset=offset)

        return [
            RevisionMetadata(revision_id=record.revision_id, created_at=record.created_at)
            for record in history
        ]

    def get_entity_revision(
        self, entity_id: str, revision_id: int, s3_client: S3Client
    ) -> Dict[str, Any]:
        """Get entity revision data by ID and revision number."""
        if s3_client is None:
            raise HTTPException(status_code=503, detail="S3 not initialized")

        revision = s3_client.read_revision(entity_id, revision_id)

        # Extract entity from full revision schema (data is already parsed dict)
        entity_data = revision.data["entity"]

        # Type assertion to ensure MyPy compatibility
        if not isinstance(entity_data, dict):
            raise HTTPException(
                status_code=500,
                detail=f"Invalid entity data type: expected dict, got {type(entity_data)}",
            )

        return entity_data  # type: ignore[return-value]

    def delete_entity(
        self,
        entity_id: str,
        request: EntityDeleteRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
    ) -> EntityDeleteResponse:
        """Delete entity (soft or hard delete)."""
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        # Check entity exists
        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        # Get current head revision
        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity has no revisions")

        if s3_client is None:
            raise HTTPException(status_code=503, detail="S3 not initialized")

        # Read current revision to preserve entity data
        current_revision = s3_client.read_revision(entity_id, head_revision_id)

        # Calculate next revision ID
        new_revision_id = head_revision_id + 1

        # Prepare deletion revision data
        edit_type = (
            EditType.SOFT_DELETE.value
            if request.delete_type == DeleteType.SOFT
            else EditType.HARD_DELETE.value
        )

        revision_data = {
            "schema_version": settings.s3_revision_schema_version,
            "revision_id": new_revision_id,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "created_by": "entity-api",
            "is_mass_edit": False,
            "edit_type": edit_type,
            "entity_type": current_revision.data.get("entity_type", "item"),
            "is_semi_protected": current_revision.data.get("is_semi_protected", False),
            "is_locked": current_revision.data.get("is_locked", False),
            "is_archived": current_revision.data.get("is_archived", False),
            "is_dangling": current_revision.data.get("is_dangling", False),
            "is_mass_edit_protected": current_revision.data.get(
                "is_mass_edit_protected", False
            ),
            "is_deleted": True,
            "is_redirect": False,
            "entity": current_revision.data.get("entity", {}),
        }

        # Decrement ref_count for hard delete (orphaned statement tracking)
        if request.delete_type == DeleteType.HARD:
            old_statements = current_revision.data.get("statements", [])
            for statement_hash in old_statements:
                try:
                    vitess_client.decrement_ref_count(statement_hash)
                except Exception:
                    continue

        # Write deletion revision to S3
        s3_client.write_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            data=revision_data,
            publication_state="pending",
        )

        # Deleted entities have no statements
        statements: list[Any] = []
        properties: list[Any] = []
        property_counts: dict[Any, Any] = {}

        # Insert revision metadata into Vitess
        vitess_client.insert_revision(
            entity_id,
            new_revision_id,
            is_mass_edit=False,
            edit_type=edit_type,
            statements=statements,
            properties=properties,
            property_counts=property_counts,
        )

        # Handle hard delete
        if request.delete_type == DeleteType.HARD:
            vitess_client.hard_delete_entity(
                entity_id=entity_id,
                head_revision_id=new_revision_id,
            )
        else:
            # For soft delete, update head pointer with CAS
            success = vitess_client.cas_update_head_with_status(
                entity_id,
                head_revision_id,
                new_revision_id,
                current_revision.data.get("is_semi_protected", False),
                current_revision.data.get("is_locked", False),
                current_revision.data.get("is_archived", False),
                current_revision.data.get("is_dangling", False),
                current_revision.data.get("is_mass_edit_protected", False),
                is_deleted=False,
            )

            if not success:
                raise HTTPException(
                    status_code=409, detail="Concurrent modification detected"
                )

        # Mark as published
        s3_client.mark_published(
            entity_id=entity_id,
            revision_id=new_revision_id,
            publication_state="published",
        )

        return EntityDeleteResponse(
            id=entity_id,
            revision_id=new_revision_id,
            is_deleted=True,
            deletion_type=request.delete_type,
            deletion_status="soft_deleted"
            if request.delete_type == "soft"
            else "hard_deleted",
        )