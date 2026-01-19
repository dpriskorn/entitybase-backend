from enum import Enum


class UserActivityType(str, Enum):
    """User activity types for entity operations."""

    ENTITY_CREATE = "entity_create"  # Creating new entities
    ENTITY_EDIT = "entity_edit"  # Editing existing entities
    ENTITY_REVERT = "entity_revert"  # Reverting entity changes
    ENTITY_DELETE = "entity_delete"  # Deleting entities
    ENTITY_UNDELETE = "entity_undelete"  # Undeleting entities
    ENTITY_LOCK = "entity_lock"  # Locking entities
    ENTITY_UNLOCK = "entity_unlock"  # Unlocking entities
    ENTITY_ARCHIVE = "entity_archive"  # Archiving entities
    ENTITY_UNARCHIVE = "entity_unarchive"  # Unarchiving entities
    THANK_SENT = "thank_sent"  # Sending thanks for a revision
    THANK_RECEIVED = "thank_received"  # Receiving thanks for a revision
    ENDORSEMENT_GIVEN = "endorsement_given"  # Giving endorsement to a statement
    ENDORSEMENT_WITHDRAWN = (
        "endorsement_withdrawn"  # Withdrawing endorsement from a statement
    )
