"""Entity update lexeme mixins."""

import logging
import re
from typing import Any

from pydantic import BaseModel

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.enums import EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import LexemeUpdateRequest
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    EventPublishContext,
)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.utils import raise_validation_error
from .update_transaction import UpdateTransaction

logger = logging.getLogger(__name__)


class EntityUpdateLexemeMixin(BaseModel):
    """Mixin for lexeme-specific update operations."""

    model_config = {"extra": "allow"}

    state: Any

    async def update_lexeme(
        self,
        entity_id: str,
        request: LexemeUpdateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update a lexeme with proper transaction handling for S3 lexeme terms.

        This method processes lexeme terms (form representations and sense glosses)
        within the transaction scope, ensuring S3 data is cleaned up on rollback.

        Args:
            entity_id: The lexeme ID (must match L\\d+ format)
            request: EntityUpdateRequest containing the lexeme data
            edit_headers: Edit metadata headers
            validator: Optional validator for statement processing

        Returns:
            EntityResponse with updated lexeme data
        """
        logger.debug(f"Updating lexeme {entity_id}")

        if not re.match(r"^L\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be a lexeme (format: L followed by digits)",
                status_code=400,
            )

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id

        try:
            head_revision_id = tx.state.vitess_client.get_head(entity_id)

            data = request.data.copy()
            data["id"] = entity_id

            forms = data.get("forms", [])
            senses = data.get("senses", [])
            lemmas = data.get("lemmas", {})
            tx.process_lexeme_terms(forms, senses, lemmas)

            data["forms"] = forms
            data["senses"] = senses
            request_data = PreparedRequestData(**data)

            hash_result = tx.process_statements(entity_id, request_data, validator)

            response = await tx.create_revision(
                entity_id=entity_id,
                request_data=request_data,
                entity_type=EntityType(request.type),
                edit_headers=edit_headers,
                hash_result=hash_result,
            )

            edit_context = EditContext(
                user_id=edit_headers.x_user_id,
                edit_summary=edit_headers.x_edit_summary,
            )
            event_context = EventPublishContext(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type=ChangeType.EDIT,
                from_revision_id=head_revision_id,
                changed_at=None,
            )
            tx.publish_event(event_context, edit_context)

            if edit_headers.x_user_id:
                activity_result = (
                    self.state.vitess_client.user_repository.log_user_activity(
                        user_id=edit_headers.x_user_id,
                        activity_type=UserActivityType.ENTITY_EDIT,
                        entity_id=entity_id,
                        revision_id=response.revision_id,
                    )
                )
                if not activity_result.success:
                    logger.warning(
                        f"Failed to log user activity: {activity_result.error}"
                    )

            tx.commit()
            return response
        except S3NotFoundError:
            logger.warning(f"Lexeme revision not found during update for {entity_id}")
            tx.rollback()
            raise_validation_error(f"Entity not found: {entity_id}", status_code=404)
        except Exception as e:
            logger.error(f"Lexeme update failed for {entity_id}: {e}", exc_info=True)
            tx.rollback()
            raise_validation_error(
                f"Update failed: {type(e).__name__}: {str(e)}", status_code=500
            )
