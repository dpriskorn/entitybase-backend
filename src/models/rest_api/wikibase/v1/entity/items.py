from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any, List

from models.rest_api.response.entity import WikibaseEntityResponse
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
async def get_item_properties(item_id: str) -> Dict[str, Any]:
    """Get item properties - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/entities/items/{item_id}/properties")
async def add_item_property(item_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
    """Add item property - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/sitelinks")
async def get_item_sitelinks(item_id: str) -> Dict[str, Any]:
    """Get item sitelinks - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/labels")
async def get_item_labels(item_id: str) -> Dict[str, Any]:
    """Get item labels - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/labels/{language_code}")
async def get_item_label(item_id: str, language_code: str, req: Request) -> Dict[str, Any]:
    """Get item label for language"""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        item_id, clients.vitess, clients.s3
    )
    labels = response.data.get("labels", {})
    if language_code not in labels:
        raise HTTPException(status_code=404, detail=f"Label not found for language {language_code}")
    return labels[language_code]





@router.put("/entities/items/{item_id}/labels/{language_code}")
async def set_item_label(
    item_id: str, language_code: str, request: Dict[str, Any]
) -> Dict[str, Any]:
    """Set item label for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/entities/items/{item_id}/labels/{language_code}")
async def delete_item_label(item_id: str, language_code: str) -> Dict[str, Any]:
    """Delete item label for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/labels_with_language_fallback/{language_code}")
async def get_item_labels_with_fallback(
    item_id: str, language_code: str
) -> Dict[str, Any]:
    """Get item labels with language fallback - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/aliases")
async def get_item_aliases(item_id: str) -> Dict[str, Any]:
    """Get item aliases - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/aliases/{language_code}")
async def get_item_aliases_for_language(item_id: str, language_code: str, req: Request) -> List[Dict[str, Any]]:
    """Get item aliases for language"""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        item_id, clients.vitess, clients.s3
    )
    aliases = response.data.get("aliases", {})
    if language_code not in aliases:
        raise HTTPException(status_code=404, detail=f"Aliases not found for language {language_code}")
    return aliases[language_code]


@router.put("/entities/items/{item_id}/aliases/{language_code}")
async def set_item_aliases_for_language(
    item_id: str, language_code: str, request: Dict[str, Any]
) -> Dict[str, Any]:
    """Set item aliases for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/entities/items/{item_id}/aliases/{language_code}")
async def delete_item_aliases_for_language(
    item_id: str, language_code: str
) -> Dict[str, Any]:
    """Delete item aliases for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/descriptions")
async def get_item_descriptions(item_id: str) -> Dict[str, Any]:
    """Get item descriptions - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}/descriptions/{language_code}")
async def get_item_description(item_id: str, language_code: str, req: Request) -> Dict[str, Any]:
    """Get item description for language"""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        item_id, clients.vitess, clients.s3
    )
    descriptions = response.data.get("descriptions", {})
    if language_code not in descriptions:
        raise HTTPException(status_code=404, detail=f"Description not found for language {language_code}")
    return descriptions[language_code]


@router.put("/entities/items/{item_id}/descriptions/{language_code}")
async def set_item_description(
    item_id: str, language_code: str, request: Dict[str, Any]
) -> Dict[str, Any]:
    """Set item description for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/entities/items/{item_id}/descriptions/{language_code}")
async def delete_item_description(item_id: str, language_code: str) -> Dict[str, Any]:
    """Delete item description for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")
