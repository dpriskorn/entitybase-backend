import json
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

from models.data.rest_api.v1.entitybase.request import EntityJsonImportRequest

logger = logging.getLogger(__name__)


class TestJsonImportIntegration:
    """Integration tests for the /json-import endpoint."""

    @pytest.fixture
    def sample_jsonl_content(self) -> Tuple[str, List[Dict[str, Any]]]:
        """Create sample JSONL content with valid Wikidata entities."""
        entities = [
            {
                "type": "item",
                "id": "Q999999",
                "labels": {"en": {"language": "en", "value": "Test Item"}},
                "descriptions": {"en": {"language": "en", "value": "A test item"}},
                "aliases": {},
                "claims": {},
            },
            {
                "type": "property",
                "id": "P999999",
                "labels": {"en": {"language": "en", "value": "Test Property"}},
                "descriptions": {"en": {"language": "en", "value": "A test property"}},
                "aliases": {},
                "claims": {},
                "datatype": "string",
            },
        ]

        content = ""
        for entity in entities:
            content += json.dumps(entity, ensure_ascii=False) + ",\n"

        return content, entities

    @pytest.mark.integration
    def test_jsonl_file_creation(
        self, sample_jsonl_content: Tuple[str, List[Dict[str, Any]]]
    ) -> None:
        """Test that we can create a valid JSONL file."""
        content, entities = sample_jsonl_content

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(content)
            file_path = f.name

        try:
            # Verify file content
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            assert len(lines) == 2
            assert lines[0].endswith(",\n")
            assert lines[1].endswith(",\n")

            # Verify JSON parsing
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.endswith(","):
                    stripped_line = stripped_line[:-1]
                parsed = json.loads(stripped_line)
                assert "id" in parsed
                assert "type" in parsed

        finally:
            Path(file_path).unlink()

    @pytest.mark.integration
    def test_request_model_validation(
        self, sample_jsonl_content: Tuple[str, List[Dict[str, Any]]]
    ) -> None:
        """Test EntityJsonImportRequest model validation."""
        content, _ = sample_jsonl_content

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(content)
            file_path = f.name

        try:
            # Valid request
            request = EntityJsonImportRequest(
                jsonl_file_path=file_path,
                start_line=1,
                end_line=10,
                overwrite_existing=False,
                worker_id="test-worker",
            )
            assert request.start_line == 1
            assert request.worker_id == "test-worker"

            # Test defaults
            default_request = EntityJsonImportRequest(jsonl_file_path=file_path)
            assert default_request.start_line == 2  # Default value
            assert default_request.overwrite_existing is False

        finally:
            Path(file_path).unlink()

    @pytest.mark.integration
    def test_jsonl_line_processing(
        self, sample_jsonl_content: Tuple[str, List[Dict[str, Any]]]
    ) -> None:
        """Test processing of individual JSONL lines."""
        logger.info("=== test_jsonl_line_processing START ===")
        content, entities = sample_jsonl_content
        logger.debug(f"Processing {len(entities)} entities")

        lines = content.strip().split("\n")
        logger.debug(f"Split into {len(lines)} lines")

        for i, line in enumerate(lines):
            logger.debug(f"Processing line {i + 1}/{len(lines)}")
            # Remove trailing comma
            cleaned_line = line[:-1] if line.endswith(",") else line

            # Parse JSON
            parsed = json.loads(cleaned_line)

            # Verify it matches expected entity
            expected = entities[i]
            assert parsed["id"] == expected["id"]
            assert parsed["type"] == expected["type"]
            assert "labels" in parsed
            assert "descriptions" in parsed
            logger.debug(f"Line {i + 1} validated successfully")

        logger.info("=== test_jsonl_line_processing END ===")

    @pytest.mark.parametrize(
        "line_content,should_fail",
        [
            ('{"type": "item", "id": "Q1", "labels": {}}', False),
            (
                '{"type": "item", "id": "Q1", "labels": {}',
                True,
            ),  # Missing closing brace
            ("invalid json", True),
            ("", True),  # Empty line
            ("   ", True),  # Whitespace only
        ],
    )
    @pytest.mark.integration
    def test_json_parsing_edge_cases(
        self, line_content: str, should_fail: bool
    ) -> None:
        """Test JSON parsing with various edge cases."""
        try:
            if line_content.strip():
                # Remove trailing comma if present
                if line_content.endswith(","):
                    line_content = line_content[:-1]
                json.loads(line_content)
                parsed_successfully = True
            else:
                parsed_successfully = False
        except json.JSONDecodeError:
            parsed_successfully = False

        if should_fail:
            assert not parsed_successfully
        else:
            assert parsed_successfully
