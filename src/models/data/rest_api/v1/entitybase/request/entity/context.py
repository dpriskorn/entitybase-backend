"""Context models for entity operations."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

from models.data.infrastructure.s3 import EntityType, EditType


class EventPublishContext(BaseModel):
    """Context for publishing entity change events."""

    entity_id: str = Field(..., description="Entity ID (e.g., Q42)")
    revision_id: int = Field(..., description="Revision ID of the change")
    change_type: str = Field(..., description="Type of change")
    changed_at: Any = Field(default=None, description="Timestamp of change")
    from_revision_id: int = Field(
        default=0, description="Previous revision ID (0 for creations)"
    )


class TermUpdateContext(BaseModel):
    """Context for term update operations (labels, descriptions)."""

    language_code: str = Field(..., description="Language code from URL path")
    language: str = Field(..., description="Language code from request body")
    value: str = Field(..., description="Term value")


class EntityHeadUpdateContext(BaseModel):
    """Context for entity head update operations."""

    entity_id: str = Field(..., description="Entity ID")
    expected_head: int = Field(
        default=0, description="Expected current head revision ID"
    )
    new_head: int = Field(default=0, description="New head revision ID")
    is_semi_protected: bool = Field(default=False, description="Semi-protection status")
    is_locked: bool = Field(default=False, description="Lock status")
    is_archived: bool = Field(default=False, description="Archive status")
    is_dangling: bool = Field(default=False, description="Dangling status")
    is_mass_edit_protected: bool = Field(
        default=False, description="Mass edit protection status"
    )
    is_deleted: bool = Field(default=False, description="Deletion status")
    is_redirect: bool = Field(default=False, description="Redirect status")


class GeneralStatisticsContext(BaseModel):
    """Context for general statistics insertion."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_statements: int = Field(..., description="Total number of statements")
    total_qualifiers: int = Field(..., description="Total number of qualifiers")
    total_references: int = Field(..., description="Total number of references")
    total_items: int = Field(..., description="Total number of items")
    total_lexemes: int = Field(..., description="Total number of lexemes")
    total_properties: int = Field(..., description="Total number of properties")
    total_sitelinks: int = Field(..., description="Total number of sitelinks")
    total_terms: int = Field(..., description="Total number of terms")
    terms_per_language: Dict[str, int] = Field(
        default_factory=dict, description="Terms count per language"
    )
    terms_by_type: Dict[str, int] = Field(
        default_factory=dict, description="Terms count by type"
    )


class StatementWriteContext(BaseModel):
    """Context for writing RDF statements."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    output: Any = Field(..., description="TextIO output stream")
    entity_id: str = Field(..., description="Entity ID")
    rdf_statement: Any = Field(..., description="RDF statement to write")
    shape: Any = Field(..., description="Property shape")
    property_registry: Any = Field(..., description="Property registry")
    dedupe: Any = Field(default=None, description="Deduplication cache")


class ProcessEntityRevisionContext(BaseModel):
    """Context for processing entity revisions."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity_id: str = Field(..., description="Entity ID")
    request_data: Dict[str, Any] = Field(..., description="Request data dictionary")
    entity_type: Any = Field(..., description="Entity type enum")
    edit_type: Any = Field(default=None, description="Edit type")
    edit_headers: Any = Field(..., description="Edit headers")
    is_creation: bool = Field(
        default=False, description="Whether this is a creation operation"
    )
    validator: Any = Field(default=None, description="Validator instance")


class CreationTransactionContext(BaseModel):
    """Context for creation transaction execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    tx: Any = Field(..., description="Creation transaction instance")
    entity_id: str = Field(..., description="Entity ID")
    request_data: Any = Field(..., description="Prepared request data")
    request: Any = Field(..., description="Original create request")
    edit_headers: Any = Field(..., description="Edit headers")
    validator: Any = Field(default=None, description="Validator instance")


class SitelinkUpdateContext(BaseModel):
    """Context for sitelink update operations."""

    entity_id: str = Field(..., description="Entity ID")
    site: str = Field(..., description="Site key (e.g., enwiki)")
    title: str = Field(..., description="Page title")
    badges: List[str] = Field(default_factory=list, description="Badge IDs")


class RevisionContext(BaseModel):
    """Context for revision processing operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity_id: str
    request_data: Dict[str, Any]
    entity_type: EntityType
    edit_type: EditType | None = Field(default=None)
    edit_summary: str = ""
    is_creation: bool = False
    vitess_client: Any
    s3_client: Any
    stream_producer: Any = Field(default=None)
    validator: Any | None = Field(default=None)
