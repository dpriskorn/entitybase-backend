"""Unit tests for ReferenceHasher."""

import unittest
from models.internal_representation.reference_hasher import ReferenceHasher


class TestReferenceHasher(unittest.TestCase):
    """Unit tests for reference hashing."""

    def test_compute_hash_basic(self) -> None:
        """Test basic reference hash computation."""
        reference = {
            "snaks": {
                "P854": [
                    {
                        "snaktype": "value",
                        "property": "P854",
                        "hash": "abc123",
                        "datavalue": {"value": "http://example.com", "type": "string"},
                    }
                ]
            },
            "snaks-order": ["P854"],
        }
        hash_value = ReferenceHasher.compute_hash(reference)
        self.assertIsInstance(hash_value, int)
        self.assertNotEqual(hash_value, 0)

    def test_compute_hash_excludes_hash_field(self) -> None:
        """Test that the reference 'hash' field is excluded from hashing."""
        ref1 = {"snaks": {"P1": []}, "hash": "oldhash"}
        ref2 = {"snaks": {"P1": []}, "hash": "different"}
        hash1 = ReferenceHasher.compute_hash(ref1)
        hash2 = ReferenceHasher.compute_hash(ref2)
        self.assertEqual(hash1, hash2)

    def test_compute_hash_deterministic(self) -> None:
        """Test that hash is deterministic."""
        reference: dict[str, Any] = {"snaks": {"P1": []}}
        hash1 = ReferenceHasher.compute_hash(reference)
        hash2 = ReferenceHasher.compute_hash(reference)
        self.assertEqual(hash1, hash2)

    def test_compute_hash_order_independent(self) -> None:
        """Test that snaks-order affects hash."""
        ref1 = {"snaks": {"P1": [], "P2": []}, "snaks-order": ["P1", "P2"]}
        ref2 = {"snaks": {"P1": [], "P2": []}, "snaks-order": ["P2", "P1"]}
        hash1 = ReferenceHasher.compute_hash(ref1)
        hash2 = ReferenceHasher.compute_hash(ref2)
        self.assertNotEqual(hash1, hash2)


if __name__ == "__main__":
    unittest.main()
