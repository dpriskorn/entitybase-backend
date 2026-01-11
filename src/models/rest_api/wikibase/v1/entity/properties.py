from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any

from models.api import WikibaseEntityResponse
from models.rest_api.handlers.entity.read import EntityReadHandler

router = APIRouter()


@router.post("/entities/properties")
async def create_property(request: Dict[str, Any], req: Request) -> RedirectResponse:
    """Create property - redirects to entitybase endpoint"""
    return RedirectResponse(url="/entitybase/v1/entities/properties", status_code=307)


@router.get("/entities/properties/{property_id}", response_model=WikibaseEntityResponse)
async def get_property(property_id: str, req: Request) -> WikibaseEntityResponse:
    """Get property"""
    clients = req.app.state.clients
    handler = EntityReadHandler()
    response = handler.get_entity(
        property_id, clients.vitess, clients.s3
    )  # fetch_metadata=False by default
    # Return the entity data with labels, descriptions, aliases, and statements
    return WikibaseEntityResponse(**response.data["entity"])


@router.put("/entities/properties/{property_id}")
async def update_property(
    property_id: str, request: Dict[str, Any], req: Request
) -> RedirectResponse:
    """Update property - redirects to entitybase endpoint"""
    return RedirectResponse(
        url=f"/entitybase/v1/property/{property_id}", status_code=307
    )


@router.get("/entities/properties/{property_id}/properties")
async def get_property_properties(property_id: str) -> Dict[str, Any]:
    """Get property properties - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/sitelinks")
async def get_property_sitelinks(property_id: str) -> Dict[str, Any]:
    """Get property sitelinks - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/labels")
async def get_property_labels(property_id: str) -> Dict[str, Any]:
    """Get property labels - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/labels/{language_code}")
async def get_property_label(property_id: str, language_code: str) -> RedirectResponse:
    """Get property label for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/labels/{language_code}",
        status_code=307
    )


@router.put("/entities/properties/{property_id}/labels/{language_code}")
async def set_property_label(property_id: str, language_code: str) -> RedirectResponse:
    """Set property label for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/labels/{language_code}",
        status_code=307
    )


@router.delete("/entities/properties/{property_id}/labels/{language_code}")
async def delete_property_label(property_id: str, language_code: str) -> RedirectResponse:
    """Delete property label for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/labels/{language_code}",
        status_code=307
    )


@router.get(
    "/entities/properties/{property_id}/labels_with_language_fallback/{language_code}"
)
async def get_property_labels_with_fallback(
    property_id: str, language_code: str
) -> Dict[str, Any]:
    """Get property labels with language fallback - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/aliases")
async def get_property_aliases(property_id: str) -> Dict[str, Any]:
    """Get property aliases - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/aliases/{language_code}")
async def get_property_aliases_for_language(property_id: str, language_code: str) -> RedirectResponse:
    """Get property aliases for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}",
        status_code=307
    )


@router.patch("/entities/properties/{property_id}/aliases/{language_code}")
async def patch_property_aliases_for_language(
    property_id: str, language_code: str, request: Dict[str, Any]
) -> RedirectResponse:
    """Patch property aliases for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}",
        status_code=307
    )



@router.get("/entities/properties/{property_id}/descriptions")
async def get_property_descriptions(property_id: str) -> Dict[str, Any]:
    """Get property descriptions - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/descriptions/{language_code}")
async def get_property_description(property_id: str, language_code: str) -> RedirectResponse:
    """Get property description for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/descriptions/{language_code}",
        status_code=307
    )


@router.put("/entities/properties/{property_id}/descriptions/{language_code}")
async def set_property_description(property_id: str, language_code: str) -> RedirectResponse:
    """Set property description for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/descriptions/{language_code}",
        status_code=307
    )


@router.delete("/entities/properties/{property_id}/descriptions/{language_code}")
async def delete_property_description(property_id: str, language_code: str) -> RedirectResponse:
    """Delete property description for language - redirects to entitybase"""
    return RedirectResponse(
        url=f"/entitybase/v1/entities/properties/{property_id}/descriptions/{language_code}",
        status_code=307
    )
