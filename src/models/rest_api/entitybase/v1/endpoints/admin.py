"""Admin routes."""

import logging
from typing import Optional

from fastapi import APIRouter, Query, Request, Depends
from pydantic import BaseModel

from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.handlers.admin import AdminHandler
from models.data.rest_api.v1.entitybase.response import EntityListResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


admin_router = APIRouter()


class ListEntitiesQuery(BaseModel):
    """Query parameters for listing entities."""

    entity_type: str = Query(
        "",
        description="Entity type to filter by (item, property, lexeme, entityschema). Leave empty for all types",
    )
    status: str = Query(
        "",
        description="Status filter (locked, semi_protected, archived, dangling). Leave empty for all statuses",
    )
    edit_type: str = Query(
        "",
        description="Edit type filter. Leave empty to return all entities",
    )
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of entities to return"
    )
    offset: int = Query(0, ge=0, description="Number of entities to skip")


def get_list_entities_query(
    entity_type: str = Query(""),
    status: str = Query(""),
    edit_type: str = Query(""),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> ListEntitiesQuery:
    """Dependency to extract query parameters."""
    return ListEntitiesQuery(
        entity_type=entity_type,
        status=status,
        edit_type=edit_type,
        limit=limit,
        offset=offset,
    )


@admin_router.get("/entities", response_model=EntityListResponse)
def list_entities(  # type: ignore[no-any-return]
    req: Request,
    query: ListEntitiesQuery = Depends(get_list_entities_query),
) -> EntityListResponse:
    """List entities based on type, status, edit_type, limit, and offset."""
    logger.debug(
        f"Listing entities - type: {query.entity_type}, status: {query.status}, edit_type: {query.edit_type}, "
        f"limit: {query.limit}, offset: {query.offset}"
    )
    state = req.app.state.state_handler
    if not isinstance(state, StateHandler):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = AdminHandler(state=state)
    result = handler.list_entities(
        entity_type=query.entity_type,
        status=query.status,
        edit_type=query.edit_type,
        limit=query.limit,
        offset=query.offset,
    )
    if not isinstance(result, EntityListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result
