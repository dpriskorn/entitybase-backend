"""Common data models for dump workers."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EntityDumpRecord(BaseModel):
    entity_id: str
    revision_id: int
    internal_id: int
    updated_at: datetime | None = None


class DumpMetadata(BaseModel):
    dump_id: str
    generated_at: datetime
    time_range_start: datetime
    time_range_end: datetime
    entity_count: int
    format: str
    file: str
    size_bytes: int
    sha256: str
    compression: bool
    dump_type: str  # "full" or "incremental"
