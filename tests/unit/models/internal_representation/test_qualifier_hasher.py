"""Unit tests for QualifierHasher."""

import unittest
from typing import Any

from models.internal_representation.qualifier_hasher import QualifierHasher


class TestQualifierHasher(unittest.TestCase):
    """Unit tests for qualifier hashing."""

    def test_compute_hash_basic(self) -> None:
        """Test basic qualifier hash computation."""
        qualifiers = {
            "P580": [
                {
                    "snaktype": "value",
                    "property": "P580",
                    "datatype": "time",
                    "datavalue": {
                        "value": {"time": "+2018-01-01T00:00:00Z"},
                        "type": "time",
                    },
                }
            ]
        }
        hash_value = QualifierHasher.compute_hash(qualifiers)
        self.assertIsInstance(hash_value, int)
        self.assertNotEqual(hash_value, 0)

    def test_compute_hash_deterministic(self) -> None:
        """Test that hash is deterministic."""
        qualifiers: dict[str, Any] = {"P1": []}
        hash1 = QualifierHasher.compute_hash(qualifiers)
        hash2 = QualifierHasher.compute_hash(qualifiers)
        self.assertEqual(hash1, hash2)

    def test_compute_hash_order_independent(self) -> None:
        """Test that hash depends on content, not key order."""
        qual1: dict[str, Any] = {"P1": [], "P2": []}
        qual2: dict[str, Any] = {"P2": [], "P1": []}
        hash1 = QualifierHasher.compute_hash(qual1)
        hash2 = QualifierHasher.compute_hash(qual2)
        self.assertEqual(hash1, hash2)


if __name__ == "__main__":
    unittest.main()
