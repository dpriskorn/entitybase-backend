"""Health check routes."""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Response
from starlette import status
from starlette.requests import Request

from models.data.rest_api.v1.entitybase.response import HealthCheckResponse
from models.config.settings import Settings

logger = logging.getLogger(__name__)

health_router = APIRouter(tags=["health"])


def _check_client_status(client: Any, client_name: str) -> str:
    """Check if a client is connected and healthy.

    Args:
        client: Client instance (S3 or Vitess)
        client_name: Name of the client for logging

    Returns:
        "connected" or "disconnected"
    """
    client_status = (
        "connected"
        if client
        and hasattr(client, "healthy_connection")
        and client.healthy_connection
        else "disconnected"
    )
    logger.debug(f"{client_name} status: {client_status}")
    return client_status


def _check_producer_status(
    producer: Any, settings: Settings, topic_attr: str
) -> str:
    """Check Kafka stream producer status.

    Args:
        producer: StreamProducerClient instance or None
        settings: Application settings to check if topic is configured
        topic_attr: Attribute name on settings for topic (e.g., 'kafka_entitychange_json_topic')

    Returns:
        "connected", "disconnected", or "not_configured"
    """
    topic_value = getattr(settings, topic_attr, "")
    if not topic_value:
        return "not_configured"

    if producer and hasattr(producer, "healthy_connection") and producer.healthy_connection:
        return "connected"
    return "disconnected"


def _build_error_response(status_value: str, timestamp: str) -> HealthCheckResponse:
    """Build error response with given status.

    Args:
        status_value: Status value ("starting", "unavailable")
        timestamp: Current timestamp

    Returns:
        HealthCheckResponse with error status
    """
    return HealthCheckResponse(
        status=status_value,
        s3="disconnected",
        vitess="disconnected",
        timestamp=timestamp,
        producers={
            "entity_change": "not_configured",
            "entitydiff": "not_configured",
            "user_change": "not_configured",
        },
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

    logger.debug("Checking connection status for S3 and Vitess")

    if not hasattr(state, "vitess_client") or not hasattr(state, "s3_client"):
        logger.debug(
            "State handler not properly initialized, returning unavailable status"
        )
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return _build_error_response("unavailable", timestamp)

    s3_status = _check_client_status(state.s3_client, "S3")
    vitess_status = _check_client_status(state.vitess_client, "Vitess")

    settings = state.settings
    producers = {
        "entity_change": _check_producer_status(
            state.entity_change_stream_producer,
            settings,
            "kafka_entitychange_json_topic",
        ),
        "entitydiff": _check_producer_status(
            state.entitydiff_stream_producer,
            settings,
            "kafka_entity_diff_topic",
        ),
        "user_change": _check_producer_status(
            state.user_change_stream_producer,
            settings,
            "kafka_userchange_json_topic",
        ),
    }

    return HealthCheckResponse(
        status="ok",
        s3=s3_status,
        vitess=vitess_status,
        timestamp=timestamp,
        producers=producers,
    )
