"""Entity status handlers (lock, archive, semi-protect)."""

import logging

from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
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
        self, entity_id: str, request: EntityStatusRequest, edit_headers: EditHeaders
    ) -> EntityStatusResponse:
        """Lock an entity from edits."""
        logger.debug(f"Locking entity: {entity_id}")
        status_service = StatusService(state=self.state)
        response = status_service.change_status(
            entity_id, StatusOperation.LOCK, request
        )
        self._log_activity(edit_headers, UserActivityType.ENTITY_LOCK, entity_id)
        return response

    def unlock(
        self, entity_id: str, request: EntityStatusRequest, edit_headers: EditHeaders
    ) -> EntityStatusResponse:
        """Remove lock from an entity."""
        logger.debug(f"Unlocking entity: {entity_id}")
        status_service = StatusService(state=self.state)
        response = status_service.change_status(
            entity_id, StatusOperation.UNLOCK, request
        )
        self._log_activity(edit_headers, UserActivityType.ENTITY_UNLOCK, entity_id)
        return response

    def archive(
        self, entity_id: str, request: EntityStatusRequest, edit_headers: EditHeaders
    ) -> EntityStatusResponse:
        """Archive an entity."""
        logger.debug(f"Archiving entity: {entity_id}")
        status_service = StatusService(state=self.state)
        response = status_service.change_status(
            entity_id, StatusOperation.ARCHIVE, request
        )
        self._log_activity(edit_headers, UserActivityType.ENTITY_ARCHIVE, entity_id)
        return response

    def unarchive(
        self, entity_id: str, request: EntityStatusRequest, edit_headers: EditHeaders
    ) -> EntityStatusResponse:
        """Unarchive an entity."""
        logger.debug(f"Unarchiving entity: {entity_id}")
        status_service = StatusService(state=self.state)
        response = status_service.change_status(
            entity_id, StatusOperation.UNARCHIVE, request
        )
        self._log_activity(edit_headers, UserActivityType.ENTITY_UNARCHIVE, entity_id)
        return response

    def _log_activity(
        self, edit_headers: EditHeaders, activity_type: UserActivityType, entity_id: str
    ) -> None:
        """Log user activity."""
        if edit_headers.x_user_id > 0:
            activity_result = (
                self.state.vitess_client.user_repository.log_user_activity(
                    user_id=edit_headers.x_user_id,
                    activity_type=activity_type,
                    entity_id=entity_id,
                    revision_id=0,
                )
            )
            if not activity_result.success:
                logger.warning(f"Failed to log user activity: {activity_result.error}")

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
