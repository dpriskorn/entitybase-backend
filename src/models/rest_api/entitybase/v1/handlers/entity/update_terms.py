"""Entity update term mixins."""

import logging
from typing import Any

from pydantic import BaseModel

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    TermUpdateContext,
    EventPublishContext,
)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.infrastructure.s3.enums import EntityType
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


def _infer_entity_type_from_id(entity_id: str) -> EntityType | None:
    """Infer entity type from ID format."""
    import re

    if re.match(r"^Q\d+$", entity_id):
        return EntityType.ITEM
    elif re.match(r"^P\d+$", entity_id):
        return EntityType.PROPERTY
    elif re.match(r"^L\d+$", entity_id):
        return EntityType.LEXEME
    return None


class EntityUpdateTermsMixin(BaseModel):
    """Mixin for entity term update operations (labels, descriptions, aliases)."""

    model_config = {"extra": "allow"}

    state: Any
    _update_with_transaction: Any

    async def update_label(
        self,
        entity_id: str,
        context: TermUpdateContext,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update or add a label for a language."""
        logger.debug(f"Updating label for {entity_id} in {context.language_code}")
        if context.language != context.language_code:
            raise_validation_error(
                f"Language in request ({context.language}) does not match path parameter ({context.language_code})",
                status_code=400,
            )

        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        entity_dict = current_entity.entity_data.revision

        if "labels" not in entity_dict:
            entity_dict["labels"] = {}
        entity_dict["labels"][context.language_code] = {
            "language": context.language_code,
            "value": context.value,
        }

        return await self._update_with_transaction(  # type: ignore[no-any-return]
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
        from .update_transaction import UpdateTransaction

        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        existing_hashes = current_entity.entity_data.revision.get("hashes", {})
        labels_hashes = existing_hashes.get("labels", {})
        if language_code not in labels_hashes:
            return current_entity

        updated_labels_hashes = dict(labels_hashes)
        del updated_labels_hashes[language_code]

        updated_hashes = dict(existing_hashes)
        updated_hashes["labels"] = updated_labels_hashes

        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            head_revision_id = tx.state.vitess_client.get_head(entity_id)

            response = await tx.create_revision_with_hashes(
                entity_id=entity_id,
                entity_type=entity_type,
                edit_headers=edit_headers,
                existing_hashes=updated_hashes,
                existing_revision=current_entity.entity_data.revision,
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
        except Exception as e:
            logger.error(f"Delete label failed for {entity_id}: {e}", exc_info=True)
            tx.rollback()
            raise_validation_error(
                f"Delete label failed: {type(e).__name__}: {str(e)}", status_code=500
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
        if context.language != context.language_code:
            raise_validation_error(
                f"Language in request ({context.language}) does not match path parameter ({context.language_code})",
                status_code=400,
            )

        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        entity_dict = current_entity.entity_data.revision

        if "descriptions" not in entity_dict:
            entity_dict["descriptions"] = {}
        entity_dict["descriptions"][context.language_code] = {
            "language": context.language_code,
            "value": context.value,
        }

        return await self._update_with_transaction(  # type: ignore[no-any-return]
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
        from .update_transaction import UpdateTransaction

        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        existing_hashes = current_entity.entity_data.revision.get("hashes", {})
        descriptions_hashes = existing_hashes.get("descriptions", {})
        if language_code not in descriptions_hashes:
            return current_entity

        updated_descriptions_hashes = dict(descriptions_hashes)
        del updated_descriptions_hashes[language_code]

        updated_hashes = dict(existing_hashes)
        updated_hashes["descriptions"] = updated_descriptions_hashes

        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            head_revision_id = tx.state.vitess_client.get_head(entity_id)

            response = await tx.create_revision_with_hashes(
                entity_id=entity_id,
                entity_type=entity_type,
                edit_headers=edit_headers,
                existing_hashes=updated_hashes,
                existing_revision=current_entity.entity_data.revision,
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
        except Exception as e:
            logger.error(
                f"Delete description failed for {entity_id}: {e}", exc_info=True
            )
            tx.rollback()
            raise_validation_error(
                f"Delete description failed: {type(e).__name__}: {str(e)}",
                status_code=500,
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
        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        entity_dict = current_entity.entity_data.revision

        if "aliases" not in entity_dict:
            entity_dict["aliases"] = {}
        entity_dict["aliases"][language_code] = [{"value": alias} for alias in aliases]

        return await self._update_with_transaction(  # type: ignore[no-any-return]
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
        """Add a single alias to the existing list for a language.

        Uses hash-direct approach:
        1. Hash the new alias
        2. Check against existing alias hashes (no S3 read needed)
        3. Store the new alias in S3/Vitess
        4. Create new revision with updated hash list
        """
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.infrastructure.vitess.repositories.terms import TermsRepository
        from .update_transaction import UpdateTransaction

        logger.debug(
            f"Adding alias '{alias}' for entity {entity_id}, language {language_code}"
        )

        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        existing_hashes = current_entity.entity_data.revision.get("hashes", {})
        aliases_hashes = existing_hashes.get("aliases", {})
        existing_alias_hashes = list(aliases_hashes.get(language_code, []))

        new_alias_hash = MetadataExtractor.hash_string(alias)
        if new_alias_hash in existing_alias_hashes:
            raise_validation_error(
                f"Alias '{alias}' already exists for language {language_code}",
                status_code=409,
            )

        self.state.s3_client.store_term_metadata(alias, new_alias_hash)
        if self.state.vitess_config:
            terms_repo = TermsRepository(vitess_client=self.state.vitess_client)
            terms_repo.insert_term(new_alias_hash, alias, "alias")

        updated_alias_hashes = existing_alias_hashes + [new_alias_hash]
        updated_aliases_hashes = dict(aliases_hashes)
        updated_aliases_hashes[language_code] = updated_alias_hashes

        updated_hashes = dict(existing_hashes)
        updated_hashes["aliases"] = updated_aliases_hashes

        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            head_revision_id = tx.state.vitess_client.get_head(entity_id)

            response = await tx.create_revision_with_hashes(
                entity_id=entity_id,
                entity_type=entity_type,
                edit_headers=edit_headers,
                existing_hashes=updated_hashes,
                existing_revision=current_entity.entity_data.revision,
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
        except Exception as e:
            logger.error(f"Add alias failed for {entity_id}: {e}", exc_info=True)
            tx.rollback()
            raise_validation_error(
                f"Add alias failed: {type(e).__name__}: {str(e)}", status_code=500
            )

    async def delete_aliases(
        self,
        entity_id: str,
        language_code: str,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Delete all aliases for a language (idempotent)."""
        from .update_transaction import UpdateTransaction

        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        if self.state.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity deleted", status_code=410)

        if self.state.vitess_client.is_entity_locked(entity_id):
            raise_validation_error("Entity locked", status_code=423)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        existing_hashes = current_entity.entity_data.revision.get("hashes", {})
        aliases_hashes = existing_hashes.get("aliases", {})
        if language_code not in aliases_hashes:
            return current_entity

        updated_aliases_hashes = dict(aliases_hashes)
        del updated_aliases_hashes[language_code]

        updated_hashes = dict(existing_hashes)
        updated_hashes["aliases"] = updated_aliases_hashes

        tx = UpdateTransaction(state=self.state)
        tx.entity_id = entity_id
        try:
            head_revision_id = tx.state.vitess_client.get_head(entity_id)

            response = await tx.create_revision_with_hashes(
                entity_id=entity_id,
                entity_type=entity_type,
                edit_headers=edit_headers,
                existing_hashes=updated_hashes,
                existing_revision=current_entity.entity_data.revision,
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
        except Exception as e:
            logger.error(f"Delete aliases failed for {entity_id}: {e}", exc_info=True)
            tx.rollback()
            raise_validation_error(
                f"Delete aliases failed: {type(e).__name__}: {str(e)}", status_code=500
            )
