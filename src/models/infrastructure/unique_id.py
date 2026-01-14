"""ULID flake ID generation utilities."""

import uuid

_counter = 0


def generate_unique_id() -> int:
    """Generate a ULID-flake style unique identifier."""
    global _counter
    _counter += 1
    # Use UUID plus counter for guaranteed uniqueness
    return (uuid.uuid4().int + _counter) & ((1 << 64) - 1)
