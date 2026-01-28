"""Health check routes."""
from datetime import datetime, timezone

from fastapi import APIRouter, Response
from starlette import status
from starlette.requests import Request

from models.rest_api.entitybase.v1.handlers import health_check
from models.data.rest_api.v1.entitybase.response import HealthCheckResponse

health_router = APIRouter(tags=["health"])


@health_router.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response, req: Request) -> HealthCheckResponse:
    """Health check endpoint for monitoring service status."""
    state = req.app.state.state_handler
    if state is None:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthCheckResponse(
            status="starting", s3="disconnected", vitess="disconnected", timestamp=datetime.now(
                timezone.utc).isoformat()
        )
    from models.rest_api.entitybase.v1.handlers.state import StateHandler
    assert isinstance(state, StateHandler)
    from models.infrastructure.s3.client import MyS3Client
    from models.infrastructure.vitess.client import VitessClient

    s3 = state.s3_client
    s3_status = (
        "connected"
        if s3 and isinstance(s3, MyS3Client) and s3.healthy_connection
        else "disconnected"
    )
    vitess = state.vitess_client
    vitess_status = (
        "connected"
        if vitess
        and isinstance(vitess, VitessClient)
        and vitess.healthy_connection
        else "disconnected"
    )

    return HealthCheckResponse(status="ok", s3=s3_status, vitess=vitess_status, timestamp=datetime.now(timezone.utc).isoformat())
