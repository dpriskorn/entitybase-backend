from typing import Dict, Any, List

from pydantic import AliasChoices, BaseModel, Field, model_validator

from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType, DeleteType
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    EventPublishContext,
    TermUpdateContext,
    EntityHeadUpdateContext,
    GeneralStatisticsContext,
    StatementWriteContext,
    ProcessEntityRevisionContext,
    CreationTransactionContext,
    SitelinkUpdateContext,
)
from models.rest_api.utils import raise_validation_error
from wikibaseintegrator.models.claims import Claims
from wikibaseintegrator.models.forms import Forms
from wikibaseintegrator.models.senses import Senses

__all__ = [
    "EntityCreateRequest",
    "LexemeUpdateRequest",
    "EntityDeleteRequest",
    "EditContext",
    "EventPublishContext",
    "TermUpdateContext",
    "EntityInsertDataRequest",
    "PreparedRequestData",
    "EntityHeadUpdateContext",
    "GeneralStatisticsContext",
    "StatementWriteContext",
    "ProcessEntityRevisionContext",
    "CreationTransactionContext",
    "SitelinkUpdateContext",
]


class EntityCreateRequest(BaseModel):
    """Request model for entity creation."""

    id: str = Field(
        default="",
        description="Entity ID (e.g., Q42) - optional for creation, auto-assigned if not provided",
    )
    type: str = Field(..., description="Entity type (item, property, lexeme)")
    labels: Dict[str, Dict[str, str]] = {}
    descriptions: Dict[str, Dict[str, str]] = {}
    claims: Dict[str, Any] = {}
    aliases: Dict[str, Any] = {}
    sitelinks: Dict[str, Any] = {}
    forms: List[Dict[str, Any]] = []
    senses: List[Dict[str, Any]] = []
    lemmas: Dict[str, Any] = {}
    language: str = Field(
        default="",
        description="Lexeme language (QID)",
        validation_alias=AliasChoices("language", "Language"),
    )
    lexical_category: str = Field(
        default="",
        description="Lexeme lexical category (QID)",
        validation_alias=AliasChoices("lexical_category", "lexicalCategory"),
    )
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    state: EntityState = Field(default=EntityState(), description="Entity state")
    is_autoconfirmed_user: bool = Field(
        default=False,
        description="User is autoconfirmed (not a new/unconfirmed account)",
    )
    is_semi_protected: bool = Field(
        default=False, description="Whether the entity is semi-protected"
    )
    is_locked: bool = Field(default=False, description="Whether the entity is locked")
    is_archived: bool = Field(
        default=False, description="Whether the entity is archived"
    )
    is_dangling: bool = Field(
        default=False, description="Whether the entity is dangling"
    )
    is_mass_edit_protected: bool = Field(
        default=False, description="Whether the entity is mass edit protected"
    )

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)  # type: ignore[no-any-return]

    def validate_claims_wbi(self) -> Claims:
        """Validate claims using WBI model."""
        if not self.claims:
            return Claims()
        return Claims().from_json(self.claims)

    def validate_forms_wbi(self) -> Forms:
        """Validate forms using WBI model."""
        if not self.forms:
            return Forms()
        forms_with_defaults = []
        for form in self.forms:
            form_copy = form.copy()
            if "grammaticalFeatures" not in form_copy:
                form_copy["grammaticalFeatures"] = []
            if "claims" not in form_copy:
                form_copy["claims"] = {}
            if "representations" not in form_copy:
                form_copy["representations"] = {}
            forms_with_defaults.append(form_copy)
        return Forms().from_json(forms_with_defaults)

    def validate_senses_wbi(self) -> Senses:
        """Validate senses using WBI model."""
        if not self.senses:
            return Senses()
        senses_with_defaults = []
        for sense in self.senses:
            sense_copy = sense.copy()
            if "glosses" not in sense_copy:
                sense_copy["glosses"] = {}
            if "claims" not in sense_copy:
                sense_copy["claims"] = {}
            senses_with_defaults.append(sense_copy)
        return Senses().from_json(senses_with_defaults)

    @model_validator(mode="after")
    def validate_wbi(self) -> "EntityCreateRequest":
        """Validate all WBI components on instantiation."""
        try:
            self.validate_claims_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid claims: {e}", status_code=400)

        try:
            self.validate_forms_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid forms: {e}", status_code=400)

        try:
            self.validate_senses_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid senses: {e}", status_code=400)

        return self


class LexemeUpdateRequest(BaseModel):
    """Request model for updating a lexeme entity."""

    id: str = Field(
        ...,
        description="Entity ID (e.g., L42)",
    )
    type: str = Field(default="lexeme", description="Entity type")
    labels: Dict[str, Dict[str, str]] = {}
    descriptions: Dict[str, Dict[str, str]] = {}
    claims: Dict[str, Any] = {}
    aliases: Dict[str, Any] = {}
    sitelinks: Dict[str, Any] = {}
    forms: List[Dict[str, Any]] = []
    senses: List[Dict[str, Any]] = []
    lemmas: Dict[str, Any] = {}
    language: str = Field(
        default="",
        description="Lexeme language (QID)",
        validation_alias=AliasChoices("language", "Language"),
    )
    lexical_category: str = Field(
        default="",
        description="Lexeme lexical category (QID)",
        validation_alias=AliasChoices("lexical_category", "lexicalCategory"),
    )
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    state: EntityState = Field(default=EntityState(), description="Entity state")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    is_not_autoconfirmed_user: bool = Field(
        default=False, description="User is not autoconfirmed (new/unconfirmed account)"
    )
    is_semi_protected: bool = Field(
        default=False, description="Whether the entity is semi-protected"
    )
    is_locked: bool = Field(default=False, description="Whether the entity is locked")
    is_archived: bool = Field(
        default=False, description="Whether the entity is archived"
    )
    is_dangling: bool = Field(
        default=False, description="Whether the entity is dangling"
    )
    is_mass_edit_protected: bool = Field(
        default=False, description="Whether the entity has mass edit protection"
    )

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)  # type: ignore[no-any-return]

    def validate_claims_wbi(self) -> Claims:
        """Validate claims using WBI model."""
        if not self.claims:
            return Claims()
        return Claims().from_json(self.claims)

    def validate_forms_wbi(self) -> Forms:
        """Validate forms using WBI model."""
        if not self.forms:
            return Forms()
        forms_with_defaults = []
        for form in self.forms:
            form_copy = form.copy()
            if "grammaticalFeatures" not in form_copy:
                form_copy["grammaticalFeatures"] = []
            if "claims" not in form_copy:
                form_copy["claims"] = {}
            if "representations" not in form_copy:
                form_copy["representations"] = {}
            forms_with_defaults.append(form_copy)
        return Forms().from_json(forms_with_defaults)

    def validate_senses_wbi(self) -> Senses:
        """Validate senses using WBI model."""
        if not self.senses:
            return Senses()
        senses_with_defaults = []
        for sense in self.senses:
            sense_copy = sense.copy()
            if "glosses" not in sense_copy:
                sense_copy["glosses"] = {}
            if "claims" not in sense_copy:
                sense_copy["claims"] = {}
            senses_with_defaults.append(sense_copy)
        return Senses().from_json(senses_with_defaults)

    @model_validator(mode="after")
    def validate_wbi(self) -> "LexemeUpdateRequest":
        """Validate all WBI components on instantiation."""
        try:
            self.validate_claims_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid claims: {e}", status_code=400)

        try:
            self.validate_forms_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid forms: {e}", status_code=400)

        try:
            self.validate_senses_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid senses: {e}", status_code=400)

        return self


class EntityDeleteRequest(BaseModel):
    """Request to delete an entity."""

    delete_type: DeleteType = Field(
        default=DeleteType.SOFT, description="Type of deletion"
    )


class EntityInsertDataRequest(BaseModel):
    """Data for inserting a revision."""

    is_mass_edit: bool
    edit_type: str
    statements: list[int] | None
    properties: list[str] | None
    property_counts: dict[str, int] | None


class PreparedRequestData(BaseModel):
    """Prepared request data with entity ID for entity creation."""

    id: str = Field(..., description="Entity ID (e.g., Q42)")
    type: str = Field(default="item", description="Entity type")
    labels: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    descriptions: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    claims: Dict[str, Any] = Field(default_factory=dict)
    aliases: Dict[str, Any] = Field(default_factory=dict)
    sitelinks: Dict[str, Any] = Field(default_factory=dict)
    forms: List[Dict[str, Any]] = Field(default_factory=list)
    senses: List[Dict[str, Any]] = Field(default_factory=list)
    lemmas: Dict[str, Any] = Field(default_factory=dict)
    language: str = Field(
        default="",
        description="Lexeme language (QID)",
        validation_alias=AliasChoices("language", "Language"),
    )
    lexical_category: str = Field(
        default="",
        description="Lexeme lexical category (QID)",
        validation_alias=AliasChoices("lexical_category", "lexicalCategory"),
    )
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    state: EntityState = Field(default_factory=EntityState, description="Entity state")
    is_autoconfirmed_user: bool = Field(
        default=False,
        description="User is autoconfirmed (not a new/unconfirmed account)",
    )
    is_semi_protected: bool = Field(
        default=False, description="Whether the entity is semi-protected"
    )
    is_locked: bool = Field(default=False, description="Whether the entity is locked")
    is_archived: bool = Field(
        default=False, description="Whether the entity is archived"
    )
    is_dangling: bool = Field(
        default=False, description="Whether the entity is dangling"
    )
    is_mass_edit_protected: bool = Field(
        default=False, description="Whether the entity is mass edit protected"
    )

    def validate_claims_wbi(self) -> Claims:
        """Validate claims using WBI model."""
        if not self.claims:
            return Claims()
        return Claims().from_json(self.claims)

    def validate_forms_wbi(self) -> Forms:
        """Validate forms using WBI model."""
        if not self.forms:
            return Forms()
        forms_with_defaults = []
        for form in self.forms:
            form_copy = form.copy()
            if "grammaticalFeatures" not in form_copy:
                form_copy["grammaticalFeatures"] = []
            if "claims" not in form_copy:
                form_copy["claims"] = {}
            if "representations" not in form_copy:
                form_copy["representations"] = {}
            forms_with_defaults.append(form_copy)
        return Forms().from_json(forms_with_defaults)

    def validate_senses_wbi(self) -> Senses:
        """Validate senses using WBI model."""
        if not self.senses:
            return Senses()
        senses_with_defaults = []
        for sense in self.senses:
            sense_copy = sense.copy()
            if "glosses" not in sense_copy:
                sense_copy["glosses"] = {}
            if "claims" not in sense_copy:
                sense_copy["claims"] = {}
            senses_with_defaults.append(sense_copy)
        return Senses().from_json(senses_with_defaults)

    @model_validator(mode="after")
    def validate_wbi(self) -> "PreparedRequestData":
        """Validate all WBI components on instantiation."""
        try:
            self.validate_claims_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid claims: {e}", status_code=400)

        try:
            self.validate_forms_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid forms: {e}", status_code=400)

        try:
            self.validate_senses_wbi()
        except Exception as e:
            raise_validation_error(f"Invalid senses: {e}", status_code=400)

        return self
