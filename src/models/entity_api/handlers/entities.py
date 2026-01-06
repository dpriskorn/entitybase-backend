import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import HTTPException

from models.entity import (
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityDeleteResponse,
    EntityResponse,
    RevisionMetadata,
)
from models.infrastructure.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient

# Import statement service functions
try:
    from .services.statement_service import (
        hash_entity_statements,
        deduplicate_and_store_statements,
    )
except ImportError:
    # Fallback for type checking
    from typing import Any, Dict
    from models.entity import StatementHashResult

    def hash_entity_statements(entity_data: Dict[str, Any]) -> StatementHashResult:
        return StatementHashResult()

    def deduplicate_and_store_statements(
        hash_result: StatementHashResult,
        vitess_client: VitessClient,
        s3_client: S3Client,
    ) -> None:
        pass


logger = logging.getLogger(__name__)


def create_entity(
    request: EntityCreateRequest, vitess_client: VitessClient, s3_client: S3Client
) -> EntityResponse:
    """Create or update an entity with statement deduplication."""
    logger.debug("=== ENTITY CREATION START ===")
    logger.debug(f"Request entity_id: {request.data.get('id')}")
    logger.debug(f"Request data keys: {list(request.data.keys())}")
    logger.debug(f"Request is_mass_edit: {request.is_mass_edit}")
    logger.debug(f"Request edit_type: {request.edit_type}")

    if vitess_client is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    entity_id = request.data.get("id")
    if not entity_id:
        raise HTTPException(status_code=400, detail="Entity ID is required")

    # Check if entity exists and verify protection status
    if not vitess_client.entity_exists(entity_id):
        logger.debug(f"Entity {entity_id} does not exist, creating new entity")
        head_revision_id = 0
    else:
        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity has no revisions")

        # Check protection status
        protection_info = vitess_client.get_protection_info(entity_id)
        logger.debug(f"Protection info: {protection_info}")

        if (
            protection_info.get("is_semi_protected", False)
            and not request.is_semi_protected
        ):
            raise HTTPException(
                status_code=403,
                detail="Entity is semi-protected and request lacks semi-protection",
            )
        if protection_info.get("is_locked", False) and not request.is_locked:
            raise HTTPException(
                status_code=403, detail="Entity is locked and request lacks lock"
            )
        if (
            protection_info.get("is_mass_edit_protected", False)
            and request.is_mass_edit
            and not request.is_mass_edit_protected
        ):
            raise HTTPException(
                status_code=403,
                detail="Entity is mass-edit protected and request lacks mass-edit protection",
            )

        # Check if entity is hard-deleted
        if vitess_client.is_entity_deleted(entity_id):
            raise HTTPException(
                status_code=410, detail=f"Entity {entity_id} has been deleted"
            )

    # Create new revision
    new_revision_id = head_revision_id + 1
    logger.debug(f"Creating revision {new_revision_id} for entity {entity_id}")

    # Process statements with hashing and deduplication
    hash_result = hash_entity_statements(request.data)
    logger.debug(f"Generated {len(hash_result.statements)} statement hashes")

    # Store deduplicated statements
    if s3_client is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")
    deduplicate_and_store_statements(hash_result, vitess_client, s3_client)

    # Create revision data with metadata
    revision_data = {
        "entity": request.data,
        "revision_id": new_revision_id,
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "edit_type": request.edit_type.value,
        "is_semi_protected": request.is_semi_protected,
        "is_locked": request.is_locked,
        "is_archived": request.is_archived,
        "is_dangling": request.is_dangling,
        "is_mass_edit_protected": request.is_mass_edit_protected,
        "edit_summary": request.edit_summary,
        "editor": request.editor,
        "bot": request.bot,
        "hashes": hash_result.statements,
        "properties": hash_result.properties,
        "property_counts": hash_result.property_counts,
    }

    # Use CAS operation if entity exists
    if head_revision_id > 0:
        success = vitess_client.create_revision_cas(
            entity_id, new_revision_id, revision_data, head_revision_id
        )
        if not success:
            logger.error(f"CAS failed for entity {entity_id}")
            raise HTTPException(
                status_code=409,
                detail=f"Concurrent modification detected for entity {entity_id}",
            )
    else:
        vitess_client.create_revision(entity_id, new_revision_id, revision_data)

    # Update entity table
    vitess_client.upsert_entity(
        entity_id,
        {
            "entity_id": entity_id,
            "head_revision_id": new_revision_id,
            "properties": hash_result.properties,
            "property_counts": hash_result.property_counts,
            "is_semi_protected": request.is_semi_protected,
            "is_locked": request.is_locked,
            "is_archived": request.is_archived,
            "is_dangling": request.is_dangling,
            "is_mass_edit_protected": request.is_mass_edit_protected,
        },
    )

    logger.debug(f"Successfully created entity {entity_id} revision {new_revision_id}")
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
    entity_id: str, vitess_client: VitessClient, s3_client: S3Client
) -> EntityResponse:
    """Get an entity by ID."""
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
    entity_id: str,
    limit: int = 20,
    offset: int = 0,
    vitess_client: VitessClient | None = None,
) -> list[RevisionMetadata]:
    """Get revision history for an entity with paging

    Args:
        entity_id: Entity ID to fetch history for
        limit: Maximum number of revisions to return (default: 20)
        offset: Number of revisions to skip (default: 0)

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
    entity_id: str, revision_id: int, vitess_client: VitessClient, s3_client: S3Client
) -> Dict[str, Any]:
    """Get a specific entity revision."""
    if vitess_client is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not vitess_client.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    if s3_client is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    revision = s3_client.read_revision(entity_id, revision_id)

    # Return full revision schema for debugging/inspection
    return dict(revision.data)


def delete_entity(
    entity_id: str,
    request: EntityDeleteRequest,
    vitess_client: VitessClient,
    s3_client: S3Client,
) -> EntityDeleteResponse:
    """Delete an entity (soft or hard delete)."""
    if vitess_client is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not vitess_client.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    head_revision_id = vitess_client.get_head(entity_id)
    if head_revision_id == 0:
        raise HTTPException(status_code=404, detail="Entity has no revisions")

    # Check protection status
    protection_info = vitess_client.get_protection_info(entity_id)
    if protection_info.get("is_locked", False) and not request.is_locked:
        raise HTTPException(
            status_code=403, detail="Entity is locked and request lacks lock"
        )

    # Get current revision data to preserve
    if s3_client is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")
    current_revision = s3_client.read_revision(entity_id, head_revision_id)

    # Create new revision marking deletion
    new_revision_id = head_revision_id + 1
    deletion_revision_data = {
        "entity": current_revision.data["entity"],
        "revision_id": new_revision_id,
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "edit_type": request.delete_type.value,
        "is_semi_protected": current_revision.data.get("is_semi_protected", False),
        "is_locked": request.is_locked,
        "is_archived": current_revision.data.get("is_archived", False),
        "is_dangling": current_revision.data.get("is_dangling", False),
        "is_mass_edit_protected": current_revision.data.get(
            "is_mass_edit_protected", False
        ),
        "edit_summary": request.edit_summary,
        "editor": request.editor,
        "bot": request.bot,
        "deleted": True,
        "delete_type": request.delete_type.value,
        "previous_revision_id": head_revision_id,
        "hashes": current_revision.data.get("hashes", []),
        "properties": current_revision.data.get("properties", []),
        "property_counts": current_revision.data.get("property_counts", {}),
    }

    # Create the deletion revision
    success = vitess_client.create_revision_cas(
        entity_id, new_revision_id, deletion_revision_data, head_revision_id
    )
    if not success:
        raise HTTPException(
            status_code=409,
            detail=f"Concurrent modification detected for entity {entity_id}",
        )

    # Update entity status based on delete type
    if request.delete_type.value == "hard":
        # Mark as hard deleted - completely remove
        vitess_client.delete_entity(entity_id)
        deletion_status = "hard_deleted"
    else:
        # Mark as soft deleted - entity remains but flagged
        vitess_client.upsert_entity(
            entity_id,
            {
                "entity_id": entity_id,
                "head_revision_id": new_revision_id,
                "properties": current_revision.data.get("properties", []),
                "property_counts": current_revision.data.get("property_counts", {}),
                "is_semi_protected": current_revision.data.get(
                    "is_semi_protected", False
                ),
                "is_locked": request.is_locked,
                "is_archived": True,  # Soft deleted entities are archived
                "is_dangling": current_revision.data.get("is_dangling", False),
                "is_mass_edit_protected": current_revision.data.get(
                    "is_mass_edit_protected", False
                ),
                "deleted": True,
                "delete_type": request.delete_type.value,
            },
        )
        deletion_status = "soft_deleted"

    return EntityDeleteResponse(
        id=entity_id,
        revision_id=new_revision_id,
        deletion_type=request.delete_type.value,
        deletion_status=deletion_status,
    )
