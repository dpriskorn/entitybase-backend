"""Health check response models."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(description="Health status")


class HealthCheckResponse(BaseModel):
    """Detailed response model for health check."""

    status: str = Field(description="Overall health status")
    s3: str = Field(description="S3 service health status. Example: 'healthy'.")
    vitess: str = Field(description="Vitess service health status. Example: 'healthy'.")
    timestamp: str = Field(description="Timestamp of health check")


class WorkerHealthCheckResponse(BaseModel):
    """Model for worker health check response."""

    status: str = Field(description="Health status: healthy or unhealthy")
    worker_id: str = Field(description="Unique worker identifier")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Worker health details including running status and last_run"
    )
    range_status: dict[str, Any] = Field(
        default_factory=dict, description="Current ID range allocation status"
    )
