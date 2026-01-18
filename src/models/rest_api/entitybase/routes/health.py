"""Health check routes."""

from fastapi import APIRouter, Response

from models.rest_api.entitybase.handlers import health_check
from models.rest_api.entitybase.response import HealthCheckResponse

health_router = APIRouter(tags=["health"])


@health_router.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response) -> HealthCheckResponse:
    """Health check endpoint for monitoring service status."""
    return health_check(response)
