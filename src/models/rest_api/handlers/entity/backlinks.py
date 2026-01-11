"""Handler for entity backlinks operations."""

from fastapi import HTTPException
from pydantic import BaseModel

from models.infrastructure.vitess_client import VitessClient
from models.rest_api.response import BacklinksResponse, Backlink


class BacklinkHandler(BaseModel):
    """Handler for entity backlink operations."""

    async def get(
        self,
        entity_id: str,
        vitess_client: VitessClient,
        limit: int = 100,
        offset: int = 0,
    ) -> BacklinksResponse:
        """Get backlinks for an entity."""
        with vitess_client.connection_manager.get_connection() as conn:
            internal_id = vitess_client.id_resolver.resolve_id(conn, entity_id)
            if not internal_id:
                raise HTTPException(status_code=404, detail="Entity not found")

            backlinks = vitess_client.get_backlinks(internal_id, limit, offset)

            backlink_models = []
            for b in backlinks:
                referencing_entity_id = vitess_client.id_resolver.resolve_entity_id(
                    conn, b.referencing_internal_id
                )
                if referencing_entity_id:
                    backlink_models.append(
                        Backlink(
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
