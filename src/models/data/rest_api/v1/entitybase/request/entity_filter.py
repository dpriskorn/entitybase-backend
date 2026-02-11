from pydantic import BaseModel, Field


class EntityFilterRequest(BaseModel):
    model_config = {"extra": "forbid"}

    entity_type: str = Field(
        default="",
        description="Entity type to filter by (item, property, lexeme, entityschema)",
    )
    status: str = Field(
        default="",
        description="Status filter (locked, semi_protected, archived, dangling)",
    )
    edit_type: str = Field(
        default="", description="Edit type filter (lock-added, lock-removed, etc.)"
    )
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum number of entities to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of entities to skip")
