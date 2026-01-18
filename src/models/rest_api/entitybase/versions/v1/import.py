"""Import routes."""

from fastapi import APIRouter, Request

from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers.entity.json_import import EntityJsonImportHandler
from models.rest_api.entitybase.request import EntityJsonImportRequest
from models.rest_api.entitybase.response import EntityJsonImportResponse

import_router = APIRouter(tags=["import"])


@import_router.post("/json-import", response_model=EntityJsonImportResponse)
async def import_entities_from_jsonl(
    request: EntityJsonImportRequest, req: Request
) -> EntityJsonImportResponse:
    """Import entities from Wikidata JSONL dump file."""
    clients = req.app.state.clients
    handler = EntityJsonImportHandler()
    return await handler.import_entities_from_jsonl(request, clients.vitess, clients.s3)