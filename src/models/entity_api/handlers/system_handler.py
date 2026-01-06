from fastapi import Response
from starlette import status

from models.entity import HealthCheckResponse


def health_check(response: Response) -> HealthCheckResponse:
    """Health check endpoint for monitoring system status."""
    from models.entity_api.main import app

    clients = getattr(app.state, "clients", None)

    if clients is None:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthCheckResponse(
            status="starting", s3="disconnected", vitess="disconnected"
        )

    s3_status = (
        "connected" if clients.s3 and clients.s3.check_connection() else "disconnected"
    )
    vitess_status = (
        "connected"
        if clients.vitess and clients.vitess.check_connection()
        else "disconnected"
    )

    return HealthCheckResponse(status="ok", s3=s3_status, vitess=vitess_status)