"""Item operations for Wikibase v1 API."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any

from models.rest_api.response import WikibaseEntityResponse
from models.rest_api.response.misc import (
    LabelsResponse,
    DescriptionsResponse,
    SitelinksResponse,
    PropertiesResponse,
    Aliases,
)
from models.rest_api.handlers.entity.read import EntityReadHandler


router = APIRouter()


@router.post("/entities/items")
async def create_item(request: Dict[str, Any], req: Request) -> RedirectResponse:
    """Create item - redirects to entitybase endpoint"""
    return RedirectResponse(url="/entitybase/v1/entities/items", status_code=307)


@router.get("/entities/items/{item_id}", response_model=WikibaseEntityResponse)
async def get_item(item_id: str, req: Request) -> WikibaseEntityResponse:
    """Get item"""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        item_id, clients.vitess, clients.s3
    )  # fetch_metadata=False by default
    # Return the entity data with labels, descriptions, aliases, and statements
    return WikibaseEntityResponse(**response.data["entity"])


@router.put("/entities/items/{item_id}")
async def update_item(
    item_id: str, request: Dict[str, Any], req: Request
) -> RedirectResponse:
    """Update item - redirects to entitybase endpoint"""
    return RedirectResponse(url=f"/entitybase/v1/item/{item_id}", status_code=307)


@router.get("/entities/items/{item_id}/properties")
async def get_item_properties(item_id: str) -> PropertiesResponse:
    """Get item properties - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/entities/items/{item_id}/properties")
async def add_item_property(
    item_id: str, request: Dict[str, Any]
) -> PropertiesResponse:
    """Add item property - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/sitelinks")
async def get_item_sitelinks(item_id: str) -> SitelinksResponse:
    """Get item sitelinks - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/sitelinks/{wiki_id}")
async def get_item_sitelink(item_id: str, wiki_id: str, req: Request) -> str:
    """Get sitelink title for a specific wiki in an item."""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    # Get the entity's latest revision
    entity_response = handler.get_entity(item_id, clients.vitess, clients.s3)
    entity_data = entity_response.revision_data["entity"]
    sitelinks = entity_data.get("sitelinks", {})
    if wiki_id not in sitelinks:
        raise HTTPException(status_code=404, detail=f"Sitelink for {wiki_id} not found")
    hash_value = sitelinks[wiki_id]
    # Load the title from S3
    title = clients.s3.load_sitelink_metadata(hash_value)
    if not title:
        raise HTTPException(status_code=404, detail="Sitelink not found")
    return str(title)


@router.get("/entities/items/{item_id}/labels")
async def get_item_labels(item_id: str) -> LabelsResponse:
    """Get item labels - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/labels/{language_code}")
async def get_item_label(item_id: str, language_code: str) -> RedirectResponse:
    """Get item label for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/labels/{language_code}",
        status_code=307,
    )


@router.put("/entities/items/{item_id}/labels/{language_code}")
async def set_item_label(item_id: str, language_code: str) -> RedirectResponse:
    """Set item label for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/labels/{language_code}",
        status_code=307,
    )


@router.delete("/entities/items/{item_id}/labels/{language_code}")
async def delete_item_label(item_id: str, language_code: str) -> RedirectResponse:
    """Delete item label for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/labels/{language_code}",
        status_code=307,
    )


@router.get("/entities/items/{item_id}/labels_with_language_fallback/{language_code}")
async def get_item_labels_with_fallback(
    item_id: str, language_code: str
) -> LabelsResponse:
    """Get item labels with language fallback - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/aliases")
async def get_item_aliases(item_id: str) -> Aliases:
    """Get item aliases - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/aliases/{language_code}")
async def get_item_aliases_for_language(
    item_id: str, language_code: str
) -> RedirectResponse:
    """Get item aliases for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/aliases/{language_code}",
        status_code=307,
    )


@router.patch("/entities/items/{item_id}/aliases/{language_code}")
async def patch_item_aliases_for_language(
    item_id: str, language_code: str, request: Dict[str, Any]
) -> RedirectResponse:
    """Patch item aliases for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/aliases/{language_code}",
        status_code=307,
    )


@router.get("/entities/items/{item_id}/descriptions")
async def get_item_descriptions(item_id: str) -> DescriptionsResponse:
    """Get item descriptions - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/descriptions/{language_code}")
async def get_item_description(item_id: str, language_code: str) -> RedirectResponse:
    """Get item description for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}",
        status_code=307,
    )


@router.put("/entities/items/{item_id}/descriptions/{language_code}")
async def set_item_description(item_id: str, language_code: str) -> RedirectResponse:
    """Set item description for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}",
        status_code=307,
    )


@router.delete("/entities/items/{item_id}/descriptions/{language_code}")
async def delete_item_description(item_id: str, language_code: str) -> RedirectResponse:
    """Delete item description for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}",
        status_code=307,
    )
