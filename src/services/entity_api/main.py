import json
from fastapi import FastAPI, HTTPException
from typing import Any, Dict

from services.shared.config.settings import settings
from infrastructure.ulid_flake import generate_ulid_flake
from infrastructure.s3_client import S3Client
from infrastructure.vitess_client import VitessClient
from services.shared.models.entity import EntityCreateRequest, EntityResponse, RevisionMetadata


app = FastAPI()
s3_client: S3Client | None = None
vitess_client: VitessClient | None = None


def get_clients():
    if s3_client is None or vitess_client is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return s3_client, vitess_client


@app.on_event("startup")
async def startup():
    global s3_client, vitess_client
    s3_client = S3Client(
        endpoint_url=settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        bucket=settings.s3_bucket
    )
    vitess_client = VitessClient(
        host=settings.vitess_host,
        port=settings.vitess_port,
        database=settings.vitess_database,
        user=settings.vitess_user,
        password=settings.vitess_password
    )


@app.get("/health")
def health_check():
    if s3_client is None or vitess_client is None:
        return {"status": "starting", "s3": "disconnected", "vitess": "disconnected"}
    return {"status": "ok", "s3": "connected", "vitess": "connected"}


@app.post("/entity", response_model=EntityResponse)
def create_entity(request: EntityCreateRequest):
    s3, vitess = get_clients()
    external_id = request.data.get("id")
    if not external_id:
        raise HTTPException(status_code=400, detail="Entity must have 'id' field")
    
    internal_id = vitess.resolve_id(external_id)
    if internal_id is None:
        internal_id = generate_ulid_flake()
        vitess.register_entity(external_id, internal_id)
    
    head_revision_id = vitess.get_head(internal_id)
    new_revision_id = head_revision_id + 1 if head_revision_id else 1
    
    s3.write_snapshot(external_id, new_revision_id, json.dumps(request.data), {"publication_state": "pending"})
    vitess.insert_revision(internal_id, new_revision_id)
    
    success = vitess.cas_update_head(internal_id, head_revision_id, new_revision_id)
    if not success:
        raise HTTPException(status_code=409, detail="Concurrent modification detected")
    
    s3.mark_published(external_id, new_revision_id)
    
    return EntityResponse(id=external_id, revision_id=new_revision_id, data=request.data)


@app.get("/entity/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str):
    s3, vitess = get_clients()
    internal_id = vitess.resolve_id(entity_id)
    if internal_id is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    head_revision_id = vitess.get_head(internal_id)
    if head_revision_id is None:
        raise HTTPException(status_code=404, detail="Entity has no revisions")
    
    data_str = s3.read_snapshot(entity_id, head_revision_id)
    data = json.loads(data_str)
    
    return EntityResponse(id=entity_id, revision_id=head_revision_id, data=data)


@app.get("/entity/{entity_id}/history", response_model=list[RevisionMetadata])
def get_entity_history(entity_id: str):
    _, vitess = get_clients()
    internal_id = vitess.resolve_id(entity_id)
    if internal_id is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    history = vitess.get_history(internal_id)
    
    return [RevisionMetadata(revision_id=row[0], created_at=str(row[1])) for row in history]


@app.get("/entity/{entity_id}/revision/{revision_id}", response_model=Dict[str, Any])
def get_entity_revision(entity_id: str, revision_id: int):
    s3, _ = get_clients()
    data_str = s3.read_snapshot(entity_id, revision_id)
    data = json.loads(data_str)
    
    return data
