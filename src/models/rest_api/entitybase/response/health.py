"""Health check response models."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str


class HealthCheckResponse(BaseModel):
    """Detailed response model for health check."""

    status: str
    s3: str
    vitess: str


class WorkerHealthCheckResponse(BaseModel):
    """Model for worker health check response."""

    status: str = Field(description="Health status: healthy or unhealthy")
    worker_id: str = Field(description="Unique worker identifier")
    range_status: dict[str, Any] | None = Field(
        default=None,
        description="Current ID range allocation status (None for non-ID workers)"
    )
