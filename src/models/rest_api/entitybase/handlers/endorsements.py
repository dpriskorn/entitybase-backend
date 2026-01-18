"""Handler for endorsement operations."""

import logging
from datetime import datetime

from models.infrastructure.stream.actions import EndorseAction
from models.infrastructure.stream.event import EndorseChangeEvent
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.entitybase.request.endorsements import EndorsementListRequest
from models.rest_api.entitybase.response.endorsements import (
    BatchEndorsementStatsResponse,
    EndorsementListResponse,
    EndorsementResponse,
    EndorsementStatsResponse,
)
from models.validation.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EndorsementHandler:
    """Handler for endorsement operations."""

    def endorse_statement(
        self, statement_hash: int, user_id: int, vitess_client: VitessClient
    ) -> EndorsementResponse:
        """Create an endorsement for a statement."""
        logger.debug(f"Endorsing statement {statement_hash} for user {user_id}")
        # Validate user exists
        if not vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=400)

        # Create endorsement via repository
        result = vitess_client.endorsement_repository.create_endorsement(  # type: ignore[union-attr]
            user_id, statement_hash
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to create endorsement", status_code=400
            )

        # Get the endorsement details for response
        endorsements_result = (
            vitess_client.endorsement_repository.get_statement_endorsements(
                statement_hash, limit=1, offset=0, include_removed=True
            )
        )
        if not endorsements_result.success:
            raise_validation_error(
                "Failed to retrieve endorsement details", status_code=500
            )

        endorsements_data = endorsements_result.data
        if not endorsements_data["endorsements"]:  # type: ignore[index]
            raise_validation_error(
                "Failed to retrieve created endorsement", status_code=500
            )

        # Find the endorsement we just created
        created_endorsement = next(
            (
                e
                for e in endorsements_data["endorsements"]  # type: ignore[index]
                if e.user_id == user_id and not e.removed_at
            ),
            None,
        )
        if not created_endorsement:
            raise_validation_error(
                "Failed to retrieve created endorsement", status_code=500
            )

        # Publish event
        if vitess_client.stream_producer:
            event = EndorseChangeEvent(
                hash=str(statement_hash),
                user=str(user_id),
                act=EndorseAction.ENDORSE,
                ts=datetime.utcnow(),
            )
            vitess_client.stream_producer.publish_change(event)

        return EndorsementResponse(
            id=created_endorsement.id,  # type: ignore[union-attr]
            user_id=created_endorsement.user_id,  # type: ignore[union-attr]
            hash=created_endorsement.statement_hash,  # type: ignore[union-attr]
            created_at=created_endorsement.created_at.isoformat(),  # type: ignore[union-attr]
            removed_at="",
        )

    def withdraw_endorsement(
        self, statement_hash: int, user_id: int, vitess_client: VitessClient
    ) -> EndorsementResponse:
        """Withdraw an endorsement for a statement."""
        logger.debug(
            f"Withdrawing endorsement for statement {statement_hash} by user {user_id}"
        )
        # Validate user exists
        if not vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=400)

        # Withdraw endorsement via repository
        result = vitess_client.endorsement_repository.withdraw_endorsement(
            user_id, statement_hash
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to withdraw endorsement", status_code=400
            )

        # Get the withdrawn endorsement details for response
        endorsements_result = (
            vitess_client.endorsement_repository.get_statement_endorsements(
                statement_hash, limit=1, offset=0, include_removed=True
            )
        )
        if not endorsements_result.success:
            raise_validation_error(
                "Failed to retrieve endorsement details", status_code=500
            )

        endorsements_data = endorsements_result.data
        if not endorsements_data["endorsements"]:  # type: ignore[index]
            raise_validation_error(
                "Failed to retrieve withdrawn endorsement", status_code=500
            )

        # Find the endorsement we just withdrew
        withdrawn_endorsement = next(
            (
                e
                for e in endorsements_data["endorsements"]  # type: ignore[index]
                if e.user_id == user_id and e.removed_at is not None
            ),
            None,
        )
        if not withdrawn_endorsement:
            raise_validation_error(
                "Failed to retrieve withdrawn endorsement", status_code=500
            )

        # Publish event
        if vitess_client.stream_producer:
            event = EndorseChangeEvent(
                hash=str(statement_hash),
                user=str(user_id),
                act=EndorseAction.WITHDRAW,
                ts=datetime.utcnow(),
            )
            vitess_client.stream_producer.publish_change(event)

        return EndorsementResponse(
            id=withdrawn_endorsement.id,  # type: ignore[union-attr]
            user_id=withdrawn_endorsement.user_id,  # type: ignore[union-attr]
            hash=withdrawn_endorsement.statement_hash,  # type: ignore[union-attr]
            created_at=withdrawn_endorsement.created_at.isoformat(),  # type: ignore[union-attr]
            removed_at=withdrawn_endorsement.removed_at.isoformat()  # type: ignore[union-attr]
            if withdrawn_endorsement.removed_at  # type: ignore[union-attr]
            else None,
        )

    def get_statement_endorsements(
        self,
        statement_hash: int,
        request: EndorsementListRequest,
        vitess_client: VitessClient,
    ) -> EndorsementListResponse:
        """Get endorsements for a statement."""
        logger.debug(f"Getting endorsements for statement {statement_hash}")
        result = vitess_client.endorsement_repository.get_statement_endorsements(
            statement_hash, request.limit, request.offset, request.include_removed
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get endorsements", status_code=500
            )

        # Get stats for this statement
        stats_result = (
            vitess_client.endorsement_repository.get_batch_statement_endorsement_stats(
                [statement_hash]
            )
        )
        if not stats_result.success:
            raise_validation_error("Failed to get endorsement stats", status_code=500)

        # Create StatementEndorsementStats object
        raw_stats = (
            stats_result.data[0]
            if stats_result.data
            else {
                "total_endorsements": 0,
                "active_endorsements": 0,
                "withdrawn_endorsements": 0,
            }
        )

        from models.rest_api.entitybase.response.endorsements import (
            StatementEndorsementStats,
        )

        stats = StatementEndorsementStats(
            total=raw_stats["total_endorsements"],
            active=raw_stats["active_endorsements"],
            withdrawn=raw_stats["withdrawn_endorsements"],
        )

        data = result.data
        return EndorsementListResponse(
            hash=statement_hash,
            list=data["endorsements"],  # type: ignore[index]
            count=data["total_count"],  # type: ignore[index]
            more=data["has_more"],  # type: ignore[index]
            stats=stats,
        )

    def get_user_endorsements(
        self, user_id: int, request: EndorsementListRequest, vitess_client: VitessClient
    ) -> EndorsementListResponse:
        """Get endorsements given by a user."""
        # Validate user exists
        if not vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=400)

        result = vitess_client.endorsement_repository.get_user_endorsements(
            user_id, request.limit, request.offset, request.include_removed
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get endorsements", status_code=500
            )

        data = result.data
        return EndorsementListResponse(
            user_id=user_id,
            list=data["endorsements"],  # type: ignore[index]
            count=data["total_count"],  # type: ignore[index]
            more=data["has_more"],  # type: ignore[index]
            stats=None,
        )

    def get_user_endorsement_stats(
        self, user_id: int, vitess_client: VitessClient
    ) -> EndorsementStatsResponse:
        """Get endorsement statistics for a user."""
        # Validate user exists
        if not vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=400)

        result = vitess_client.endorsement_repository.get_user_endorsement_stats(
            user_id
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get endorsement stats", status_code=500
            )

        data = result.data
        return EndorsementStatsResponse(
            user_id=user_id,
            given=data["total_endorsements_given"],  # type: ignore[index]
            active=data["total_endorsements_active"],  # type: ignore[index]
        )

    def get_batch_statement_endorsement_stats(
        self, statement_hashes: list[int], vitess_client: VitessClient
    ) -> BatchEndorsementStatsResponse:
        """Get endorsement statistics for multiple statements."""
        # Validate statement hashes exist (basic validation)
        for statement_hash in statement_hashes:
            if statement_hash <= 0:
                raise_validation_error("Invalid statement hash", status_code=400)

        result = (
            vitess_client.endorsement_repository.get_batch_statement_endorsement_stats(
                statement_hashes
            )
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get endorsement stats", status_code=500
            )

        return BatchEndorsementStatsResponse(stats=result.data)
