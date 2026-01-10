from fastapi import APIRouter, Request

from models.api_models import MostUsedStatementsRequest, MostUsedStatementsResponse
from ..handlers.statement import StatementHandler

router = APIRouter()


@router.get("/statement/most_used", response_model=MostUsedStatementsResponse)
def get_most_used_statements(
    request: MostUsedStatementsRequest, req: Request
) -> MostUsedStatementsResponse:
    clients = req.app.state.clients
    handler = StatementHandler()
    return handler.get_most_used_statements(
        clients.vitess, request.limit, request.min_ref_count
    )
