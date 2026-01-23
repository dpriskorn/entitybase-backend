"""Unit tests for event."""

from datetime import datetime, timezone

from models.data.infrastructure.stream.actions import EndorseAction
from models.data.infrastructure.stream.change_type import ChangeType
from models.infrastructure.stream.event import (
    EndorseChangeEvent,
    NewThankEvent,
    EntityChangeEvent,
)


class TestEndorseChangeEvent:
    """Unit tests for EndorseChangeEvent."""
    pass

class TestNewThankEvent:
    """Unit tests for NewThankEvent."""

    pass

class TestEntityChangeEvent:
    """Unit tests for EntityChangeEvent."""
    pass
