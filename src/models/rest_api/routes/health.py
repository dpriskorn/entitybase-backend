"""Health check routes."""

from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

from models.rest_api.entitybase.handlers import health_check
from models.rest_api.entitybase.response import HealthCheckResponse


health_router = APIRouter()


@health_router.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response) -> HealthCheckResponse:
    """Health check endpoint for monitoring service status."""
    return health_check(response)


@health_router.get("/v1/health")
def health_redirect() -> RedirectResponse:
    """Redirect legacy /v1/health endpoint to /health."""
    return RedirectResponse(url="/health", status_code=302)
