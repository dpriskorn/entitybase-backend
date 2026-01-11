"""General entity operations for Wikibase v1 API."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any


router = APIRouter()


@router.get("/entities")
async def get_entities() -> Dict[str, Any]:
    """Search entities - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


# Statements


@router.get("/statements")
async def get_statements() -> Dict[str, Any]:
    """Get statements - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")
