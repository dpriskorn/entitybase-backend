from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

# Stub implementations for Wikibase REST API compatibility


@router.get("/entities")
async def get_entities() -> Dict[str, Any]:
    """Search entities - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/entities/items")
async def create_item(request: Dict[str, Any]) -> Dict[str, Any]:
    """Create item - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/items/{item_id}")
async def get_item(item_id: str) -> Dict[str, Any]:
    """Get item - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/entities/items/{item_id}")
async def update_item(item_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
    """Update item - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


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
async def get_item_label(item_id: str, language_code: str) -> Dict[str, Any]:
    """Get item label for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


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
async def get_item_aliases_for_language(
    item_id: str, language_code: str
) -> Dict[str, Any]:
    """Get item aliases for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


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
async def get_item_description(item_id: str, language_code: str) -> Dict[str, Any]:
    """Get item description for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


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


# Properties endpoints


@router.post("/entities/properties")
async def create_property(request: Dict[str, Any]) -> Dict[str, Any]:
    """Create property - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}")
async def get_property(property_id: str) -> Dict[str, Any]:
    """Get property - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/entities/properties/{property_id}")
async def update_property(property_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
    """Update property - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


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
async def get_property_label(property_id: str, language_code: str) -> Dict[str, Any]:
    """Get property label for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/entities/properties/{property_id}/labels/{language_code}")
async def set_property_label(
    property_id: str, language_code: str, request: Dict[str, Any]
) -> Dict[str, Any]:
    """Set property label for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/entities/properties/{property_id}/labels/{language_code}")
async def delete_property_label(property_id: str, language_code: str) -> Dict[str, Any]:
    """Delete property label for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


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
async def get_property_aliases_for_language(
    property_id: str, language_code: str
) -> Dict[str, Any]:
    """Get property aliases for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/entities/properties/{property_id}/aliases/{language_code}")
async def set_property_aliases_for_language(
    property_id: str, language_code: str, request: Dict[str, Any]
) -> Dict[str, Any]:
    """Set property aliases for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/entities/properties/{property_id}/aliases/{language_code}")
async def delete_property_aliases_for_language(
    property_id: str, language_code: str
) -> Dict[str, Any]:
    """Delete property aliases for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/descriptions")
async def get_property_descriptions(property_id: str) -> Dict[str, Any]:
    """Get property descriptions - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/entities/properties/{property_id}/descriptions/{language_code}")
async def get_property_description(
    property_id: str, language_code: str
) -> Dict[str, Any]:
    """Get property description for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/entities/properties/{property_id}/descriptions/{language_code}")
async def set_property_description(
    property_id: str, language_code: str, request: Dict[str, Any]
) -> Dict[str, Any]:
    """Set property description for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/entities/properties/{property_id}/descriptions/{language_code}")
async def delete_property_description(
    property_id: str, language_code: str
) -> Dict[str, Any]:
    """Delete property description for language - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")


# Statements


@router.get("/statements")
async def get_statements() -> Dict[str, Any]:
    """Get statements - stub"""
    raise HTTPException(status_code=501, detail="Not implemented")
