"""Entity update sitelink mixins."""

import logging
import re
from typing import Any

from pydantic import BaseModel

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request.entity.context import (
    SitelinkUpdateContext,
)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.infrastructure.s3.enums import EntityType
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


def _infer_entity_type_from_id(entity_id: str) -> EntityType | None:
    """Infer entity type from ID format."""
    if re.match(r"^Q\d+$", entity_id):
        return EntityType.ITEM
    elif re.match(r"^P\d+$", entity_id):
        return EntityType.PROPERTY
    elif re.match(r"^L\d+$", entity_id):
        return EntityType.LEXEME
    return None


class EntityUpdateSitelinksMixin(BaseModel):
    """Mixin for entity sitelink update operations."""

    model_config = {"extra": "allow"}

    state: Any
    _update_with_transaction: Any

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
        entity_type = _infer_entity_type_from_id(ctx.entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(ctx.entity_id)

        entity_dict = current_entity.entity_data.revision

        sitelinks = entity_dict.get("sitelinks", {})
        if ctx.site in sitelinks:
            pass

        if "sitelinks" not in entity_dict:
            entity_dict["sitelinks"] = {}
        entity_dict["sitelinks"][ctx.site] = {
            "title": ctx.title,
            "badges": ctx.badges,
        }

        return await self._update_with_transaction(  # type: ignore[no-any-return]
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
        entity_type = _infer_entity_type_from_id(entity_id)
        if not entity_type:
            raise_validation_error("Invalid entity ID format", status_code=400)

        read_handler = EntityReadHandler(state=self.state)
        current_entity = read_handler.get_entity(entity_id)

        entity_dict = current_entity.entity_data.revision

        sitelinks = entity_dict.get("sitelinks", {})
        if site not in sitelinks:
            return current_entity

        del entity_dict["sitelinks"][site]

        return await self._update_with_transaction(  # type: ignore[no-any-return]
            entity_id,
            entity_dict,
            entity_type,
            edit_headers,
            validator,
        )
