"""Tests for unique ID generation."""

import pytest

from models.infrastructure.unique_id import generate_unique_id


class TestUniqueId:
    """Test unique ID generation."""

    def test_generate_unique_id_uniqueness(self) -> None:
        """Test that generated IDs are unique."""
        ids = {generate_unique_id() for _ in range(1000)}
        assert len(ids) == 1000

    def test_generate_unique_id_type(self) -> None:
        """Test that generated ID is an integer."""
        id_value = generate_unique_id()
        assert isinstance(id_value, int)
        assert id_value > 0
