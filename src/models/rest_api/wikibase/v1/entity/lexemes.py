"""Lexeme operations for Wikibase v1 API."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any

from models.rest_api.response.entity import WikibaseEntityResponse
from models.rest_api.handlers.entity.read import EntityReadHandler


router = APIRouter()


@router.post("/entities/lexemes")
async def create_lexeme(request: Dict[str, Any], req: Request) -> RedirectResponse:
    """Create lexeme - redirects to entitybase endpoint"""
    return RedirectResponse(url="/entitybase/v1/entities/lexemes", status_code=307)


@router.get("/entities/lexemes/{lexeme_id}", response_model=WikibaseEntityResponse)
async def get_lexeme(lexeme_id: str, req: Request) -> WikibaseEntityResponse:
    """Get lexeme"""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        lexeme_id, clients.vitess, clients.s3
    )  # fetch_metadata=False by default
    # Return the entity data with labels, descriptions, aliases, and statements
    return WikibaseEntityResponse(**response.data["entity"])


@router.put("/entities/lexemes/{lexeme_id}")
async def update_lexeme(
    lexeme_id: str, request: Dict[str, Any], req: Request
) -> RedirectResponse:
    """Update lexeme - redirects to entitybase endpoint"""
    return RedirectResponse(url=f"/entitybase/v1/lexeme/{lexeme_id}", status_code=307)
