"""Entity update handlers."""

import logging
import re
from typing import Any

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.enums import EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    EventPublishContext,
)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.utils import raise_validation_error
from .handler import EntityHandler
from .update_transaction import UpdateTransaction
from .update_terms import EntityUpdateTermsMixin
from .update_sitelinks import EntityUpdateSitelinksMixin
from .update_lexeme import EntityUpdateLexemeMixin

logger = logging.getLogger(__name__)


class EntityUpdateHandler(
    EntityUpdateTermsMixin,
    EntityUpdateSitelinksMixin,
    EntityUpdateLexemeMixin,
    EntityHandler,
):
    """Handler for entity update operations."""

    async def _update_with_transaction(
        self,
        entity_id: str,
        modified_data: dict[str, Any],
        entity_type: EntityType,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Execute entity update using UpdateTransaction.

        This method handles the common pattern:
        1. Validation (exists, deleted, locked)
        2. UpdateTransaction creation
        3. Statement processing
        4. Revision creation
        5. Event publishing
        6. Activity logging
        7. Commit/Rollback
        """
        logger.info(f"_update_with_transaction START: entity={entity_id}, type={entity_type}")
        logger.debug(f"_update_with_transaction: modified_data keys: {list(modified_data.keys())}")

        if not self.state.vitess_client.entity_exists(entity_id):
            logger.warning(f"_update_with_transaction: entity not found: {entity_id}")
            raise_validation_error("Entity not found", status_code=404)

        if self.state.vitess_client.is_entity_deleted(entity_id):
            logger.warning(f"_update_with_transaction: entity deleted: {entity_id}")
            raise_validation_error("Entity deleted", status_code=410)

        if self.state.vitess_client.is_entity_locked(entity_id):
            logger.warning(f"_update_with_transaction: entity locked: {entity_id}")
            raise_validation_error("Entity locked", status_code=423)

        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            head_revision_id = tx.state.vitess_client.get_head(entity_id)
            logger.debug(f"_update_with_transaction: head_revision_id={head_revision_id}")

            modified_data["id"] = entity_id
            logger.debug(f"_update_with_transaction: creating PreparedRequestData")
            request_data = PreparedRequestData(**modified_data)
            logger.debug(f"_update_with_transaction: PreparedRequestData created successfully")

            logger.debug(f"_update_with_transaction: processing statements for {entity_id}")
            hash_result = tx.process_statements(entity_id, request_data, validator)
            logger.debug(f"_update_with_transaction: statements processed, hash_result.success={hash_result.success}")

            logger.debug(f"_update_with_transaction: creating revision for {entity_id}")
            response = await tx.create_revision(
                entity_id=entity_id,
                request_data=request_data,
                entity_type=entity_type,
                edit_headers=edit_headers,
                hash_result=hash_result,
            )
            logger.debug(f"_update_with_transaction: revision created: {response.revision_id}")

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

            logger.debug(f"_update_with_transaction: committing transaction for {entity_id}")
            tx.commit()
            logger.info(f"_update_with_transaction SUCCESS: entity={entity_id}, rev={response.revision_id}")
            return response
        except S3NotFoundError:
            logger.warning(f"Entity revision not found during update for {entity_id}")
            tx.rollback()
            raise_validation_error(f"Entity not found: {entity_id}", status_code=404)
        except Exception as e:
            logger.error(f"Entity update failed for {entity_id}: {e}", exc_info=True)
            tx.rollback()
            raise_validation_error(
                f"Update failed: {type(e).__name__}: {str(e)}", status_code=500
            )

    @staticmethod
    def _infer_entity_type_from_id(entity_id: str) -> EntityType | None:
        """Infer entity type from ID format.

        Returns:
            EntityType.ITEM for Q\\d+
            EntityType.PROPERTY for P\\d+
            EntityType.LEXEME for L\\d+
            None if invalid format
        """
        if re.match(r"^Q\d+$", entity_id):
            return EntityType.ITEM
        elif re.match(r"^P\d+$", entity_id):
            return EntityType.PROPERTY
        elif re.match(r"^L\d+$", entity_id):
            return EntityType.LEXEME
        return None
