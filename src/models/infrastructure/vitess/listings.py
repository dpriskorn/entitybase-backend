from pydantic import BaseModel


class EntityHeadListing(BaseModel):
    """Model for entity head listings."""

    entity_id: str
    head_revision_id: int


class EntityEditListing(BaseModel):
    """Model for entity edit type listings."""

    entity_id: str
    edit_type: str
    revision_id: int
