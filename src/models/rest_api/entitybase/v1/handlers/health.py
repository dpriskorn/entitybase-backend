"""Handler for system health check operations."""

from datetime import datetime, timezone

from fastapi import Response
from starlette import status

from models.rest_api.entitybase.v1.response import HealthCheckResponse


def health_check(response: Response) -> HealthCheckResponse:
    """Health check endpoint for monitoring system status."""
    from models.rest_api.main import app

    state = getattr(app.state, "state_handler", None)
    if state is None:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthCheckResponse(
            status="starting", s3="disconnected", vitess="disconnected", timestamp=datetime.now(timezone.utc).isoformat()
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
