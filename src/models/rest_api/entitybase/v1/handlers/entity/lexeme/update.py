"""Handler for lexeme update operations in the REST API (deprecated - use EntityUpdateHandler instead)."""

import logging
from models.common import EditHeaders
from models.data.rest_api.v1.entitybase.request import LexemeUpdateRequest
from models.data.rest_api.v1.entitybase.request.entity.crud import EntityUpdateRequest
from models.rest_api.utils import raise_validation_error
from ..update import EntityUpdateHandler

logger = logging.getLogger(__name__)


class LexemeUpdateHandler(EntityUpdateHandler):
    """Deprecated: Use EntityUpdateHandler.update_lexeme instead."""

    async def update_entity(
        self,
        entity_id: str,
        request: LexemeUpdateRequest | EntityUpdateRequest,
        edit_headers: EditHeaders,
        validator: Any | None,
    ) -> None:
        """Deprecated method - delegates to EntityUpdateHandler.update_lexeme."""
        logger.warning("LexemeUpdateHandler.update_entity is deprecated, use EntityUpdateHandler.update_lexeme")

        # Convert LexemeUpdateRequest to internal EntityUpdateRequest if needed
        if isinstance(request, LexemeUpdateRequest):
            internal_request = EntityUpdateRequest(
                id=request.id,
                type=request.type,
                labels=request.labels,
                descriptions=request.descriptions,
                claims=request.claims,
                aliases=request.aliases,
                sitelinks=request.sitelinks,
                forms=request.forms,
                senses=request.senses,
                is_mass_edit=request.is_mass_edit,
                state=request.state,
                edit_type=request.edit_type,
                is_not_autoconfirmed_user=request.is_not_autoconfirmed_user,
                is_semi_protected=request.is_semi_protected,
                is_locked=request.is_locked,
                is_archived=request.is_archived,
                is_dangling=request.is_dangling,
                is_mass_edit_protected=request.is_mass_edit_protected,
            )
        else:
            internal_request = request

        return await self.update_lexeme(entity_id, internal_request, edit_headers, validator)
