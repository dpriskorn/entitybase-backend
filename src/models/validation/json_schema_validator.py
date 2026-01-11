"""JSON schema validation utilities."""

import json
import logging
from pathlib import Path
from typing import Any, cast

from models.validation.utils import raise_validation_error
from jsonschema import Draft202012Validator

logger = logging.getLogger(__name__)


class JsonSchemaValidator:
    """Validator for JSON schemas used in entity validation."""

    def __init__(
        self,
        s3_revision_version: str = "latest",
        s3_statement_version: str = "latest",
        wmf_recentchange_version: str = "latest",
    ) -> None:
        self.s3_revision_version = s3_revision_version
        self.s3_statement_version = s3_statement_version
        self.wmf_recentchange_version = wmf_recentchange_version
        self._entity_revision_schema: dict[str, Any] | None = None
        self._statement_schema: dict[str, Any] | None = None
        self._recentchange_schema: dict[str, Any] | None = None
        self._entity_validator: Draft202012Validator | None = None
        self._statement_validator: Draft202012Validator | None = None
        self._recentchange_validator: Draft202012Validator | None = None

    def _load_schema(self, schema_path: str) -> dict[str, Any]:
        schema_file = Path(schema_path)
        if not schema_file.exists():
            raise_validation_error(
                f"Schema file not found: {schema_path}", status_code=500
            )

        with open(schema_file, encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise_validation_error(
                    f"Schema file must contain a JSON object: {schema_path}",
                    status_code=500,
                )
            return cast(dict[str, Any], data)

    def _get_entity_revision_schema(self) -> dict:
        if self._entity_revision_schema is None:
            self._entity_revision_schema = self._load_schema(
                f"src/schemas/entitybase/s3-revision/{self.s3_revision_version}/schema.json"
            )
        return self._entity_revision_schema

    def _get_statement_schema(self) -> dict:
        if self._statement_schema is None:
            self._statement_schema = self._load_schema(
                f"src/schemas/s3-statement/{self.s3_statement_version}/schema.json"
            )
        return self._statement_schema

    def _get_recentchange_schema(self) -> dict:
        if self._recentchange_schema is None:
            self._recentchange_schema = self._load_schema(
                f"src/schemas/wmf-recentchange/{self.wmf_recentchange_version}/schema.json"
            )
        return self._recentchange_schema

    def _get_entity_validator(self) -> Draft202012Validator:
        if self._entity_validator is None:
            schema = self._get_entity_revision_schema()
            self._entity_validator = Draft202012Validator(schema)
        return self._entity_validator

    def _get_statement_validator(self) -> Draft202012Validator:
        if self._statement_validator is None:
            schema = self._get_statement_schema()
            self._statement_validator = Draft202012Validator(schema)
        return self._statement_validator

    def _get_recentchange_validator(self) -> Draft202012Validator:
        if self._recentchange_validator is None:
            schema = self._get_recentchange_schema()
            self._recentchange_validator = Draft202012Validator(schema)
        return self._recentchange_validator

    def validate_entity_revision(self, data: dict) -> None:
        """Validate entity revision data against schema."""
        validator = self._get_entity_validator()
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
            logger.error(f"Entity validation failed: {error_messages}")
            raise_validation_error(str(errors[0]), status_code=400)

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
