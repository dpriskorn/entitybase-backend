from pydantic import BaseModel, ConfigDict, Field


class UserStatsData(BaseModel):
    """Container for computed user statistics."""

    model_config = ConfigDict(populate_by_name=True)

    total_users: int = Field(
        alias="total",
        description="Total number of users. Example: 1000.",
    )
    active_users: int = Field(
        alias="active",
        description="Number of active users. Example: 500.",
    )


class UserStatsResponse(BaseModel):
    """API response for user statistics."""

    model_config = ConfigDict(populate_by_name=True)

    date: str = Field(
        description="Date of statistics computation. Example: '2023-01-01'."
    )
    total_users: int = Field(
        alias="total",
        description="Total number of users. Example: 1000.",
    )
    active_users: int = Field(
        alias="active",
        description="Number of active users. Example: 500.",
    )
