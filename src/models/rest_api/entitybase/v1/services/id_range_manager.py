"""ID range management service."""

import logging
import time
from typing import Dict, Any

from pydantic import BaseModel, Field

from models.common import OperationResult
from models.data.rest_api.v1.response import RangeStatus, RangeStatuses

logger = logging.getLogger(__name__)


class IdRange(BaseModel):
    """Represents an allocated range of IDs for a specific entity type."""

    entity_type: str
    current_start: int
    current_end: int
    next_id: int


class IdRangeManager(BaseModel):
    """Manages ID range allocation and local ID generation to prevent write hotspots."""

    vitess_client: Any
    range_size: int = 1_000_000
    min_ids: Dict[str, int] = Field(default_factory=dict)
    local_ranges: Dict[str, IdRange] = {}
    worker_id: str = ""

    def set_worker_id(self, worker_id: str) -> None:
        """Set the worker ID for range allocation tracking."""
        self.worker_id = worker_id

    def get_next_id(self, entity_type: str) -> str:
        """Get the next available ID for the given entity type.
        Allocates new ranges automatically when current range is exhausted.
        """
        if entity_type not in self.local_ranges:
            self._ensure_range_available(entity_type)

        range_obj = self.local_ranges[entity_type]

        # Check if we need to allocate a new range (when 80% consumed)
        if self._should_allocate_new_range(range_obj):
            logger.info(f"Allocating new range for {entity_type} (80% consumed)")
            result = self._allocate_new_range(entity_type)
            if not result.success:
                logger.error(
                    f"Failed to allocate range for {entity_type}: {result.error}"
                )
                raise RuntimeError(
                    f"Failed to allocate range for {entity_type}: {result.error}"
                )
            self.local_ranges[entity_type] = result.data  # type: ignore[assignment]
            range_obj = result.data  # type: ignore[assignment]

        # Get next ID from current range
        id_number = range_obj.next_id
        range_obj.next_id += 1

        return f"{entity_type}{id_number}"

    def _ensure_range_available(self, entity_type: str) -> None:
        """Ensure we have an available range for the given entity type."""
        if entity_type in self.local_ranges:
            return

        # Try to allocate a new range
        try:
            result = self._allocate_new_range(entity_type)
            if not result.success:
                raise RuntimeError(result.error)
            self.local_ranges[entity_type] = result.data  # type: ignore[assignment]
        except Exception as e:
            logger.error(f"Failed to allocate range for {entity_type}: {e}")
            raise

    @staticmethod
    def _should_allocate_new_range(range_obj: IdRange) -> bool:
        """Check if we should allocate a new range (when 80% of current range is used)."""
        ids_used = range_obj.next_id - range_obj.current_start
        return ids_used > (range_obj.current_end - range_obj.current_start) * 0.8

    def _allocate_new_range(self, entity_type: str) -> OperationResult:
        """Atomically allocate a new ID range from the database.
        Uses optimistic locking to prevent conflicts between workers.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get current range end atomically
                cursor = self.vitess_client.cursor

                # Lock the row for update
                cursor.execute(
                    """
                    SELECT current_range_end, version
                    FROM id_ranges
                    WHERE entity_type = %s
                    FOR UPDATE
                    """,
                    (entity_type,),
                )

                result = cursor.fetchone()
                if not result:
                    return OperationResult(
                        success=False,
                        error=f"No range configuration found for entity type {entity_type}",
                    )

                current_end, version = result

                # Calculate new range, respecting minimum IDs
                new_start = max(current_end + 1, self.min_ids.get(entity_type, 1))
                new_end = new_start + self.range_size - 1

                # Update with optimistic locking
                cursor.execute(
                    """
                    UPDATE id_ranges
                    SET current_range_start = %s,
                        current_range_end = %s,
                        allocated_at = NOW(),
                        worker_id = %s,
                        version = version + 1
                    WHERE entity_type = %s AND version = %s
                    """,
                    (new_start, new_end, self.worker_id, entity_type, version),
                )

                if cursor.rowcount == 0:
                    # Version conflict, retry
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Range allocation conflict for {entity_type}, retrying..."
                        )
                        continue
                    else:
                        return OperationResult(
                            success=False,
                            error=f"Failed to allocate range for {entity_type} after {max_retries} attempts",
                        )

                logger.info(
                    f"Allocated new range for {entity_type}: {new_start}-{new_end}"
                )

                range_obj = IdRange(
                    entity_type=entity_type,
                    current_start=new_start,
                    current_end=new_end,
                    next_id=new_start,
                )
                return OperationResult(success=True, data=range_obj)

            except Exception as e:
                logger.error(
                    f"Range allocation attempt {attempt + 1} failed for {entity_type}: {e}"
                )
                if attempt == max_retries - 1:
                    raise
                continue

        return OperationResult(
            success=False, error=f"Failed to allocate range for {entity_type}"
        )

    def initialize_from_database(self) -> None:
        """Initialize local range state from database (for startup/recovery)."""
        try:
            cursor = self.vitess_client.cursor
            cursor.execute(
                "SELECT entity_type, current_range_start, current_range_end FROM id_ranges"
            )

            for row in cursor.fetchall():
                entity_type, start, end = row
                # Get the max used ID for this entity type to avoid collisions
                cursor.execute(
                    "SELECT MAX(CAST(SUBSTRING(entity_id, 2) AS UNSIGNED)) FROM entity_id_mapping WHERE entity_id LIKE %s",
                    (f"{entity_type}%",),
                )
                max_used_result = cursor.fetchone()
                max_used = (
                    max_used_result[0]
                    if max_used_result and max_used_result[0]
                    else 0
                )
                # Start from a high number with time-based offset to avoid collisions with leftover test data
                next_id = max(
                    start, max_used + 1, 900000 + int(time.time()) % 100000
                )
                self.local_ranges[entity_type] = IdRange(
                    entity_type=entity_type,
                    current_start=start,
                    current_end=end,
                    next_id=next_id,
                )
            logger.info(
                f"Initialized {len(self.local_ranges)} ID ranges from database"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ranges from database: {e}")
            raise

    def get_range_status(self) -> RangeStatuses:
        """Get status of all local ranges for monitoring."""
        ranges = {}
        for entity_type, range_obj in self.local_ranges.items():
            ids_used = range_obj.next_id - range_obj.current_start
            total_ids = range_obj.current_end - range_obj.current_start + 1
            utilization = ids_used / total_ids if total_ids > 0 else 0

            ranges[entity_type] = RangeStatus(
                current_start=range_obj.current_start,
                current_end=range_obj.current_end,
                next_id=range_obj.next_id,
                ids_used=ids_used,
                utilization=round(utilization * 100, 2),
            )

        return RangeStatuses(ranges=ranges)
