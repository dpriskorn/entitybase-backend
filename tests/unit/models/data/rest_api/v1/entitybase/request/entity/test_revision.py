"""Unit tests for CreateRevisionRequest model."""

import pytest

from models.data.infrastructure.s3.enums import EntityType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.entity.revision import (
    CreateRevisionRequest,
)
from models.data.rest_api.v1.entitybase.response.statement import StatementHashResult


class TestCreateRevisionRequest:
    """Unit tests for CreateRevisionRequest."""

    def test_basic_instantiation(self):
        """Test basic instantiation with required fields."""
        request_data = PreparedRequestData(id="Q1")
        hash_result = StatementHashResult(statements=[12345])

        request = CreateRevisionRequest(
            entity_id="Q1",
            new_revision_id=1,
            head_revision_id=0,
            request_data=request_data,
            entity_type=EntityType.ITEM,
            hash_result=hash_result,
            edit_type="manual-create",
        )

        assert request.entity_id == "Q1"
        assert request.new_revision_id == 1
        assert request.head_revision_id == 0
        assert request.entity_type == EntityType.ITEM
        assert request.edit_type == "manual-create"

    def test_default_values(self):
        """Test default values are applied correctly."""
        request_data = PreparedRequestData(id="Q1")
        hash_result = StatementHashResult(statements=[12345])

        request = CreateRevisionRequest(
            entity_id="Q1",
            new_revision_id=1,
            head_revision_id=0,
            request_data=request_data,
            entity_type=EntityType.ITEM,
            hash_result=hash_result,
            edit_type="manual-create",
        )

        assert request.is_mass_edit is False
        assert request.edit_summary == ""
        assert request.is_semi_protected is False
        assert request.is_locked is False
        assert request.is_archived is False
        assert request.is_dangling is False
        assert request.is_mass_edit_protected is False
        assert request.is_creation is False
        assert request.user_id == 0

    def test_all_optional_flags_true(self):
        """Test all optional boolean flags can be set to True."""
        request_data = PreparedRequestData(id="Q1")
        hash_result = StatementHashResult(statements=[12345])

        request = CreateRevisionRequest(
            entity_id="Q1",
            new_revision_id=2,
            head_revision_id=1,
            request_data=request_data,
            entity_type=EntityType.PROPERTY,
            hash_result=hash_result,
            edit_type="mass-edit",
            is_mass_edit=True,
            edit_summary="Bulk update",
            is_semi_protected=True,
            is_locked=True,
            is_archived=True,
            is_dangling=True,
            is_mass_edit_protected=True,
            is_creation=True,
            user_id=42,
        )

        assert request.is_mass_edit is True
        assert request.edit_summary == "Bulk update"
        assert request.is_semi_protected is True
        assert request.is_locked is True
        assert request.is_archived is True
        assert request.is_dangling is True
        assert request.is_mass_edit_protected is True
        assert request.is_creation is True
        assert request.user_id == 42

    def test_different_entity_types(self):
        """Test CreateRevisionRequest works with different entity types."""
        request_data = PreparedRequestData(id="Q1")
        hash_result = StatementHashResult(statements=[12345])

        for entity_type in [EntityType.ITEM, EntityType.PROPERTY, EntityType.LEXEME]:
            request = CreateRevisionRequest(
                entity_id="Q1",
                new_revision_id=1,
                head_revision_id=0,
                request_data=request_data,
                entity_type=entity_type,
                hash_result=hash_result,
                edit_type="manual-create",
            )
            assert request.entity_type == entity_type

    def test_model_dump(self):
        """Test model_dump() includes all fields."""
        request_data = PreparedRequestData(id="Q1")
        hash_result = StatementHashResult(statements=[12345])

        request = CreateRevisionRequest(
            entity_id="Q1",
            new_revision_id=1,
            head_revision_id=0,
            request_data=request_data,
            entity_type=EntityType.ITEM,
            hash_result=hash_result,
            edit_type="manual-create",
            edit_summary="Test edit",
            user_id=123,
        )

        dumped = request.model_dump()

        assert dumped["entity_id"] == "Q1"
        assert dumped["new_revision_id"] == 1
        assert dumped["head_revision_id"] == 0
        assert dumped["entity_type"] == EntityType.ITEM
        assert dumped["edit_type"] == "manual-create"
        assert dumped["edit_summary"] == "Test edit"
        assert dumped["user_id"] == 123

    def test_model_dump_json(self):
        """Test model_dump_json() works correctly."""
        request_data = PreparedRequestData(id="Q1")
        hash_result = StatementHashResult(statements=[12345])

        request = CreateRevisionRequest(
            entity_id="Q1",
            new_revision_id=1,
            head_revision_id=0,
            request_data=request_data,
            entity_type=EntityType.ITEM,
            hash_result=hash_result,
            edit_type="manual-create",
        )

        json_str = request.model_dump_json()
        assert "Q1" in json_str
        assert "1" in json_str
