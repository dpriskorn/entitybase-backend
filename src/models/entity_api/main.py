import json
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from rapidhash import rapidhash

logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from starlette import status

from models.infrastructure.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient
from models.config.settings import settings
from models.entity import (
    CleanupOrphanedRequest,
    CleanupOrphanedResponse,
    DeleteType,
    EditType,
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityDeleteResponse,
    EntityResponse,
    RevisionMetadata,
    EntityRedirectRequest,
    MostUsedStatementsResponse,
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
    RedirectRevertRequest,
    StatementBatchRequest,
    StatementBatchResponse,
    StatementHashResult,
    StatementResponse,
)
from models.json_parser import parse_entity
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.loader import load_property_registry
from models.rdf_builder.property_registry.registry import PropertyRegistry

from services.entity_api.redirects import RedirectService

if TYPE_CHECKING:
    from models.infrastructure.s3_client import S3Config
    from models.infrastructure.vitess_client import VitessConfig


class Clients(BaseModel):
    s3: S3Client | None = None
    vitess: VitessClient | None = None
    property_registry: PropertyRegistry | None = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        s3: "S3Config",
        vitess: "VitessConfig",
        property_registry_path: Path | None = None,
        **kwargs,
    ):
        super().__init__(
            s3=S3Client(s3),
            vitess=VitessClient(vitess),
            property_registry=(
                load_property_registry(property_registry_path)
                if property_registry_path
                else None
            ),
            **kwargs,
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.debug("Initializing clients...")
        s3_config = settings.to_s3_config()
        vitess_config = settings.to_vitess_config()
        logger.debug(f"S3 config: {s3_config}")
        logger.debug(f"Vitess config: {vitess_config}")

        property_registry_path = (
            Path("test_data/properties")
            if Path("test_data/properties").exists()
            else None
        )
        logger.debug(f"Property registry path: {property_registry_path}")

        app.state.clients = Clients(
            s3=s3_config,
            vitess=vitess_config,
            property_registry_path=property_registry_path,
        )
        logger.debug("Clients initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


app = FastAPI(lifespan=lifespan)


def serialize_entity_to_turtle(entity_data: dict[str, Any], entity_id: str) -> str:
    """Convert entity data dict to Turtle format string."""
    entity = parse_entity(entity_data)
    converter = EntityConverter(
        property_registry=app.state.clients.property_registry
        or PropertyRegistry(properties={}),
        enable_deduplication=True,
    )
    return converter.convert_to_string(entity)


def hash_entity_statements(
    entity_data: dict[str, Any],
) -> StatementHashResult:
    """Extract and hash statements from entity data.

    Returns:
        StatementHashResult with hashes, properties, and full statements
    """
    statements = []
    full_statements = []
    properties_set = set()
    property_counts = {}

    claims = entity_data.get("claims", {})
    logger.debug(f"Entity claims: {claims}")

    if not claims:
        logger.debug("No claims found in entity data")
        return StatementHashResult()

    claims_count = sum(len(claim_list) for claim_list in claims.values())
    logger.debug(
        f"Hashing statements for entity with {len(claims)} properties, {claims_count} total statements"
    )

    for property_id, claim_list in claims.items():
        logger.debug(
            f"Processing property {property_id} with {len(claim_list)} statements"
        )

        if not claim_list:
            logger.debug(f"Empty claim list for property {property_id}")
            continue

        properties_set.add(property_id)
        count = 0

        for idx, statement in enumerate(claim_list):
            logger.debug(
                f"Processing statement {idx + 1}/{len(claim_list)} for property {property_id}"
            )
            try:
                statement_for_hash = {k: v for k, v in statement.items() if k != "id"}
                statement_json = json.dumps(statement_for_hash, sort_keys=True)
                statement_hash = rapidhash(statement_json.encode())
                logger.debug(
                    f"Generated hash {statement_hash} for statement {idx + 1} in property {property_id}"
                )

                statements.append(statement_hash)
                full_statements.append(statement)
                count += 1
            except Exception as e:
                logger.error(
                    f"Failed to hash statement {idx + 1} for property {property_id}: {e}"
                )
                logger.error(f"Statement data: {statement}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to hash statement: {e}",
                )

        property_counts[property_id] = count
        logger.debug(f"Property {property_id}: processed {count} statements")

    logger.debug(
        f"Generated {len(statements)} hashes, properties: {sorted(properties_set)}"
    )
    logger.debug(f"Property counts: {property_counts}")

    return StatementHashResult(
        statements=statements,
        properties=sorted(properties_set),
        property_counts=property_counts,
        full_statements=full_statements,
    )


def deduplicate_and_store_statements(
    hash_result: StatementHashResult,
    vitess_client: VitessClient,
    s3_client: S3Client,
) -> None:
    """Deduplicate and store statements in Vitess and S3.

    For each statement:
    - Check if hash exists in statement_content table
    - If not exists: write to S3 and insert into statement_content
    - If exists: increment ref_count

    Args:
        hash_result: StatementHashResult with hashes and full statements
        vitess_client: Vitess client for statement_content operations
        s3_client: S3 client for statement storage
    """
    logger.debug(f"Deduplicating and storing {len(hash_result.statements)} statements")

    for idx, (statement_hash, statement_data) in enumerate(
        zip(hash_result.statements, hash_result.full_statements)
    ):
        logger.debug(
            f"Processing statement {idx + 1}/{len(hash_result.statements)} with hash {statement_hash}"
        )
        try:
            is_new = vitess_client.insert_statement_content(statement_hash)
            logger.debug(f"Statement {statement_hash} is_new: {is_new}")

            if is_new:
                statement_with_hash = {
                    **statement_data,
                    "content_hash": statement_hash,
                    "created_at": datetime.now(timezone.utc).isoformat() + "Z",
                }
                logger.debug(f"Writing new statement {statement_hash} to S3")
                s3_client.write_statement(statement_hash, statement_with_hash)
                logger.debug(f"Successfully wrote statement {statement_hash} to S3")
            else:
                logger.debug(
                    f"Incrementing ref_count for existing statement {statement_hash}"
                )
                vitess_client.increment_ref_count(statement_hash)
                logger.debug(
                    f"Successfully incremented ref_count for statement {statement_hash}"
                )
        except Exception as e:
            logger.error(f"Failed to store statement {statement_hash}: {e}")
            logger.error(f"Statement data: {statement_data}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store statement {statement_hash}: {e}",
            )

    logger.debug(
        f"Successfully stored all {len(hash_result.statements)} statements (new + existing)"
    )


@app.get("/health")
async def health_check(response: Response):
    clients = getattr(app.state, "clients", None)

    if clients is None:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "starting"}

    s3_status = (
        "connected" if clients.s3 and clients.s3.check_connection() else "disconnected"
    )
    vitess_status = (
        "connected"
        if clients.vitess and clients.vitess.check_connection()
        else "disconnected"
    )

    return {"status": "ok", "s3": s3_status, "vitess": vitess_status}


@app.post("/entity", response_model=EntityResponse)
def create_entity(request: EntityCreateRequest):
    clients = app.state.clients

    logger.debug("=== ENTITY CREATION START ===")
    logger.debug(f"Request entity_id: {request.data.get('id')}")
    logger.debug(f"Request data keys: {list(request.data.keys())}")
    logger.debug(f"Request is_mass_edit: {request.is_mass_edit}")
    logger.debug(f"Request edit_type: {request.edit_type}")

    if clients.vitess is None:
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
    entity_existed = clients.vitess.entity_exists(entity_id)
    logger.debug(f"Entity {entity_id} exists: {entity_existed}")

    if not entity_existed:
        logger.debug(f"Registering new entity {entity_id}")
        clients.vitess.register_entity(entity_id)
        logger.debug(f"Successfully registered entity {entity_id}")
    else:
        logger.debug(f"Entity {entity_id} already registered")

    # Check if entity is hard-deleted (block edits/undelete)
    is_deleted = clients.vitess.is_entity_deleted(entity_id)
    logger.debug(f"Entity {entity_id} is_deleted: {is_deleted}")

    if is_deleted:
        logger.error(f"Entity {entity_id} is hard-deleted, blocking creation")
        raise HTTPException(
            status_code=410, detail=f"Entity {entity_id} has been deleted"
        )

    head_revision_id = clients.vitess.get_head(entity_id)
    logger.debug(f"Current head revision for {entity_id}: {head_revision_id}")

    # Calculate content hash for deduplication
    entity_json = json.dumps(request.data, sort_keys=True)
    content_hash = rapidhash(entity_json.encode())
    logger.debug(f"Entity content hash: {content_hash}")

    # Check if head revision has same content (idempotency)
    if head_revision_id != 0:
        logger.debug(f"Checking idempotency against head revision {head_revision_id}")
        try:
            head_revision = clients.s3.read_revision(entity_id, head_revision_id)
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
            current = clients.s3.read_revision(entity_id, head_revision_id)

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
    hash_result = hash_entity_statements(request.data)
    logger.debug(
        f"Statement hashing complete: {len(hash_result.statements)} hashes generated"
    )

    # Store statements in S3
    logger.debug("Starting statement deduplication and storage process")
    deduplicate_and_store_statements(
        hash_result=hash_result,
        vitess_client=clients.vitess,
        s3_client=clients.s3,
    )
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
    clients.s3.write_revision(
        entity_id=entity_id,
        revision_id=new_revision_id,
        data=revision_data,
        publication_state="pending",
    )
    logger.debug(f"Successfully wrote revision {new_revision_id} to S3")

    logger.debug(
        f"Inserting revision {new_revision_id} metadata into database for entity {entity_id}"
    )
    clients.vitess.insert_revision(
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
        success = clients.vitess.insert_head_with_status(
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
        success = clients.vitess.cas_update_head_with_status(
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
    clients.s3.mark_published(
        entity_id=entity_id,
        revision_id=new_revision_id,
        publication_state="published",
    )
    logger.debug(f"Successfully marked revision {new_revision_id} as published")

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


@app.get("/entity/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str):
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    head_revision_id = clients.vitess.get_head(entity_id)
    if head_revision_id == 0:
        raise HTTPException(status_code=404, detail="Entity has no revisions")

    # Check if entity is hard-deleted
    if clients.vitess.is_entity_deleted(entity_id):
        raise HTTPException(
            status_code=410, detail=f"Entity {entity_id} has been deleted"
        )

    if clients.s3 is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    revision = clients.s3.read_revision(entity_id, head_revision_id)

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


@app.get("/entity/{entity_id}/history", response_model=list[RevisionMetadata])
def get_entity_history(entity_id: str, limit: int = 20, offset: int = 0):
    """Get revision history for an entity with paging

    Args:
        entity_id: Entity ID to fetch history for
        limit: Maximum number of revisions to return (default: 20)
        offset: Number of revisions to skip (default: 0)

    Returns:
        List of revision metadata ordered by created_at DESC (newest first)
    """
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    history = clients.vitess.get_history(entity_id, limit=limit, offset=offset)

    return [
        RevisionMetadata(revision_id=record.revision_id, created_at=record.created_at)
        for record in history
    ]


@app.get("/wiki/Special:EntityData/{entity_id}.ttl")
async def get_entity_data_turtle(entity_id: str):
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    head_revision_id = clients.vitess.get_head(entity_id)
    if head_revision_id == 0:
        raise HTTPException(status_code=404, detail="Entity has no revisions")

    revision = clients.s3.read_revision(entity_id, head_revision_id)
    entity_data = revision.data["entity"]

    turtle = serialize_entity_to_turtle(entity_data, entity_id)
    return Response(content=turtle, media_type="text/turtle")


@app.post("/redirects")
async def create_entity_redirect(request: EntityRedirectRequest):
    """Create a redirect from one entity to another"""
    clients = app.state.clients
    redirect_service = RedirectService(clients.s3, clients.vitess)
    return redirect_service.create_redirect(request)


@app.post("/entities/{entity_id}/revert-redirect")
async def revert_entity_redirect(entity_id: str, request: RedirectRevertRequest):
    """Revert a redirect entity back to normal using revision-based restore"""
    clients = app.state.clients
    redirect_service = RedirectService(clients.s3, clients.vitess)
    return redirect_service.revert_redirect(entity_id, request.revert_to_revision_id)


@app.get("/entity/{entity_id}/revision/{revision_id}", response_model=Dict[str, Any])
def get_entity_revision(entity_id: str, revision_id: int):
    clients = app.state.clients

    if clients.s3 is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    revision = clients.s3.read_revision(entity_id, revision_id)

    # Extract entity from full revision schema (data is already parsed dict)
    entity_data = revision.data["entity"]

    return entity_data


@app.delete("/entity/{entity_id}", response_model=EntityDeleteResponse)
def delete_entity(entity_id: str, request: EntityDeleteRequest):
    """Delete entity (soft or hard delete)"""
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    # Check entity exists
    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get current head revision
    head_revision_id = clients.vitess.get_head(entity_id)
    if head_revision_id == 0:
        raise HTTPException(status_code=404, detail="Entity has no revisions")

    if clients.s3 is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    # Read current revision to preserve entity data
    current_revision = clients.s3.read_revision(entity_id, head_revision_id)

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
                clients.vitess.decrement_ref_count(statement_hash)
            except Exception:
                continue

    # Write deletion revision to S3
    clients.s3.write_revision(
        entity_id=entity_id,
        revision_id=new_revision_id,
        data=revision_data,
        publication_state="pending",
    )

    # Deleted entities have no statements
    statements, properties, property_counts = [], [], {}

    # Insert revision metadata into Vitess
    clients.vitess.insert_revision(
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
        clients.vitess.hard_delete_entity(
            entity_id=entity_id,
            head_revision_id=new_revision_id,
        )
    else:
        # For soft delete, update head pointer with CAS
        success = clients.vitess.cas_update_head_with_status(
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
    clients.s3.mark_published(
        entity_id=entity_id,
        revision_id=new_revision_id,
        publication_state="published",
    )

    return EntityDeleteResponse(
        id=entity_id,
        revision_id=new_revision_id,
        delete_type=request.delete_type,
        is_deleted=True,
    )


@app.get("/raw/{entity_id}/{revision_id}")
def get_raw_revision(entity_id: str, revision_id: int):
    """
    Returns raw S3 entity data for specific revision.

    Pure S3 data - no wrapper, no transformation.

    Returns 404 with typed error_type if:
    - Entity doesn't exist in ID mapping (ENTITY_NOT_FOUND)
    - Entity has no revisions (NO_REVISIONS)
    - Requested revision doesn't exist (REVISION_NOT_FOUND)
    """
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    # Check if entity exists
    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(
            status_code=404, detail=f"Entity {entity_id} not found in ID mapping"
        )

    # Check if revisions exist for entity
    history = clients.vitess.get_history(entity_id)
    if not history:
        raise HTTPException(
            status_code=404, detail=f"Entity {entity_id} has no revisions"
        )

    # Check if requested revision exists
    revision_ids = sorted([r.revision_id for r in history])
    if revision_id not in revision_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Revision {revision_id} not found for entity {entity_id}. Available revisions: {revision_ids}",
        )

    # Read full revision schema from S3
    if clients.s3 is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    revision = clients.s3.read_full_revision(entity_id, revision_id)

    # Return full revision as-is (no transformation)
    return revision


@app.get("/entities")
def list_entities(
    status: Optional[str] = None, edit_type: Optional[str] = None, limit: int = 100
):
    """Filter entities by status or edit_type"""
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if status == "locked":
        return clients.vitess.list_locked_entities(limit)
    elif status == "semi_protected":
        return clients.vitess.list_semi_protected_entities(limit)
    elif status == "archived":
        return clients.vitess.list_archived_entities(limit)
    elif status == "dangling":
        return clients.vitess.list_dangling_entities(limit)
    elif edit_type:
        return clients.vitess.list_by_edit_type(edit_type, limit)
    else:
        raise HTTPException(
            status_code=400, detail="Must provide status or edit_type filter"
        )


@app.get("/statement/{content_hash}", response_model=StatementResponse)
def get_statement(content_hash: int):
    """Get a single statement by its hash

    Returns the full statement JSON from S3.
    """
    clients = app.state.clients

    if clients.s3 is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    try:
        statement_data = clients.s3.read_statement(content_hash)
        return StatementResponse(
            content_hash=content_hash,
            statement=statement_data["statement"],
            created_at=statement_data["created_at"],
        )
    except Exception:
        raise HTTPException(
            status_code=404, detail=f"Statement {content_hash} not found"
        )


@app.post("/statements/batch", response_model=StatementBatchResponse)
def get_statements_batch(request: StatementBatchRequest):
    """Get multiple statements by their hashes

    Efficiently fetches multiple statements in one request.
    Returns not_found list for any hashes that don't exist.
    """
    clients = app.state.clients

    if clients.s3 is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    statements = []
    not_found = []

    for content_hash in request.hashes:
        try:
            statement_data = clients.s3.read_statement(content_hash)
            statements.append(
                StatementResponse(
                    content_hash=content_hash,
                    statement=statement_data["statement"],
                    created_at=statement_data["created_at"],
                )
            )
        except Exception:
            not_found.append(content_hash)

    return StatementBatchResponse(statements=statements, not_found=not_found)


@app.get("/entity/{entity_id}/properties", response_model=PropertyListResponse)
def get_entity_properties(entity_id: str):
    """Get list of unique property IDs for an entity's head revision

    Returns sorted list of properties used in entity statements.
    """
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    head_revision_id = clients.vitess.get_head(entity_id)
    if head_revision_id == 0:
        raise HTTPException(status_code=404, detail="Entity has no revisions")

    history = clients.vitess.get_history(entity_id)
    revision_record = next(
        (r for r in history if r.revision_id == head_revision_id), None
    )

    if not revision_record:
        raise HTTPException(
            status_code=404, detail="Head revision not found in history"
        )

    revision_metadata = clients.s3.read_full_revision(entity_id, head_revision_id)
    properties = revision_metadata.get("properties", [])
    return PropertyListResponse(properties=properties)


@app.get("/entity/{entity_id}/properties/counts", response_model=PropertyCountsResponse)
def get_entity_property_counts(entity_id: str):
    """Get statement counts per property for an entity's head revision

    Returns dict mapping property ID -> count of statements.
    """
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    head_revision_id = clients.vitess.get_head(entity_id)
    if head_revision_id == 0:
        raise HTTPException(status_code=404, detail="Entity has no revisions")

    revision_metadata = clients.s3.read_full_revision(entity_id, head_revision_id)
    property_counts = revision_metadata.get("property_counts", {})
    return PropertyCountsResponse(property_counts=property_counts)


@app.get(
    "/entity/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
def get_entity_property_hashes(entity_id: str, property_list: str):
    """Get statement hashes for specific properties

    Property list format: comma-separated property IDs (e.g., P31,P569)

    Returns list of statement hashes for the specified properties.
    """
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if not clients.vitess.entity_exists(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")

    head_revision_id = clients.vitess.get_head(entity_id)
    if head_revision_id == 0:
        raise HTTPException(status_code=404, detail="Entity has no revisions")

    revision_metadata = clients.s3.read_full_revision(entity_id, head_revision_id)

    property_ids = [p.strip() for p in property_list.split(",") if p.strip()]

    all_statements = revision_metadata.get("statements", [])
    all_properties = revision_metadata.get("properties", [])

    property_hash_map = {}
    entity_data = clients.s3.read_revision(entity_id, head_revision_id)
    claims = entity_data.data.get("entity", {}).get("claims", {})

    for prop_id in property_ids:
        if prop_id not in all_properties:
            continue
        claim_list = claims.get(prop_id, [])
        for claim in claim_list:
            try:
                claim_json = json.dumps(claim, sort_keys=True)
                claim_hash = rapidhash(claim_json.encode())
                property_hash_map.setdefault(prop_id, []).append(claim_hash)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to hash claim: {e}",
                )

    flat_hashes = []
    for prop_id in property_ids:
        if prop_id in property_hash_map:
            flat_hashes.extend(property_hash_map[prop_id])

    return PropertyHashesResponse(property_hashes=flat_hashes)


@app.get("/statement/most_used", response_model=MostUsedStatementsResponse)
def get_most_used_statements(limit: int = 100, min_ref_count: int = 1):
    """Get most referenced statements

    Returns statement hashes sorted by ref_count DESC.
    Useful for analytics and scientific analysis of statement usage patterns.

    Query params:
    - limit: Maximum number of statements to return (1-10000, default 100)
    - min_ref_count: Minimum ref_count threshold (default 1)
    """
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    try:
        statement_hashes = clients.vitess.get_most_used_statements(
            limit=limit, min_ref_count=min_ref_count
        )
        return MostUsedStatementsResponse(statements=statement_hashes)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching most-used statements: {e}"
        )


@app.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(request: CleanupOrphanedRequest):
    """Cleanup orphaned statements from S3 and Vitess

    Orphaned statements are those with ref_count = 0 and are older than
    the specified threshold. This endpoint is typically called by a
    background job (e.g., cron) to clean up unused data.

    Query params (in request body):
    - older_than_days: Minimum age in days (default 180)
    - limit: Maximum statements to cleanup (default 1000)

    Returns count of cleaned and failed statements.
    """
    clients = app.state.clients

    if clients.vitess is None:
        raise HTTPException(status_code=503, detail="Vitess not initialized")

    if clients.s3 is None:
        raise HTTPException(status_code=503, detail="S3 not initialized")

    cleaned_count = 0
    failed_count = 0
    errors = []

    try:
        orphaned_hashes = clients.vitess.get_orphaned_statements(
            older_than_days=request.older_than_days, limit=request.limit
        )

        for content_hash in orphaned_hashes:
            try:
                key = f"statements/{content_hash}.json"
                clients.s3.client.delete_object(
                    Bucket=clients.s3.config.bucket, Key=key
                )

                conn = clients.vitess.connect()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM statement_content WHERE content_hash = %s",
                    (content_hash,),
                )
                cursor.close()
                cleaned_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(f"Hash {content_hash}: {str(e)}")

        return CleanupOrphanedResponse(
            cleaned_count=cleaned_count,
            failed_count=failed_count,
            errors=errors,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during orphaned statement cleanup: {e}",
        )
