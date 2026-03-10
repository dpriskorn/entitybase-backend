"""Settings routes."""

import logging

from fastapi import APIRouter

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response.settings import (
    SettingsResponse,
    settings_to_response,
)

logger = logging.getLogger(__name__)

settings_router = APIRouter(tags=["settings"])


@settings_router.get("/settings", response_model=SettingsResponse)
def get_settings() -> SettingsResponse:
    """Get current application settings (excludes sensitive values)."""
    logger.debug("Settings requested")
    return settings_to_response(settings)
