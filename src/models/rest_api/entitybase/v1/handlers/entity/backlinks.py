"""Handler for entity backlinks operations."""

import logging

from fastapi import HTTPException

from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.response import BacklinksResponse
from models.data.rest_api.v1.entitybase.response import BacklinkResponse

logger = logging.getLogger(__name__)


class BacklinkHandler(Handler):
    """Handler for entity backlink operations."""

    async def get(
        self,
        entity_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> BacklinksResponse:
        """Get backlinks for an entity."""
        logger.debug(f"Getting backlinks for entity {entity_id}, limit {limit}")
        logger.debug(f"Resolving entity_id: {entity_id}")
        internal_id = self.state.vitess_client.id_resolver.resolve_id(entity_id)
        logger.debug(f"Resolved internal_id: {internal_id}")
        if not internal_id:
            raise HTTPException(status_code=404, detail="Entity not found")

        logger.debug(
            f"Calling get_backlinks with internal_id={internal_id}, limit={limit}, offset={offset}"
        )
        backlinks = self.state.vitess_client.get_backlinks(internal_id, limit, offset)
        logger.debug(f"Got {len(backlinks)} backlinks")

        backlink_models = []
        for b in backlinks:
            referencing_entity_id = (
                self.state.vitess_client.id_resolver.resolve_entity_id(
                    b.referencing_internal_id
                )
            )
            if referencing_entity_id:
                backlink_models.append(
                    BacklinkResponse(
                        entity_id=referencing_entity_id,
                        property_id=b.property_id,
                        rank=b.rank,
                    )
                )

        return BacklinksResponse(
            backlinks=backlink_models,
            limit=limit,
            offset=offset,
        )
