from fastapi import Response
from starlette import status

from models.api_models import HealthCheckResponse
from models.infrastructure import S3Client, VitessClient


def health_check(response: Response) -> HealthCheckResponse:
    """Health check endpoint for monitoring system status."""
    from models.rest_api.main import app

    clients = getattr(app.state, "clients", None)
    clients.s3: S3Client
    clients.vitess: VitessClient

    if clients is None:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthCheckResponse(
            status="starting", s3="disconnected", vitess="disconnected"
        )

    s3_status = (
        "connected"
        if clients.s3 and clients.s3.healthy_connection()
        else "disconnected"
    )
    vitess_status = (
        "connected"
        if clients.vitess and clients.vitess.healthy_connection()
        else "disconnected"
    )

    return HealthCheckResponse(status="ok", s3=s3_status, vitess=vitess_status)
