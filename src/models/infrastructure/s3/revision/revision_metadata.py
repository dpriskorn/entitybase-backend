"""Revision metadata model."""

from pydantic import BaseModel


class RevisionMetadata(BaseModel):
    """Metadata for stored revisions."""

    key: str