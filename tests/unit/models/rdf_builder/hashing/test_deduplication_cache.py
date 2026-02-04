"""Tests for models.rdf_builder.hashing.deduplication_cache module."""

import pytest
from models.rdf_builder.hashing.deduplication_cache import HashDedupeBag, DedupeBag


class TestHashDedupeBag:
    """Test suite for the HashDedupeBag class."""

    def test_initialization_with_default_cutoff(self):
        """Test HashDedupeBag initialization with default cutoff value."""
        dedupe_bag = HashDedupeBag()

        assert dedupe_bag.cutoff == 5
        assert dedupe_bag.bag == {}
        assert dedupe_bag.hits == 0
        assert dedupe_bag.misses == 0

    def test_initialization_with_custom_cutoff(self):
        """Test HashDedupeBag initialization with custom cutoff value."""
        dedupe_bag = HashDedupeBag(cutoff=10)

        assert dedupe_bag.cutoff == 10
        assert dedupe_bag.bag == {}
        assert dedupe_bag.hits == 0
        assert dedupe_bag.misses == 0

    def test_already_seen_returns_false_for_first_hash(self):
        """Test that already_seen returns False for a hash not seen before."""
        dedupe_bag = HashDedupeBag()

        result = dedupe_bag.already_seen("abc123")

        assert result is False
        assert dedupe_bag.misses == 1
        assert dedupe_bag.hits == 0

    def test_already_seen_returns_true_for_duplicate_hash(self):
        """Test that already_seen returns True for a hash seen before."""
        dedupe_bag = HashDedupeBag()

        dedupe_bag.already_seen("abc123")
        result = dedupe_bag.already_seen("abc123")

        assert result is True
        assert dedupe_bag.hits == 1
        assert dedupe_bag.misses == 1

    def test_namespace_handling_wdv_exact_deduplication(self):
        """Test that 'wdv' namespace uses exact deduplication (no truncation)."""
        dedupe_bag = HashDedupeBag(cutoff=3)

        hash1 = "abc123def456"
        hash2 = "abc123xyz789"

        result1 = dedupe_bag.already_seen(hash1, namespace="wdv")
        result2 = dedupe_bag.already_seen(hash2, namespace="wdv")
        result3 = dedupe_bag.already_seen(hash1, namespace="wdv")

        assert result1 is False
        assert result2 is False
        assert result3 is True
        assert dedupe_bag.hits == 1
        assert dedupe_bag.misses == 2

    def test_collision_behavior_hash_collision(self):
        """Test that hash collisions cause false negatives (lossy cache)."""
        dedupe_bag = HashDedupeBag(cutoff=2)

        hash1 = "ab111111"
        hash2 = "ab222222"
        hash3 = "ab333333"

        result1 = dedupe_bag.already_seen(hash1)
        result2 = dedupe_bag.already_seen(hash2)
        result3 = dedupe_bag.already_seen(hash1)

        assert result1 is False
        assert result2 is False
        assert result3 is False
        assert dedupe_bag.hits == 0
        assert dedupe_bag.misses == 3

    def test_namespace_with_truncation(self):
        """Test that namespace is prepended to truncated hash."""
        dedupe_bag = HashDedupeBag(cutoff=2)

        result1 = dedupe_bag.already_seen("abc123", namespace="ns1")
        result2 = dedupe_bag.already_seen("abc456", namespace="ns2")
        result3 = dedupe_bag.already_seen("abc123", namespace="ns1")

        assert result1 is False
        assert result2 is False
        assert result3 is True

    def test_stats_returns_correct_statistics(self):
        """Test that stats() returns correct deduplication statistics."""
        dedupe_bag = HashDedupeBag(cutoff=2)

        dedupe_bag.already_seen("abc123")
        dedupe_bag.already_seen("abc123")
        dedupe_bag.already_seen("xyz456")
        dedupe_bag.already_seen("abc123")

        stats = dedupe_bag.stats()

        assert stats.hits == 2
        assert stats.misses == 2
        assert stats.size == 2
        assert stats.collision_rate == 50.0

    def test_stats_with_zero_operations(self):
        """Test that stats() returns correct statistics when no operations."""
        dedupe_bag = HashDedupeBag()

        stats = dedupe_bag.stats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.size == 0
        assert stats.collision_rate == 0.0

    def test_clear_resets_all_state(self):
        """Test that clear() resets all bag state."""
        dedupe_bag = HashDedupeBag()

        dedupe_bag.already_seen("abc123")
        dedupe_bag.already_seen("abc123")
        dedupe_bag.already_seen("xyz456")

        assert len(dedupe_bag.bag) > 0
        assert dedupe_bag.hits > 0
        assert dedupe_bag.misses > 0

        dedupe_bag.clear()

        assert dedupe_bag.bag == {}
        assert dedupe_bag.hits == 0
        assert dedupe_bag.misses == 0

    def test_clear_and_reuse(self):
        """Test that bag can be reused after clear."""
        dedupe_bag = HashDedupeBag()

        dedupe_bag.already_seen("abc123")
        dedupe_bag.clear()
        result = dedupe_bag.already_seen("abc123")

        assert result is False
        assert dedupe_bag.hits == 0
        assert dedupe_bag.misses == 1

    def test_wdv_namespace_with_different_hashes(self):
        """Test wdv namespace with completely different hashes."""
        dedupe_bag = HashDedupeBag(cutoff=2)

        result1 = dedupe_bag.already_seen("abcdef", namespace="wdv")
        result2 = dedupe_bag.already_seen("ghijkl", namespace="wdv")
        result3 = dedupe_bag.already_seen("abcdef", namespace="wdv")

        assert result1 is False
        assert result2 is False
        assert result3 is True

    def test_multiple_independent_namespaces(self):
        """Test that different namespaces are independent."""
        dedupe_bag = HashDedupeBag(cutoff=2)

        dedupe_bag.already_seen("abc123", namespace="ns1")
        dedupe_bag.already_seen("abc123", namespace="ns2")

        result1 = dedupe_bag.already_seen("abc123", namespace="ns1")
        result2 = dedupe_bag.already_seen("abc123", namespace="ns2")

        assert result1 is True
        assert result2 is True

    def test_large_cutoff_value(self):
        """Test HashDedupeBag with large cutoff value."""
        dedupe_bag = HashDedupeBag(cutoff=50)

        assert dedupe_bag.cutoff == 50

        hash_value = "a" * 100
        result = dedupe_bag.already_seen(hash_value)

        assert result is False

    def test_hash_shorter_than_cutoff(self):
        """Test behavior when hash is shorter than cutoff."""
        dedupe_bag = HashDedupeBag(cutoff=10)

        result = dedupe_bag.already_seen("abc", namespace="test")

        assert result is False
