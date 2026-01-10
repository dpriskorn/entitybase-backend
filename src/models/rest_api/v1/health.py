from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health_redirect(req: Request) -> dict:
    """Health check endpoint that redirects or provides status."""
    # For now, return a simple health status
    return {"status": "ok"}
