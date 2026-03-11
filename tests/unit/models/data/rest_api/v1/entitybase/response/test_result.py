"""Unit tests for result response models."""

import pytest

from models.data.rest_api.v1.entitybase.response.result import (
    EntityIdResult,
    RevisionIdResult,
    RevisionResult,
)


class TestEntityIdResult:
    """Unit tests for EntityIdResult model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        result = EntityIdResult(entity_id="Q123", revision_id=1)
        assert result.entity_id == "Q123"
        assert result.revision_id == 1

    def test_model_dump(self):
        """Test model_dump()."""
        result = EntityIdResult(entity_id="Q456", revision_id=2)
        dumped = result.model_dump()
        assert dumped == {"entity_id": "Q456", "revision_id": 2}

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        result = EntityIdResult(entity_id="Q789", revision_id=3)
        json_str = result.model_dump_json()
        assert "Q789" in json_str
        assert "3" in json_str


class TestRevisionIdResult:
    """Unit tests for RevisionIdResult model."""

    def test_default_revision_id(self):
        """Test default revision_id is 0."""
        result = RevisionIdResult()
        assert result.revision_id == 0

    def test_with_revision_id(self):
        """Test with revision_id."""
        result = RevisionIdResult(revision_id=42)
        assert result.revision_id == 42

    def test_model_dump(self):
        """Test model_dump()."""
        result = RevisionIdResult(revision_id=10)
        dumped = result.model_dump()
        assert dumped == {"revision_id": 10}


class TestRevisionResult:
    """Unit tests for RevisionResult model."""

    def test_success_result(self):
        """Test successful result."""
        result = RevisionResult(success=True, revision_id=5)
        assert result.success is True
        assert result.revision_id == 5
        assert result.error == ""

    def test_failure_result(self):
        """Test failed result."""
        result = RevisionResult(success=False, error="Something went wrong")
        assert result.success is False
        assert result.revision_id == 0
        assert result.error == "Something went wrong"

    def test_model_dump(self):
        """Test model_dump()."""
        result = RevisionResult(success=True, revision_id=7)
        dumped = result.model_dump()
        assert dumped["success"] is True
        assert dumped["revision_id"] == 7
