"""Entity status handlers (lock, archive, semi-protect)."""

import logging

from models.data.rest_api.v1.entitybase.request.entity.entity_status import (
    EntityStatusRequest,
)
from models.data.rest_api.v1.entitybase.response.entity.entity_status import (
    EntityStatusResponse,
)
from models.rest_api.entitybase.v1.handler import Handler
from models.rest_api.entitybase.v1.services.status_service import (
    StatusOperation,
    StatusService,
)

logger = logging.getLogger(__name__)


# noinspection PyArgumentList
class EntityStatusHandler(Handler):
    """Handler for entity status change operations."""

    def lock(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Lock an entity from edits."""
        logger.debug(f"Locking entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(entity_id, StatusOperation.LOCK, request)

    def unlock(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Remove lock from an entity."""
        logger.debug(f"Unlocking entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(entity_id, StatusOperation.UNLOCK, request)

    def archive(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Archive an entity."""
        logger.debug(f"Archiving entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(entity_id, StatusOperation.ARCHIVE, request)

    def unarchive(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Unarchive an entity."""
        logger.debug(f"Unarchiving entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(
            entity_id, StatusOperation.UNARCHIVE, request
        )

    def semi_protect(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Semi-protect an entity."""
        logger.debug(f"Semi-protecting entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(
            entity_id, StatusOperation.SEMI_PROTECT, request
        )

    def unsemi_protect(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Remove semi-protection from an entity."""
        logger.debug(f"Removing semi-protection from entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(
            entity_id, StatusOperation.UNSEMI_PROTECT, request
        )

    def mass_edit_protect(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Add mass edit protection to an entity."""
        logger.debug(f"Adding mass edit protection to entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(
            entity_id, StatusOperation.MASS_EDIT_PROTECT, request
        )

    def mass_edit_unprotect(
        self, entity_id: str, request: EntityStatusRequest
    ) -> EntityStatusResponse:
        """Remove mass edit protection from an entity."""
        logger.debug(f"Removing mass edit protection from entity: {entity_id}")
        status_service = StatusService(state=self.state)
        return status_service.change_status(
            entity_id, StatusOperation.MASS_EDIT_UNPROTECT, request
        )
