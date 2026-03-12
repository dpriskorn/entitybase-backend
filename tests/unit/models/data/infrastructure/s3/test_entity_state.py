"""Unit tests for EntityState model."""

import pytest

from models.data.infrastructure.s3.entity_state import EntityState


class TestEntityState:
    """Unit tests for EntityState model."""

    def test_default_values(self):
        """Test default values."""
        state = EntityState()
        assert state.is_semi_protected is False
        assert state.is_locked is False
        assert state.is_archived is False
        assert state.is_dangling is False
        assert state.is_mass_edit_protected is False
        assert state.is_deleted is False

    def test_with_all_flags(self):
        """Test with all protection flags set."""
        state = EntityState(
            is_semi_protected=True,
            is_locked=True,
            is_archived=True,
            is_dangling=True,
            is_mass_edit_protected=True,
            is_deleted=True,
        )
        assert state.is_semi_protected is True
        assert state.is_locked is True
        assert state.is_archived is True
        assert state.is_dangling is True
        assert state.is_mass_edit_protected is True
        assert state.is_deleted is True

    def test_model_dump(self):
        """Test model_dump()."""
        state = EntityState(is_locked=True, is_deleted=True)
        dumped = state.model_dump()
        assert dumped["is_locked"] is True
        assert dumped["is_deleted"] is True

    def test_model_dump_by_alias(self):
        """Test model_dump with alias."""
        state = EntityState(is_locked=True, is_deleted=True)
        dumped = state.model_dump(by_alias=True)
        assert dumped["locked"] is True
        assert dumped["deleted"] is True

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        state = EntityState(is_semi_protected=True)
        json_str = state.model_dump_json()
        assert "sp" in json_str or "semi_protected" in json_str
