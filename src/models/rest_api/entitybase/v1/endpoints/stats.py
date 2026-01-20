"""General statistics routes."""

from fastapi import APIRouter, Request

from models.rest_api.entitybase.v1.handlers.user import UserHandler
from models.rest_api.entitybase.v1.response.misc import GeneralStatsResponse

stats_router = APIRouter(tags=["statistics"])


@stats_router.get("/stats", response_model=GeneralStatsResponse)
def get_general_stats(req: Request) -> GeneralStatsResponse:
    """Get general wiki statistics."""
    clients = req.app.state.clients
    handler = UserHandler()
    try:
        stats = handler.get_general_stats(clients.vitess_config)
        return stats
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))
