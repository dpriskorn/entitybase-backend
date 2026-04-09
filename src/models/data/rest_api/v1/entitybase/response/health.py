"""Health check response models."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(description="Health status")


class HealthCheckResponse(BaseModel):
    """Detailed response model for health check."""

    model_config = {"extra": "forbid"}

    status: str = Field(description="Overall health status")
    s3: str = Field(description="S3 service health status. Example: 'healthy'.")
    vitess: str = Field(description="Vitess service health status. Example: 'healthy'.")
    timestamp: str = Field(description="Timestamp of health check")
    producers: dict[str, str] = Field(
        default_factory=dict,
        description="Kafka stream producer status. Keys: entity_change, entitydiff, user_change. Values: connected, disconnected, not_configured",
    )


class WorkerHealthCheckResponse(BaseModel):
    """Model for worker health check response."""

    status: str = Field(description="Health status: healthy or unhealthy")
    worker_id: str = Field(description="Unique worker identifier")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Worker health details including running status and last_run",
    )
    range_status: dict[str, Any] = Field(
        default_factory=dict, description="Current ID range allocation status"
    )
