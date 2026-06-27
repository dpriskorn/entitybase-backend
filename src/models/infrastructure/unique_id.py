"""Unique ID generation module.

This module provides dependency injection (DI) for unique ID generation.

Dependency Injection (DI) is a design pattern where dependencies (like
UniqueIdGenerator) are passed into classes/functions rather than being
created globally. This improves testability - you can inject a mock generator
in tests to get deterministic, predictable IDs.

Example usage in tests:
    from models.infrastructure.unique_id import UniqueIdGenerator

    # Create a custom generator for deterministic/testing IDs
    generator = UniqueIdGenerator()

    # Inject it into IdResolver (or any class that accepts it)
    resolver = IdResolver(mysql_client=mock_client, unique_id_generator=generator)

    # Now IDs are deterministic and controllable in tests
    id1 = generator.generate_unique_id()
"""

import uuid
import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class UniqueIdGenerator(BaseModel):
    """Generates unique 64-bit IDs."""

    model_config = {"arbitrary_types_allowed": True}

    _counter: int = 0

    @property
    def counter(self) -> int:
        """Return the current counter value."""
        return self._counter

    def generate_unique_id(self) -> int:
        """Generate a unique 63-bit ID compatible with both SQLite and MySQL.

        SQLite INTEGER is signed 64-bit (max 2^63-1), so we mask to 63 bits.
        MySQL BIGINT UNSIGNED supports up to 2^64-1, but 63 bits is sufficient.
        """
        self._counter += 1
        return (uuid.uuid4().int + self._counter) & ((1 << 63) - 1)
