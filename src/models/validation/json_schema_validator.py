import json
import logging
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

logger = logging.getLogger(__name__)


class JsonSchemaValidator:
    def __init__(self) -> None:
        self._entity_revision_schema: dict[str, Any] | None = None
        self._statement_schema: dict[str, Any] | None = None
        self._entity_validator: Draft202012Validator | None = None
        self._statement_validator: Draft202012Validator | None = None

    def _load_schema(self, schema_path: str) -> dict[str, Any]:
        schema_file = Path(schema_path)
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_file, encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise TypeError(
                    f"Schema file must contain a JSON object: {schema_path}"
                )
            return data

    def _get_entity_revision_schema(self) -> dict:
        if self._entity_revision_schema is None:
            self._entity_revision_schema = self._load_schema(
                "src/schemas/s3-revision/latest/latest.json"
            )
        return self._entity_revision_schema

    def _get_statement_schema(self) -> dict:
        if self._statement_schema is None:
            self._statement_schema = self._load_schema(
                "src/schemas/s3-statement/latest/latest.json"
            )
        return self._statement_schema

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

    def validate_entity_revision(self, data: dict) -> None:
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
            raise errors[0]

    def validate_statement(self, data: dict) -> None:
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
            raise errors[0]
