"""General statistics routes."""

from fastapi import APIRouter, Request

from models.rest_api.entitybase.v1.handlers.user import UserHandler
from models.data.rest_api.v1.entitybase.response import GeneralStatsResponse

stats_router = APIRouter(tags=["statistics"])


@stats_router.get("/stats", response_model=GeneralStatsResponse)
def get_general_stats(req: Request) -> GeneralStatsResponse:
    """Get general wiki statistics."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        stats = handler.get_general_stats()
        return stats
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))
