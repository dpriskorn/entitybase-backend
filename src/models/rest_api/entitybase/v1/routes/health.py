"""Health check routes."""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Response
from starlette import status
from starlette.requests import Request

from models.data.rest_api.v1.entitybase.response import HealthCheckResponse

logger = logging.getLogger(__name__)

health_router = APIRouter(tags=["health"])


def _check_client_status(client: Any, client_name: str) -> str:
    """Check if a client is connected and healthy."""
    status_val = (
        "connected"
        if client
        and hasattr(client, "healthy_connection")
        and client.healthy_connection
        else "disconnected"
    )
    logger.debug(f"{client_name} status: {status_val}")
    return status_val


def _build_error_response(status_value: str, timestamp: str) -> HealthCheckResponse:
    """Build error response with given status."""
    return HealthCheckResponse(
        status=status_value,
        s3="disconnected",
        mysql="disconnected",
        timestamp=timestamp,
    )


@health_router.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response, req: Request) -> HealthCheckResponse:
    """Health check endpoint for monitoring service status."""
    logger.debug("Health check requested")
    timestamp = datetime.now(timezone.utc).isoformat()

    state = getattr(req.app.state, "state_handler", None)
    if state is None:
        logger.debug("State handler not available, returning starting status")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return _build_error_response("starting", timestamp)

    logger.debug("Checking MySQL connection status")

    if not hasattr(state, "db_client"):
        logger.debug(
            "State handler not properly initialized, returning unavailable status"
        )
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return _build_error_response("unavailable", timestamp)

    mysql_status = _check_client_status(state.db_client, "MySQL")

    return HealthCheckResponse(
        status="ok",
        s3="connected",
        mysql=mysql_status,
        timestamp=timestamp,
    )
