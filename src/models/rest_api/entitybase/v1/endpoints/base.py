"""Base utilities for entity endpoints."""

from typing import Any

from fastapi import Request

from models.rest_api.utils import raise_validation_error, validate_state_clients
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.delete import EntityDeleteHandler
from models.rest_api.entitybase.v1.handlers.entity.status import EntityStatusHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.statement import StatementHandler
from models.rest_api.entitybase.v1.handlers.entity.backlinks import BacklinkHandler


def get_entity_read_handler(state: Any) -> EntityReadHandler:
    """Create and return an EntityReadHandler with validated state."""
    validate_state_clients(state)
    return EntityReadHandler(state=state)


def get_entity_delete_handler(state: Any) -> EntityDeleteHandler:
    """Create and return an EntityDeleteHandler with validated state."""
    validate_state_clients(state)
    return EntityDeleteHandler(state=state)


def get_entity_status_handler(state: Any) -> EntityStatusHandler:
    """Create and return an EntityStatusHandler with validated state."""
    validate_state_clients(state)
    return EntityStatusHandler(state=state)


def get_entity_update_handler(state: Any) -> EntityUpdateHandler:
    """Create and return an EntityUpdateHandler with validated state."""
    validate_state_clients(state)
    return EntityUpdateHandler(state=state)


def get_statement_handler(state: Any) -> StatementHandler:
    """Create and return a StatementHandler with validated state."""
    validate_state_clients(state)
    return StatementHandler(state=state)


def get_backlink_handler(state: Any) -> BacklinkHandler:
    """Create and return a BacklinkHandler with validated state."""
    validate_state_clients(state)
    return BacklinkHandler(state=state)


def get_state_from_request(req: Request) -> Any:
    """Extract and return state from request."""
    return req.app.state.state_handler
