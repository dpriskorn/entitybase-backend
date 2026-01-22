from pydantic import BaseModel, ConfigDict, Field

from models.rest_api.entitybase.v1.response.misc import TopEntityByBacklinks


class BacklinkStatisticsData(BaseModel):
    """Container for computed backlink statistics."""

    model_config = ConfigDict(populate_by_name=True)

    total_backlinks: int = Field(
        alias="total",
        description="Total number of backlink relationships. Example: 150.",
    )
    unique_entities_with_backlinks: int = Field(
        alias="unique",
        description="Number of entities with at least one backlink. Example: 75.",
    )
    top_entities_by_backlinks: list[TopEntityByBacklinks] = Field(
        alias="top",
        description="Top entities by backlink count. Example: [{'entity_id': 'Q1', 'backlink_count': 10}].",
    )


class BacklinkStatisticsResponse(BaseModel):
    """API response for backlink statistics."""

    model_config = ConfigDict()

    date: str = Field(
        description="Date of statistics computation. Example: '2023-01-01'."
    )
    total_backlinks: int = Field(
        alias="total",
        description="Total number of backlink relationships. Example: 150.",
    )
    unique_entities_with_backlinks: int = Field(
        alias="unique",
        description="Number of entities with at least one backlink. Example: 75.",
    )
    top_entities_by_backlinks: list[TopEntityByBacklinks] = Field(
        alias="top",
        description="Top entities by backlink count. Example: [{'entity_id': 'Q1', 'backlink_count': 10}].",
    )
