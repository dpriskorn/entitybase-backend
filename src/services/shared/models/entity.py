from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EntityCreateRequest(BaseModel):
    id: str = Field(..., description="Entity ID (e.g., Q42)")
    type: str = Field(default="item", description="Entity type")
    labels: Optional[Dict[str, Dict[str, str]]] = None
    descriptions: Optional[Dict[str, Dict[str, str]]] = None
    claims: Optional[Dict[str, List]] = None
    aliases: Optional[Dict[str, List]] = None
    sitelinks: Optional[Dict[str, Any]] = None
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    edit_type: str = Field(default="", description="Text classification of edit type (e.g., 'bot-import', 'cleanup')")
    
    model_config = ConfigDict(extra="allow")
    
    @property
    def data(self) -> Dict[str, Any]:
        """Return entity as dict for compatibility with existing code"""
        return self.model_dump(exclude_unset=True)


class EntityResponse(BaseModel):
    id: str
    revision_id: int
    data: Dict[str, Any]


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str


class RawRevisionErrorType(str, Enum):
    """Enum for raw revision endpoint error types"""
    ENTITY_NOT_FOUND = "entity_not_found"
    NO_REVISIONS = "no_revisions"
    REVISION_NOT_FOUND = "revision_not_found"


class RawRevisionErrorResponse(BaseModel):
    """Error response for raw revision endpoint"""
    detail: str = Field(description="Human-readable error message")
    error_type: RawRevisionErrorType = Field(description="Machine-readable error type")
