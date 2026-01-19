import pytest

pytestmark = pytest.mark.unit

from models.rdf_builder.hashing.value_node_hasher import ValueNodeHasher


class TestValueNodeHasher:
    def test_format_precision_no_leading_zero(self) -> None:
        """Test precision formatting without leading zero."""
        assert ValueNodeHasher._format_precision(1.0e-5) == "1.0E-5"

    def test_format_precision_remove_leading_zero(self) -> None:
        """Test precision formatting with leading zero removal."""
        assert ValueNodeHasher._format_precision(1.0e-05) == "1.0E-5"

    def test_format_precision_positive(self) -> None:
        """Test precision formatting for positive exponents."""
        assert ValueNodeHasher._format_precision(1.23e10) == "1.2E10"

    def test_hash_time_value(self) -> None:
        """Test time value hashing."""
        result = ValueNodeHasher.hash_time_value("2023-01-01", 11, 0, "Q1985727")
        # MD5 hash of "t:2023-01-01:11:0:Q1985727"
        expected = "f5d8c3a1e9b2c7d4f6e8a9b0c1d2e3f4"  # Placeholder, actual hash
        assert len(result) == 32  # MD5 hex length
        assert result.isalnum()

    def test_hash_quantity_value_basic(self) -> None:
        """Test basic quantity value hashing."""
        result = ValueNodeHasher.hash_quantity_value("123", "Q11573")
        # MD5 hash of "q:123:Q11573"
        assert len(result) == 32
        assert result.isalnum()

    def test_hash_quantity_value_with_bounds(self) -> None:
        """Test quantity value hashing with bounds."""
        result = ValueNodeHasher.hash_quantity_value("123", "Q11573", "124", "122")
        # MD5 hash of "q:123:Q11573:124:122"
        assert len(result) == 32

    def test_hash_quantity_value_partial_bounds(self) -> None:
        """Test quantity value hashing with only upper bound."""
        result = ValueNodeHasher.hash_quantity_value("123", "Q11573", "124")
        # MD5 hash of "q:123:Q11573:124"
        assert len(result) == 32

    def test_hash_entity_value(self) -> None:
        """Test entity value hashing."""
        result = ValueNodeHasher.hash_entity_value("Q42")
        # MD5 hash of "Q42"
        assert len(result) == 32
        assert result.isalnum()

    def test_hash_time_value_different_inputs(self) -> None:
        """Test that different inputs produce different hashes."""
        hash1 = ValueNodeHasher.hash_time_value("2023-01-01", 11, 0, "Q1985727")
        hash2 = ValueNodeHasher.hash_time_value("2023-01-02", 11, 0, "Q1985727")
        assert hash1 != hash2

    def test_hash_quantity_value_different_inputs(self) -> None:
        """Test that different quantity inputs produce different hashes."""
        hash1 = ValueNodeHasher.hash_quantity_value("123", "Q11573")
        hash2 = ValueNodeHasher.hash_quantity_value("124", "Q11573")
        assert hash1 != hash2
