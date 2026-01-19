"""Revision metadata model."""

from pydantic import BaseModel, Field


class RevisionMetadata(BaseModel):
    """Metadata for stored revisions."""

    key: str