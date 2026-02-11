"""JSON schema validation utilities."""

import json
import logging
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from pydantic import BaseModel, Field

from models.config.settings import settings
from models.data.json_schema import JsonSchema
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class JsonSchemaValidator(BaseModel):
    """Validator for JSON schemas used in entity validation."""

    s3_revision_version: str = Field(
        default_factory=lambda: settings.s3_schema_revision_version
    )
    s3_statement_version: str = Field(
        default_factory=lambda: settings.s3_statement_version
    )
    s3_snak_version: str = Field(default_factory=lambda: settings.s3_snak_version)
    entity_change_version: str = Field(
        default_factory=lambda: settings.streaming_entity_change_version
    )
    entity_revision_schema: JsonSchema | None = Field(default=None)
    statement_schema: JsonSchema | None = Field(default=None)
    recentchange_schema: JsonSchema | None = Field(default=None)
    snak_schema: JsonSchema | None = Field(default=None)
    entity_validator: Draft202012Validator | None = Field(default=None)
    statement_validator: Draft202012Validator | None = Field(default=None)
    recentchange_validator: Draft202012Validator | None = Field(default=None)
    snak_validator: Draft202012Validator | None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}

    @staticmethod
    def _load_schema(schema_path: str) -> JsonSchema:
        schema_file = Path(schema_path)
        if not schema_file.exists():
            raise_validation_error(
                f"Schema file not found: {schema_path}", status_code=500
            )

        with open(schema_file, encoding="utf-8") as f:
            if schema_file.suffix == ".yaml":
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
            if not isinstance(data, dict):
                raise_validation_error(
                    f"Schema file must contain a JSON/YAML object: {schema_path}",
                    status_code=500,
                )
            return JsonSchema(data=data)

    def _get_entity_revision_schema(self) -> JsonSchema:
        if self.entity_revision_schema is None:
            schema_path = Path(
                f"schemas/entitybase/s3/revision/{self.s3_revision_version}/schema.yaml"
            )
            self.entity_revision_schema = self._load_schema(str(schema_path))
        return self.entity_revision_schema

    def _get_statement_schema(self) -> JsonSchema:
        if self.statement_schema is None:
            schema_path = Path(
                f"schemas/entitybase/s3/statement/{self.s3_statement_version}/schema.yaml"
            )
            self.statement_schema = self._load_schema(str(schema_path))
        return self.statement_schema

    def _get_recentchange_schema(self) -> JsonSchema:
        if self.recentchange_schema is None:
            schema_path = Path(
                f"schemas/entitybase/events/entity_change/{self.entity_change_version}/schema.yaml"
            )
            self.recentchange_schema = self._load_schema(str(schema_path))
        return self.recentchange_schema

    def _get_snak_schema(self) -> JsonSchema:
        if self.snak_schema is None:
            schema_path = Path(
                f"schemas/entitybase/s3/snak/{self.s3_snak_version}/schema.yaml"
            )
            self.snak_schema = self._load_schema(str(schema_path))
        return self.snak_schema

    def _get_entity_validator(self) -> Draft202012Validator:
        if self.entity_validator is None:
            schema = self._get_entity_revision_schema().data
            self.entity_validator = Draft202012Validator(schema)
        return self.entity_validator

    def _get_statement_validator(self) -> Draft202012Validator:
        if self.statement_validator is None:
            schema = self._get_statement_schema().data
            self.statement_validator = Draft202012Validator(schema)
        return self.statement_validator

    def _get_recentchange_validator(self) -> Draft202012Validator:
        if self.recentchange_validator is None:
            schema = self._get_recentchange_schema().data
            self.recentchange_validator = Draft202012Validator(schema)
        return self.recentchange_validator

    def _get_snak_validator(self) -> Draft202012Validator:
        if self.snak_validator is None:
            schema = self._get_snak_schema().data
            self.snak_validator = Draft202012Validator(schema)
        return self.snak_validator

    def validate_statement(self, data: dict) -> None:
        """Validate statement data against schema."""
        validator = self._get_statement_validator()
        errors = list(validator.iter_errors(data))
        if errors:
            error_messages = [
                {
                    "field": f"{'/' + '/'.join(str(p) for p in error.path) if error.path else '/'}",
                    "message": error.message,
                    "path": error.path,
                }
                for error in errors
            ]
            logger.error(f"Statement validation failed: {error_messages}")
            raise_validation_error(str(errors[0]), status_code=400)

    # TODO: Implement usage in change streaming handlers when WMF recentchange events are consumed
    def validate_recentchange(self, data: dict) -> None:
        """Validate recent change data against schema."""
        validator = self._get_recentchange_validator()
        errors = list(validator.iter_errors(data))
        if errors:
            error_messages = [
                {
                    "field": f"{'/' + '/'.join(str(p) for p in error.path) if error.path else '/'}",
                    "message": error.message,
                    "path": error.path,
                }
                for error in errors
            ]
            logger.error(f"RecentChange validation failed: {error_messages}")
            raise_validation_error(str(errors[0]), status_code=400)
