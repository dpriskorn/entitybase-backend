"""Health check routes."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Response
from starlette import status
from starlette.requests import Request

from models.data.rest_api.v1.entitybase.response import HealthCheckResponse

logger = logging.getLogger(__name__)

health_router = APIRouter(tags=["health"])


@health_router.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response, req: Request) -> HealthCheckResponse:
    """Health check endpoint for monitoring service status."""
    logger.debug("Health check requested")
    state = getattr(req.app.state, "state_handler", None)
    if state is None:
        logger.debug("State handler not available, returning starting status")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthCheckResponse(
            status="starting",
            s3="disconnected",
            vitess="disconnected",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    logger.debug("Checking connection status for S3 and Vitess")
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
    logger.debug(f"S3 status: {s3_status}")
    vitess = state.vitess_client
    vitess_status = (
        "connected"
        if vitess and isinstance(vitess, VitessClient) and vitess.healthy_connection
        else "disconnected"
    )
    logger.debug(f"Vitess status: {vitess_status}")

    return HealthCheckResponse(
        status="ok",
        s3=s3_status,
        vitess=vitess_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
