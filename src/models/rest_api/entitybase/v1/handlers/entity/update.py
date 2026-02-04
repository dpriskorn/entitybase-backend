"""Entity update handlers."""

import logging
import re
from typing import Any

from models.common import EditHeaders
from models.data.infrastructure.s3.enums import EditType, EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.utils import raise_validation_error
from .handler import EntityHandler
from .update_transaction import UpdateTransaction
# Import internal-only EntityUpdateRequest for lexeme compatibility
from models.data.rest_api.v1.entitybase.request.entity.crud import EntityUpdateRequest as InternalEntityUpdateRequest

logger = logging.getLogger(__name__)


class EntityUpdateHandler(EntityHandler):
    """Handler for entity update operations"""

    async def update_entity(
        self,
        entity_id: str,
        request: InternalEntityUpdateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update an existing entity with transaction rollback (deprecated - use specialized methods)."""
        # Check entity exists (404 if not)
        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        # Check deletion status (410 if deleted)
        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        # Check lock status (423 if locked)
        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        # Create transaction
        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            # Get head revision
            head_revision_id = tx.state.vitess_client.get_head(entity_id)
            # Prepare data
            request_data = PreparedRequestData(**request.data.copy())
            request_data["id"] = entity_id
            # Process statements
            hash_result = tx.process_statements(entity_id, request_data, validator)
            # Create revision
            response = await tx.create_revision(
                entity_id=entity_id,
                request_data=request_data,
                entity_type=EntityType(request.type),
                edit_headers=edit_headers,
                hash_result=hash_result,
            )
            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type=ChangeType.EDIT,
                edit_headers=edit_headers,
                from_revision_id=head_revision_id,
                changed_at=None,
            )
            # Log activity
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

            # Commit
            tx.commit()
            return response
        except Exception as e:
            logger.error(f"Entity update failed for {entity_id}: {e}", exc_info=True)
            logger.error(f"Entity update failed - full details: {type(e).__name__}: {str(e)}")
            logger.error(f"Entity update failed - traceback:", exc_info=True)
            tx.rollback()
            raise_validation_error(f"Update failed: {type(e).__name__}: {str(e)}", status_code=500)

    async def update_entity(
        self,
        entity_id: str,
        request: InternalEntityUpdateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update an existing entity with transaction rollback (deprecated - use specialized methods)."""
        # Check entity exists (404 if not)
        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        # Check deletion status (410 if deleted)
        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        # Check lock status (423 if locked)
        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        # Create transaction
        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            # Get head revision
            head_revision_id = tx.state.vitess_client.get_head(entity_id)
            # Prepare data
            request_data = PreparedRequestData(**request.data.copy())
            request_data["id"] = entity_id
            # Process statements
            hash_result = tx.process_statements(entity_id, request_data, validator)
            # Create revision
            response = await tx.create_revision(
                entity_id=entity_id,
                request_data=request_data,
                entity_type=EntityType(request.type),
                edit_headers=edit_headers,
                hash_result=hash_result,
            )
            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type=ChangeType.EDIT,
                edit_headers=edit_headers,
                from_revision_id=head_revision_id,
                changed_at=None,
            )
            # Log activity
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

            # Commit
            tx.commit()
            return response
        except Exception as e:
            logger.error(f"Entity update failed for {entity_id}: {e}", exc_info=True)
            logger.error(f"Entity update failed - full details: {type(e).__name__}: {str(e)}")
            logger.error(f"Entity update failed - traceback:", exc_info=True)
            tx.rollback()
            raise_validation_error(f"Update failed: {type(e).__name__}: {str(e)}", status_code=500)

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
        # Check entity exists (404 if not)
        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        # Check deletion status (410 if deleted)
        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        # Check lock status (423 if locked)
        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        # Create transaction
        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            # Get head revision
            head_revision_id = tx.state.vitess_client.get_head(entity_id)

            # Prepare data from modified entity data
            request_data = PreparedRequestData(**modified_data.copy())
            request_data["id"] = entity_id

            # Process statements
            hash_result = tx.process_statements(entity_id, request_data, validator)

            # Create revision
            response = await tx.create_revision(
                entity_id=entity_id,
                request_data=request_data,
                entity_type=entity_type,
                edit_headers=edit_headers,
                hash_result=hash_result,
            )

            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type=ChangeType.EDIT,
                edit_headers=edit_headers,
                from_revision_id=head_revision_id,
                changed_at=None,
            )

            # Log activity
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
                    logger.warning(f"Failed to log user activity: {activity_result.error}")

            # Commit
            tx.commit()
            return response
        except Exception as e:
            logger.error(f"Entity update failed for {entity_id}: {e}", exc_info=True)
            tx.rollback()
            raise_validation_error(f"Update failed: {type(e).__name__}: {str(e)}", status_code=500)

    async def update_label(
        self,
        entity_id: str,
        language_code: str,
        language: str,
        value: str,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update or add a label for a language."""
        logger.debug(f"Updating label for {entity_id} in {language_code}")
        # Validate language codes match
        if language != language_code:
            raise_validation_error(
                f"Language in request ({language}) does not match path parameter ({language_code})",
                status_code=400
            )

        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Update label
        if "labels" not in current_entity.entity_data:
            current_entity.entity_data["labels"] = {}
        current_entity.entity_data["labels"][language_code] = {
            "language": language_code,
            "value": value,
        }

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            current_entity.entity_data,
            entity_type,
            edit_headers,
            validator,
        )

    async def delete_label(
        self,
        entity_id: str,
        language_code: str,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Delete a label for a language (idempotent)."""
        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Check if label exists
        labels = current_entity.entity_data.get("labels", {})
        if language_code not in labels:
            # Idempotent - return current entity if label doesn't exist
            return current_entity

        # Remove label
        del current_entity.entity_data["labels"][language_code]

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            current_entity.entity_data,
            entity_type,
            edit_headers,
            validator,
        )

    async def update_description(
        self,
        entity_id: str,
        language_code: str,
        language: str,
        description: str,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update or add a description for a language."""
        logger.debug(f"Updating description for {entity_id} in {language_code}")
        # Validate language codes match
        if language != language_code:
            raise_validation_error(
                f"Language in request ({language}) does not match path parameter ({language_code})",
                status_code=400
            )

        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Update description
        if "descriptions" not in current_entity.entity_data:
            current_entity.entity_data["descriptions"] = {}
        current_entity.entity_data["descriptions"][language_code] = {
            "language": language_code,
            "value": description,
        }

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            current_entity.entity_data,
            entity_type,
            edit_headers,
            validator,
        )

    async def delete_description(
        self,
        entity_id: str,
        language_code: str,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Delete a description for a language (idempotent)."""
        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Check if description exists
        descriptions = current_entity.entity_data.get("descriptions", {})
        if language_code not in descriptions:
            # Idempotent - return current entity if description doesn't exist
            return current_entity

        # Remove description
        del current_entity.entity_data["descriptions"][language_code]

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            current_entity.entity_data,
            entity_type,
            edit_headers,
            validator,
        )

    async def update_aliases(
        self,
        entity_id: str,
        language_code: str,
        aliases: list[str],
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Replace all aliases for a language."""
        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Update aliases: convert list of strings to internal format
        if "aliases" not in current_entity.entity_data:
            current_entity.entity_data["aliases"] = {}
        current_entity.entity_data["aliases"][language_code] = [
            {"value": alias} for alias in aliases
        ]

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            current_entity.entity_data,
            entity_type,
            edit_headers,
            validator,
        )

    async def update_sitelink(
        self,
        entity_id: str,
        site: str,
        title: str,
        badges: list[str],
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update or add a sitelink.

        Returns EntityResponse (not OperationResult) for consistency with other methods.
        """
        logger.debug(f"Updating sitelink {site} for {entity_id}")
        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Check if sitelink already exists
        sitelinks = current_entity.entity_data.get("sitelinks", {})
        if site in sitelinks:
            # PUT operation: allow updating existing
            pass

        # Update sitelink
        if "sitelinks" not in current_entity.entity_data:
            current_entity.entity_data["sitelinks"] = {}
        current_entity.entity_data["sitelinks"][site] = {
            "title": title,
            "badges": badges,
        }

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            current_entity.entity_data,
            entity_type,
            edit_headers,
            validator,
        )

    async def delete_sitelink(
        self,
        entity_id: str,
        site: str,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Delete a sitelink (idempotent).

        Returns EntityResponse (not OperationResult) for consistency.
        """
        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Check if sitelink exists
        sitelinks = current_entity.entity_data.get("sitelinks", {})
        if site not in sitelinks:
            # Idempotent - return current entity if sitelink doesn't exist
            return current_entity

        # Remove sitelink
        del current_entity.entity_data["sitelinks"][site]

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            current_entity.entity_data,
            entity_type,
            edit_headers,
            validator,
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

    async def update_lexeme(
        self,
        entity_id: str,
        request: InternalEntityUpdateRequest,
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

        # Validate entity type (must be lexeme)
        if not re.match(r"^L\d+$", entity_id):
            raise_validation_error(
                "Entity ID must be a lexeme (format: L followed by digits)",
                status_code=400,
            )

        # Check entity exists (404 if not)
        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        # Check deletion status (410 if deleted)
        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        # Check lock status (423 if locked)
        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        # Create transaction
        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id

        try:
            # Get head revision
            head_revision_id = tx.state.vitess_client.get_head(entity_id)

            # Prepare data from request
            request_data = PreparedRequestData(**request.data.copy())
            request_data["id"] = entity_id

            # Process lexeme terms within transaction (S3 operations)
            forms = request.data.get("forms", [])
            senses = request.data.get("senses", [])
            tx.process_lexeme_terms(forms, senses)

            # Update request_data with hashes from S3 storage
            request_data["forms"] = forms
            request_data["senses"] = senses

            # Process statements
            hash_result = tx.process_statements(entity_id, request_data, validator)

            # Create revision
            response = await tx.create_revision(
                entity_id=entity_id,
                request_data=request_data,
                entity_type=EntityType(request.type),
                edit_headers=edit_headers,
                hash_result=hash_result,
            )

            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=response.revision_id,
                change_type=ChangeType.EDIT,
                edit_headers=edit_headers,
                from_revision_id=head_revision_id,
                changed_at=None,
            )

            # Log activity
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
                    logger.warning(f"Failed to log user activity: {activity_result.error}")

            # Commit
            tx.commit()
            return response
        except Exception as e:
            logger.error(f"Lexeme update failed for {entity_id}: {e}", exc_info=True)
            tx.rollback()
            raise_validation_error(f"Update failed: {type(e).__name__}: {str(e)}", status_code=500)
