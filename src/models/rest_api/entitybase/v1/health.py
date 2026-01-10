from fastapi import APIRouter, Request

from models.api_models import HealthResponse

router = APIRouter()


@router.get("/health")
def health_redirect(req: Request) -> HealthResponse:
    """Health check endpoint that redirects or provides status."""
    # For now, return a simple health status
    return HealthResponse(status="ok")
