"""Unit tests for UniqueIdGenerator."""

from models.infrastructure.unique_id import UniqueIdGenerator


class TestUniqueIdGenerator:
    """Unit tests for UniqueIdGenerator."""

    def test_generate_unique_id_returns_int(self):
        """Test that unique ID is an integer."""
        generator = UniqueIdGenerator()
        result = generator.generate_unique_id()

        assert isinstance(result, int)
        assert result > 0

    def test_generate_unique_id_increments(self):
        """Test that generated IDs are different."""
        generator = UniqueIdGenerator()
        id1 = generator.generate_unique_id()
        id2 = generator.generate_unique_id()

        assert id1 != id2

    def test_counter_property(self):
        """Test that counter returns current count."""
        generator = UniqueIdGenerator()

        assert generator.counter == 0

        generator.generate_unique_id()

        assert generator.counter == 1

    def test_generate_unique_id_within_63_bits(self):
        """Test that generated ID fits in 63 bits (signed 64-bit max)."""
        generator = UniqueIdGenerator()
        result = generator.generate_unique_id()

        assert result < (1 << 63)
