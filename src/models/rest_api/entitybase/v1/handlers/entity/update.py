"""Entity update handlers."""

import logging
import re
from typing import Any

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.enums import EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import (
    LexemeUpdateRequest,
    UserActivityType,
)
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    TermUpdateContext,
    EventPublishContext,
    SitelinkUpdateContext,
)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.utils import raise_validation_error
from .handler import EntityHandler
from .update_transaction import UpdateTransaction

logger = logging.getLogger(__name__)


class EntityUpdateHandler(EntityHandler):
    """Handler for entity update operations"""

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
            modified_data["id"] = entity_id
            request_data = PreparedRequestData(**modified_data)

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

    async def update_label(
        self,
        entity_id: str,
        context: TermUpdateContext,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update or add a label for a language."""
        logger.debug(f"Updating label for {entity_id} in {context.language_code}")
        # Validate language codes match
        if context.language != context.language_code:
            raise_validation_error(
                f"Language in request ({context.language}) does not match path parameter ({context.language_code})",
                status_code=400,
            )

        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Get the revision data dictionary
        entity_dict = current_entity.entity_data.revision

        # Update label
        if "labels" not in entity_dict:
            entity_dict["labels"] = {}
        entity_dict["labels"][context.language_code] = {
            "language": context.language_code,
            "value": context.value,
        }

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            entity_dict,
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

        # Get the revision data dictionary
        entity_dict = current_entity.entity_data.revision

        # Check if label exists
        labels = entity_dict.get("labels", {})
        if language_code not in labels:
            # Idempotent - return current entity if label doesn't exist
            return current_entity

        # Remove label
        del entity_dict["labels"][language_code]

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            entity_dict,
            entity_type,
            edit_headers,
            validator,
        )

    async def update_description(
        self,
        entity_id: str,
        context: TermUpdateContext,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update or add a description for a language."""
        logger.debug(f"Updating description for {entity_id} in {context.language_code}")
        # Validate language codes match
        if context.language != context.language_code:
            raise_validation_error(
                f"Language in request ({context.language}) does not match path parameter ({context.language_code})",
                status_code=400,
            )

        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        # Get the revision data dictionary
        entity_dict = current_entity.entity_data.revision

        # Update description
        if "descriptions" not in entity_dict:
            entity_dict["descriptions"] = {}
        entity_dict["descriptions"][context.language_code] = {
            "language": context.language_code,
            "value": context.value,
        }

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            entity_dict,
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

        # Get the revision data dictionary
        entity_dict = current_entity.entity_data.revision

        # Check if description exists
        descriptions = entity_dict.get("descriptions", {})
        if language_code not in descriptions:
            # Idempotent - return current entity if description doesn't exist
            return current_entity

        # Remove description
        del entity_dict["descriptions"][language_code]

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            entity_dict,
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
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        entity_dict = current_entity.entity_data.revision

        if "aliases" not in entity_dict:
            entity_dict["aliases"] = {}
        entity_dict["aliases"][language_code] = [{"value": alias} for alias in aliases]

        return await self._update_with_transaction(
            entity_id,
            entity_dict,
            entity_type,
            edit_headers,
            validator,
        )

    async def add_alias(
        self,
        entity_id: str,
        language_code: str,
        alias: str,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Add a single alias to the existing list for a language."""
        entity_type = self._infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        entity_dict = current_entity.entity_data.revision

        if "aliases" not in entity_dict:
            entity_dict["aliases"] = {}
        
        existing_aliases = entity_dict["aliases"].get(language_code, [])
        existing_values = [a.get("value", a) if isinstance(a, dict) else a for a in existing_aliases]
        
        if alias in existing_values:
            raise_validation_error(
                f"Alias '{alias}' already exists for language {language_code}",
                status_code=409,
            )
        
        existing_aliases.append({"value": alias})
        entity_dict["aliases"][language_code] = existing_aliases

        return await self._update_with_transaction(
            entity_id,
            entity_dict,
            entity_type,
            edit_headers,
            validator,
        )

    async def update_sitelink(
        self,
        ctx: SitelinkUpdateContext,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update or add a sitelink.

        Returns EntityResponse (not OperationResult) for consistency with other methods.
        """
        logger.debug(f"Updating sitelink {ctx.site} for {ctx.entity_id}")
        # Validate entity ID format
        entity_type = self._infer_entity_type_from_id(ctx.entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        # Fetch current entity
        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(ctx.entity_id)

        # Get the revision data dictionary
        entity_dict = current_entity.entity_data.revision

        # Check if sitelink already exists
        sitelinks = entity_dict.get("sitelinks", {})
        if ctx.site in sitelinks:
            # PUT operation: allow updating existing
            pass

        # Update sitelink
        if "sitelinks" not in entity_dict:
            entity_dict["sitelinks"] = {}
        entity_dict["sitelinks"][ctx.site] = {
            "title": ctx.title,
            "badges": ctx.badges,
        }

        # Update with transaction
        return await self._update_with_transaction(
            ctx.entity_id,
            entity_dict,
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

        # Get the revision data dictionary
        entity_dict = current_entity.entity_data.revision

        # Check if sitelink exists
        sitelinks = entity_dict.get("sitelinks", {})
        if site not in sitelinks:
            # Idempotent - return current entity if sitelink doesn't exist
            return current_entity

        # Remove sitelink
        del entity_dict["sitelinks"][site]

        # Update with transaction
        return await self._update_with_transaction(
            entity_id,
            entity_dict,
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
            data = request.data.copy()
            data["id"] = entity_id

            # Process lexeme terms within transaction (S3 operations)
            forms = data.get("forms", [])
            senses = data.get("senses", [])
            lemmas = data.get("lemmas", {})
            tx.process_lexeme_terms(forms, senses, lemmas)

            # Update data with hashes from S3 storage
            data["forms"] = forms
            data["senses"] = senses
            request_data = PreparedRequestData(**data)

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
