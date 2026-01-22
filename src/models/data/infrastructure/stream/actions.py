"""Action enums for events."""

from enum import Enum


class EndorseAction(str, Enum):
    """Actions for endorsement changes."""

    ENDORSE = "endorse"
    WITHDRAW = "withdraw"
