"""Raw backlink data from database."""

from pydantic import BaseModel, Field


class BacklinkRecord(BaseModel):
    """Raw backlink data from database."""

    referencing_internal_id: int = Field(
        description="Internal ID of the referencing entity"
    )
    statement_hash: str = Field(description="Hash of the statement")
    property_id: str = Field(description="Property ID")
    rank: str = Field(description="Rank of the statement")