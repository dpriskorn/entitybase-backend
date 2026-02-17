"""Handler for endorsement operations."""

import logging
from datetime import datetime, timezone

from models.data.infrastructure.stream.actions import EndorseAction
from models.infrastructure.stream.event import EndorseChangeEvent
from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.request import EndorsementListRequest
from models.data.rest_api.v1.entitybase.response import (
    BatchEndorsementStatsResponse,
    EndorsementListResponse,
    EndorsementResponse,
    EndorsementStatsResponse,
    StatementEndorsementResponse,
)
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EndorsementHandler(Handler):
    """Handler for endorsement operations."""

    def endorse_statement(
        self, statement_hash: int, user_id: int
    ) -> EndorsementResponse:
        """Create an endorsement for a statement."""
        logger.debug(f"Endorsing statement {statement_hash} for user {user_id}")
        self._validate_user(user_id)

        result = self.state.vitess_client.endorsement_repository.create_endorsement(
            user_id, statement_hash
        )
        if not result.success:
            self._handle_endorsement_error(result.error, "create")

        created_endorsement = self._get_and_validate_endorsement(
            statement_hash, user_id, must_be_active=True
        )
        self._publish_endorsement_event(statement_hash, user_id, EndorseAction.ENDORSE)

        return EndorsementResponse(
            id=created_endorsement.id,
            user_id=created_endorsement.user_id,
            hash=created_endorsement.statement_hash,
            created_at=created_endorsement.created_at.isoformat(),
            removed_at="",
        )

    def withdraw_endorsement(
        self, statement_hash: int, user_id: int
    ) -> EndorsementResponse:
        """Withdraw an endorsement for a statement."""
        logger.debug(
            f"Withdrawing endorsement for statement {statement_hash} by user {user_id}"
        )
        self._validate_user(user_id)

        result = self.state.vitess_client.endorsement_repository.withdraw_endorsement(
            user_id, statement_hash
        )
        if not result.success:
            self._handle_endorsement_error(result.error, "withdraw")

        withdrawn_endorsement = self._get_and_validate_endorsement(
            statement_hash, user_id, must_be_active=False
        )
        self._publish_endorsement_event(statement_hash, user_id, EndorseAction.WITHDRAW)

        return EndorsementResponse(
            id=withdrawn_endorsement.id,
            user_id=withdrawn_endorsement.user_id,
            hash=withdrawn_endorsement.statement_hash,
            created_at=withdrawn_endorsement.created_at.isoformat(),
            removed_at=withdrawn_endorsement.removed_at.isoformat()
            if withdrawn_endorsement.removed_at
            else None,
        )

    def _validate_user(self, user_id: int) -> None:
        """Validate that user exists."""
        logger.debug("Validating user exists")
        if not self.state.vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=404)

    def _handle_endorsement_error(self, error: str | None, action: str) -> None:
        """Handle endorsement operation errors."""
        error_msg = error or f"Failed to {action} endorsement"
        if "not found" in error_msg.lower():
            raise_validation_error(error_msg, status_code=404)
        else:
            raise_validation_error(error_msg, status_code=400)

    def _get_and_validate_endorsement(
        self, statement_hash: int, user_id: int, must_be_active: bool
    ) -> StatementEndorsementResponse:
        """Get and validate endorsement details."""
        endorsements_result = (
            self.state.vitess_client.endorsement_repository.get_statement_endorsements(
                statement_hash, limit=1, offset=0, include_removed=True
            )
        )
        if not endorsements_result.success:
            raise_validation_error(
                "Failed to retrieve endorsement details", status_code=500
            )

        endorsements_data = endorsements_result.data
        if not endorsements_data["endorsements"]:
            raise_validation_error("Failed to retrieve endorsement", status_code=500)

        return self._find_endorsement_by_user(
            endorsements_data["endorsements"], user_id, must_be_active
        )

    def _find_endorsement_by_user(
        self,
        endorsements: list[StatementEndorsementResponse],
        user_id: int,
        must_be_active: bool,
    ) -> StatementEndorsementResponse:
        """Find endorsement by user ID."""
        filter_fn = (
            lambda e: e.user_id == user_id and not e.removed_at
            if must_be_active
            else e.user_id == user_id and e.removed_at is not None
        )
        endorsement = next((e for e in endorsements if filter_fn(e)), None)
        if not endorsement:
            raise_validation_error("Failed to retrieve endorsement", status_code=500)
        return endorsement

    def _publish_endorsement_event(
        self, statement_hash: int, user_id: int, action: EndorseAction
    ) -> None:
        """Publish endorsement change event."""
        if self.state.vitess_client.stream_producer:
            event = EndorseChangeEvent(
                hash=str(statement_hash),
                user=str(user_id),
                act=action,
                ts=datetime.now(timezone.utc),
            )
            self.state.vitess_client.stream_producer.publish_change(event)

    def get_statement_endorsements(
        self,
        statement_hash: int,
        request: EndorsementListRequest,
    ) -> EndorsementListResponse:
        """Get endorsements for a statement."""
        logger.debug(f"Getting endorsements for statement {statement_hash}")
        result = (
            self.state.vitess_client.endorsement_repository.get_statement_endorsements(
                statement_hash, request.limit, request.offset, request.include_removed
            )
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get endorsements", status_code=500
            )

        # Get stats for this statement
        stats_result = self.state.vitess_client.endorsement_repository.get_batch_statement_endorsement_stats(
            [statement_hash]
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

        from models.data.rest_api.v1.entitybase.response import (
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
        self, user_id: int, request: EndorsementListRequest
    ) -> EndorsementListResponse:
        """Get endorsements given by a user."""
        # Validate user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=404)

        result = self.state.vitess_client.endorsement_repository.get_user_endorsements(
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

    def get_user_endorsement_stats(self, user_id: int) -> EndorsementStatsResponse:
        """Get endorsement statistics for a user."""
        # Validate user exists
        if not self.state.vitess_client.user_repository.user_exists(user_id):  # type: ignore[union-attr]
            raise_validation_error("User not registered", status_code=404)

        result = (
            self.state.vitess_client.endorsement_repository.get_user_endorsement_stats(
                user_id
            )
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
        self, statement_hashes: list[int]
    ) -> BatchEndorsementStatsResponse:
        """Get endorsement statistics for multiple statements."""
        from models.data.rest_api.v1.entitybase.response import (
            StatementEndorsementStats,
        )

        for statement_hash in statement_hashes:
            if statement_hash <= 0:
                raise_validation_error("Invalid statement hash", status_code=400)

        result = self.state.vitess_client.endorsement_repository.get_batch_statement_endorsement_stats(
            statement_hashes
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to get endorsement stats", status_code=500
            )

        stats_list = [
            StatementEndorsementStats(
                total=item["total_endorsements"],
                active=item["active_endorsements"],
                withdrawn=item["withdrawn_endorsements"],
            )
            for item in result.data
        ]

        return BatchEndorsementStatsResponse(stats=stats_list)
