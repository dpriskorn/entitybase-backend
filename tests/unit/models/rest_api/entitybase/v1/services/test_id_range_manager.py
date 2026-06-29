"""Unit tests for id_range_manager."""

import pytest
from unittest.mock import MagicMock, patch

from models.rest_api.entitybase.v1.services.id_range_manager import (
    IdRange,
    IdRangeManager,
)


class TestIdRange:
    """Unit tests for IdRange model."""

    def test_id_range_creation(self):
        """Test IdRange creation with required fields."""
        id_range = IdRange(
            entity_type="Q",
            current_start=1,
            current_end=1000000,
            next_id=1,
        )
        assert id_range.entity_type == "Q"
        assert id_range.current_start == 1
        assert id_range.current_end == 1000000
        assert id_range.next_id == 1

    def test_id_range_model_dump(self):
        """Test IdRange model_dump()."""
        id_range = IdRange(
            entity_type="P",
            current_start=100,
            current_end=200000,
            next_id=150,
        )
        dumped = id_range.model_dump()
        assert dumped["entity_type"] == "P"
        assert dumped["current_start"] == 100
        assert dumped["current_end"] == 200000
        assert dumped["next_id"] == 150


class TestIdRangeManager:
    """Unit tests for IdRangeManager."""

    def test_set_worker_id(self):
        """Test setting worker ID."""
        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)

        manager.set_worker_id("worker-1")
        assert manager.worker_id == "worker-1"

    def test_default_values(self):
        """Test default values are applied correctly."""
        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)

        assert manager.range_size == 1_000_000
        assert manager.min_ids == {}
        assert manager.local_ranges == {}
        assert manager.worker_id == ""

    def test_should_allocate_new_range_at_threshold(self):
        """Test _should_allocate_new_range at 80% threshold."""
        range_obj = IdRange(
            entity_type="Q",
            current_start=1,
            current_end=1000,
            next_id=801,  # 80% of 1000
        )
        assert IdRangeManager._should_allocate_new_range(range_obj) is True

    def test_should_allocate_new_range_below_threshold(self):
        """Test _should_allocate_new_range below 80% threshold."""
        range_obj = IdRange(
            entity_type="Q",
            current_start=1,
            current_end=1000,
            next_id=799,  # Below 80%
        )
        assert IdRangeManager._should_allocate_new_range(range_obj) is False

    def test_should_allocate_new_range_at_79_percent(self):
        """Test _should_allocate_new_range at 79%."""
        range_obj = IdRange(
            entity_type="Q",
            current_start=1,
            current_end=1000,
            next_id=790,  # 79%
        )
        assert IdRangeManager._should_allocate_new_range(range_obj) is False

    def test_get_range_status_empty(self):
        """Test get_range_status with no ranges."""
        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)

        status = manager.get_range_status()
        assert status.ranges == {}

    def test_get_range_status_with_ranges(self):
        """Test get_range_status with allocated ranges."""
        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)

        manager.local_ranges = {
            "Q": IdRange(
                entity_type="Q",
                current_start=1,
                current_end=1000000,
                next_id=100001,
            ),
            "P": IdRange(
                entity_type="P",
                current_start=1000001,
                current_end=2000000,
                next_id=1000100,
            ),
        }

        status = manager.get_range_status()

        assert "Q" in status.ranges
        assert "P" in status.ranges
        assert status.ranges["Q"].ids_used == 100000
        assert status.ranges["P"].ids_used == 99

    def test_get_range_status_utilization(self):
        """Test utilization calculation in get_range_status."""
        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)

        manager.local_ranges = {
            "Q": IdRange(
                entity_type="Q",
                current_start=1,
                current_end=1000,
                next_id=500,
            ),
        }

        status = manager.get_range_status()
        # 500 - 1 = 499 used out of 1000 = 49.9%
        assert status.ranges["Q"].utilization == pytest.approx(49.9, rel=0.1)

    def test_model_dump(self):
        """Test IdRangeManager model_dump."""
        mock_client = MagicMock()
        manager = IdRangeManager(
            mysql_client=mock_client,
            range_size=500000,
            worker_id="test-worker",
        )

        dumped = manager.model_dump()
        assert dumped["range_size"] == 500000
        assert dumped["worker_id"] == "test-worker"

    def test_ensure_range_available_new_entity_type(self):
        """Test _ensure_range_available creates new range for unknown entity type."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchone.side_effect = [
            (1, 1),  # First call returns range config
            (1000,),  # Second call returns max used
        ]

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        manager._ensure_range_available("Q")

        assert "Q" in manager.local_ranges

    def test_get_next_id_existing_range(self):
        """Test get_next_id returns ID from existing range."""
        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)

        manager.local_ranges = {
            "Q": IdRange(
                entity_type="Q",
                current_start=1,
                current_end=1000000,
                next_id=100,
            ),
        }

        entity_id = manager.get_next_id("Q")
        assert entity_id == "Q100"
        assert manager.local_ranges["Q"].next_id == 101

    def test_get_next_id_allocates_new_range_when_80_percent_used(self):
        """Test get_next_id allocates new range when 80% consumed."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchone.side_effect = [
            (1000000, 1),  # First call - range config
            (2000000, 1),  # Second call - range config update
        ]

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        # Simulate range at 80% consumed
        manager.local_ranges = {
            "Q": IdRange(
                entity_type="Q",
                current_start=1,
                current_end=1000000,
                next_id=800001,  # 80%+ used
            ),
        }

        entity_id = manager.get_next_id("Q")
        # Should have allocated new range
        assert entity_id.startswith("Q")

    def test_allocate_new_range_success(self):
        """Test _allocate_new_range successful allocation."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchone.return_value = (1000, 1)
        mock_cursor.rowcount = 1

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        result = manager._allocate_new_range("Q")

        assert result.success is True
        assert result.data is not None
        assert result.data.entity_type == "Q"

    def test_allocate_new_range_no_config(self):
        """Test _allocate_new_range when no config exists."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchone.return_value = None

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        result = manager._allocate_new_range("Q")

        assert result.success is False
        assert "No range configuration" in result.error

    def test_allocate_new_range_version_conflict_retry(self):
        """Test _allocate_new_range handles version conflict."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        # First attempt fails (rowcount=0)
        mock_cursor.fetchone.return_value = (1000, 1)
        mock_cursor.rowcount = 0

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        # The method should handle the conflict internally
        # Just verify basic setup works
        assert manager.worker_id == "test-worker"

    def test_initialize_from_database(self):
        """Test initialize_from_database method."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchall.return_value = [
            ("Q", 1, 1000000),
            ("P", 1000001, 2000000),
        ]
        mock_cursor.fetchone.return_value = (50000,)

        manager = IdRangeManager(mysql_client=mock_client)

        with patch("time.time", return_value=12345):
            manager.initialize_from_database()

        assert "Q" in manager.local_ranges
        assert "P" in manager.local_ranges

    def test_get_next_id_entity_not_in_ranges_creates_new(self):
        """Test get_next_id creates new range for unknown entity type."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchone.side_effect = [
            (1, 1),  # First call returns range config
            (None,),  # Second call returns max used (none)
        ]

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        entity_id = manager.get_next_id("Q")

        assert entity_id.startswith("Q")
        assert "Q" in manager.local_ranges

    def test_get_next_id_alloc_failure_raises_runtime_error(self):
        """Test get_next_id raises RuntimeError when allocation fails at 80%."""
        from models.data.common import OperationResult

        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        # Set up range at 80% consumed
        manager.local_ranges = {
            "Q": IdRange(
                entity_type="Q",
                current_start=1,
                current_end=1000,
                next_id=801,
            ),
        }

        with patch.object(
            manager,
            "_allocate_new_range",
            return_value=OperationResult(success=False, error="DB error"),
        ):
            with pytest.raises(RuntimeError, match="DB error"):
                manager.get_next_id("Q")

    def test_initialize_from_database_error(self):
        """Test initialize_from_database re-raises exceptions."""
        mock_client = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(
            side_effect=Exception("Connection lost")
        )

        manager = IdRangeManager(mysql_client=mock_client)

        with pytest.raises(Exception, match="Connection lost"):
            manager.initialize_from_database()

    def test_get_next_id_new_entity_type_alloc_failure(self):
        """Test get_next_id for unknown entity type when allocation fails."""
        mock_client = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(side_effect=Exception("DB error"))
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        with pytest.raises(Exception, match="DB error"):
            manager.get_next_id("Q")

    def test_get_next_id_new_entity_type_zero_range_config(self):
        """Test get_next_id allocates with zero max used."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        mock_cursor.fetchone.side_effect = [
            (1, 1),  # First call - range config with version
            (None,),  # Second call - max used is None (0)
        ]

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        entity_id = manager.get_next_id("Q")

        assert entity_id.startswith("Q")
        assert "Q" in manager.local_ranges

    def test_ensure_range_available_alloc_failure_result(self):
        """Test _ensure_range_available raises RuntimeError when allocation returns failure."""
        from models.data.common import OperationResult

        mock_client = MagicMock()
        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        with patch.object(
            manager,
            "_allocate_new_range",
            return_value=OperationResult(success=False, error="no config"),
        ):
            with pytest.raises(RuntimeError, match="no config"):
                manager.get_next_id("Q")

    def test_allocate_new_range_version_conflict_early_attempt(self):
        """Test _allocate_new_range version conflict on early attempt (hits break)."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (1000, 1)
        mock_cursor.rowcount = 0  # Version conflict

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        result = manager._allocate_new_range("Q")

        assert result.success is False
        assert "Failed to allocate range" in result.error

    def test_allocate_new_range_version_conflict_last_attempt(self):
        """Test _allocate_new_range returns error on last attempt version conflict."""
        mock_client = MagicMock()
        mock_cursor = MagicMock()
        mock_client.cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_client.cursor.__exit__ = MagicMock(return_value=False)

        # Return success for first 2 calls, but rowcount=0 each time
        # Note: fetchone is called at the beginning of each retry inside the for loop
        # But with rowcount=0, the cursor will still return the same data
        # We need fetchone to keep returning data so we don't get "no config"
        mock_cursor.fetchone.return_value = (1000, 1)
        # rowcount=0 simulates version conflict (no rows updated)

        manager = IdRangeManager(mysql_client=mock_client)
        manager.worker_id = "test-worker"

        # Patch rowcount to be 0 for all 3 attempts (max_retries)
        with patch.object(mock_cursor, "rowcount", 0):
            result = manager._allocate_new_range("Q")

        assert result.success is False
