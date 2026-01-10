from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class HealthCheckResponse(BaseModel):
    status: str
    s3: str
    vitess: str


class WorkerHealthCheck(BaseModel):
    """Model for worker health check response."""

    status: str = Field(description="Health status: healthy or unhealthy")
    worker_id: str = Field(description="Unique worker identifier")
    range_status: dict[str, Any] = Field(
        description="Current ID range allocation status"
    )
