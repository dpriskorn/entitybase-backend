"""General statistics routes."""

import logging

from fastapi import APIRouter, HTTPException, Request

from models.rest_api.entitybase.v1.handlers.user import UserHandler
from models.data.rest_api.v1.entitybase.response import (
    DeduplicationDatabaseStatsResponse,
    GeneralStatsResponse,
)

logger = logging.getLogger(__name__)

stats_router = APIRouter(tags=["statistics"])


@stats_router.get("/stats", response_model=GeneralStatsResponse)
def get_general_stats(req: Request) -> GeneralStatsResponse:
    """Get general entity statistics."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        stats = handler.get_general_stats()
        return stats
    except ValueError as e:
        logger.warning(f"ValueError in get_general_stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve general stats: {str(e)}"
        )


@stats_router.get(
    "/stats/deduplication", response_model=DeduplicationDatabaseStatsResponse
)
def get_deduplication_stats(req: Request) -> DeduplicationDatabaseStatsResponse:
    """Get deduplication statistics for all data types."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        return handler.get_deduplication_statistics()
    except Exception as e:
        logger.warning(f"Error in get_deduplication_stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve deduplication stats: {str(e)}"
        )
