"""Uptime routes."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request

from models.data.rest_api.v1.entitybase.response.utilities import UptimeResponse

logger = logging.getLogger(__name__)

uptime_router = APIRouter(tags=["uptime"])


@uptime_router.get("/uptime", response_model=UptimeResponse)
def uptime_endpoint(req: Request) -> UptimeResponse:
    """Return application uptime."""
    start_time = getattr(req.app.state, "start_time", None)
    if start_time is None:
        logger.debug("Start time not available")
        raise HTTPException(status_code=503, detail="Startup time not available")

    start = datetime.fromisoformat(start_time)
    now = datetime.now(timezone.utc)
    uptime_seconds = int((now - start).total_seconds())

    return UptimeResponse(
        start_time=start_time,
        uptime_seconds=uptime_seconds,
    )