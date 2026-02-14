import uuid
import logging

logger = logging.getLogger(__name__)

_counter = 0


def generate_unique_id() -> int:
    """Generate a unique 64-bit ID."""
    global _counter
    _counter += 1
    return (uuid.uuid4().int + _counter) & ((1 << 64) - 1)
