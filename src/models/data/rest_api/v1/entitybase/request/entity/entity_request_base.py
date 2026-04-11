from typing import TYPE_CHECKING, Any, Dict, List, Self

from pydantic import AliasChoices, BaseModel, Field, model_validator

from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType
from models.rest_api.utils import raise_validation_error

if TYPE_CHECKING:
    from wikibaseintegrator.models.claims import Claims
    from wikibaseintegrator.models.forms import Forms
    from wikibaseintegrator.models.senses import Senses


class EntityRequestBase(BaseModel):
    """Base class for entity requests with common fields and validation."""

    id: str = Field(
        default="",
        description="Entity ID (e.g., Q42) - optional for creation, auto-assigned if not provided",
    )
    type: str = Field(
        default="item", description="Entity type (item, property, lexeme)"
    )
    labels: Dict[str, Dict[str, str]] = Field(
        default_factory=dict, description="Entity labels by language code"
    )
    descriptions: Dict[str, Dict[str, str]] = Field(
        default_factory=dict, description="Entity descriptions by language code"
    )
    claims: Dict[str, Any] = Field(
        default_factory=dict, description="Entity claims/statements by property"
    )
    aliases: Dict[str, Any] = Field(
        default_factory=dict, description="Entity aliases by language code"
    )
    sitelinks: Dict[str, Any] = Field(
        default_factory=dict, description="Entity sitelinks by site"
    )
    forms: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lexeme forms"
    )
    senses: List[Dict[str, Any]] = Field(
        default_factory=list, description="Lexeme senses"
    )
    lemmas: Dict[str, Any] = Field(
        default_factory=dict, description="Lexeme lemmas by language code"
    )
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

    @property
    def data(self) -> Self:
        """Returns the model itself for type safety."""
        return self

    def validate_claims_wbi(self) -> "Claims":
        """Validate claims using WBI model."""
        from wikibaseintegrator.models.claims import Claims

        if not self.claims:
            return Claims()
        return Claims().from_json(self.claims)

    def validate_forms_wbi(self) -> "Forms":
        """Validate forms using WBI model."""
        from wikibaseintegrator.models.forms import Forms

        if not self.forms:
            return Forms()
        forms_with_defaults = []
        for form in self.forms:
            form_copy = form.copy()
            if "id" not in form_copy:
                form_copy["id"] = None
            if "grammaticalFeatures" not in form_copy:
                form_copy["grammaticalFeatures"] = []
            if "claims" not in form_copy:
                form_copy["claims"] = {}
            if "representations" not in form_copy:
                form_copy["representations"] = {}
            forms_with_defaults.append(form_copy)
        return Forms().from_json(forms_with_defaults)

    def validate_senses_wbi(self) -> "Senses":
        """Validate senses using WBI model."""
        from wikibaseintegrator.models.senses import Senses

        if not self.senses:
            return Senses()
        senses_with_defaults = []
        for sense in self.senses:
            sense_copy = sense.copy()
            if "id" not in sense_copy:
                sense_copy["id"] = None
            if "glosses" not in sense_copy:
                sense_copy["glosses"] = {}
            if "claims" not in sense_copy:
                sense_copy["claims"] = {}
            senses_with_defaults.append(sense_copy)
        return Senses().from_json(senses_with_defaults)

    @model_validator(mode="after")
    def validate_wbi(self) -> Self:
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
