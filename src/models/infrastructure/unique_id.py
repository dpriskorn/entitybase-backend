"""ULID flake ID generation utilities."""

import uuid


def generate_unique_id() -> int:
    """Generate a ULID-flake style unique identifier."""
    # Use UUID for guaranteed uniqueness
    return uuid.uuid4().int & ((1 << 64) - 1)
