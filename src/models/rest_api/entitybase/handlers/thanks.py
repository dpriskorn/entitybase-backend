"""Handler for thanks operations."""

import logging

from models.infrastructure.vitess.vitess_client import VitessClient
from models.rest_api.entitybase.request.thanks import ThanksListRequest
from models.rest_api.entitybase.response.thanks import ThankResponse, ThanksListResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class ThanksHandler:
    """Handler for thanks operations."""

    def send_thank(
        self,
        entity_id: str,
        revision_id: int,
        from_user_id: int,
        vitess_client: VitessClient,
    ) -> ThankResponse:
        """Send a thank for a revision."""
        logger.debug(
            f"Sending thank from user {from_user_id} for {entity_id}:{revision_id}"
        )
        # Validate user exists
        if not vitess_client.user_repository.user_exists(from_user_id):
            raise_validation_error("User not registered", status_code=400)

        # Send thank via repository
        result = vitess_client.thanks_repository.send_thank(
            from_user_id, entity_id, revision_id
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to send thank", status_code=400
            )

        # Get the thank details for response
        revision_thanks = vitess_client.thanks_repository.get_revision_thanks(
            entity_id, revision_id
        )
        if not revision_thanks.success:
            raise_validation_error("Failed to retrieve thank details", status_code=500)

        # Find the thank we just created
        thanks = revision_thanks.data
        if not thanks:
            raise_validation_error("Failed to retrieve thank details", status_code=500)

        created_thank = next(
            (t for t in thanks if t.from_user_id == from_user_id), None
        )
        if not created_thank:
            raise_validation_error("Failed to retrieve created thank", status_code=500)

        assert created_thank is not None  # Already checked above
        return ThankResponse(
            thank_id=created_thank.id,
            from_user_id=created_thank.from_user_id,
            to_user_id=created_thank.to_user_id,
            entity_id=created_thank.entity_id,
            revision_id=created_thank.revision_id,
            created_at=created_thank.created_at.isoformat(),
        )

    def get_thanks_received(
        self, user_id: int, request: ThanksListRequest, vitess_client: VitessClient
    ) -> ThanksListResponse:
        """Get thanks received by user."""
        # Validate user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        result = vitess_client.thanks_repository.get_thanks_received(
            user_id, request.hours, request.limit, request.offset
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get thanks", status_code=500
            )

        data = result.data
        assert isinstance(data, dict)
        return ThanksListResponse(
            user_id=user_id,
            thanks=data["thanks"],
            total_count=data["total_count"],
            has_more=data["has_more"],
        )

    def get_thanks_sent(
        self, user_id: int, request: ThanksListRequest, vitess_client: VitessClient
    ) -> ThanksListResponse:
        """Get thanks sent by user."""
        # Validate user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        result = vitess_client.thanks_repository.get_thanks_sent(
            user_id, request.hours, request.limit, request.offset
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get thanks", status_code=500
            )

        data = result.data
        assert isinstance(data, dict)
        return ThanksListResponse(
            user_id=user_id,
            thanks=data["thanks"],
            total_count=data["total_count"],
            has_more=data["has_more"],
        )

    def get_revision_thanks(
        self, entity_id: str, revision_id: int, vitess_client: VitessClient
    ) -> ThanksListResponse:
        """Get all thanks for a specific revision."""
        result = vitess_client.thanks_repository.get_revision_thanks(
            entity_id, revision_id
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get thanks", status_code=500
            )

        assert isinstance(result.data, list)
        return ThanksListResponse(
            user_id=0,  # Not user-specific
            thanks=result.data,
            total_count=len(result.data),
            has_more=False,
        )
