"""Version routes."""

from fastapi import APIRouter

from models.config.version import API_VERSION, ENTITYBASE_VERSION
from models.data.rest_api.v1.entitybase.response.misc import VersionResponse

version_router = APIRouter(tags=["version"])


@version_router.get("/version", response_model=VersionResponse)
def version_endpoint() -> VersionResponse:
    """Return API and EntityBase versions."""
    return VersionResponse(
        api_version=API_VERSION,
        entitybase_version=ENTITYBASE_VERSION,
    )
