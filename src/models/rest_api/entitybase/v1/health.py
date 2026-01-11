"""Health check endpoint for Entitybase v1 API."""

from fastapi import APIRouter, Request

from models.rest_api.response import HealthResponse

router = APIRouter()


@router.get("/health")
def health_redirect(req: Request) -> HealthResponse:
    """Health check endpoint that redirects or provides status."""
    # For now, return a simple health status
    return HealthResponse(status="ok")
