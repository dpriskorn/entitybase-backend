"""Service for computing backlink statistics."""

import logging

from pydantic import BaseModel, Field

from models.rest_api.entitybase.v1.response.misc import (
    BacklinkStatisticsData,
    TopEntityByBacklinks,
)

logger = logging.getLogger(__name__)


class BacklinkStatisticsService(BaseModel):
    """Service for computing backlink statistics."""

    top_limit: int = Field(default=100, description="Number of top entities to include")

    def compute_daily_stats(
        self
    ) -> BacklinkStatisticsData:
        """Compute comprehensive backlink statistics for current date."""
        total_backlinks = self.get_total_backlinks()
        unique_entities = self.get_entities_with_backlinks()
        top_entities = self.get_top_entities_by_backlinks(self.top_limit)

        return BacklinkStatisticsData(
            total=total_backlinks,
            unique=unique_entities,
            top=top_entities,
        )

    def get_total_backlinks(self) -> int:
        """Count total backlink relationships."""
        with self.state.vitess_client.connection_manager.get_connection() as conn:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM entity_backlinks")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_entities_with_backlinks(self) -> int:
        """Count entities that have incoming backlinks."""
        with self.state.vitess_client.connection_manager.get_connection() as conn:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(DISTINCT referenced_internal_id) FROM entity_backlinks"
                )
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_top_entities_by_backlinks(
        self, limit: int = 100
    ) -> list[TopEntityByBacklinks]:
        """Get top entities ranked by backlink count."""
        logger.debug("Getting top %d entities by backlinks", limit)
        with self.state.vitess_client.connection_manager.get_connection() as conn:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        referenced_internal_id,
                        COUNT(*) as backlink_count
                    FROM entity_backlinks
                    GROUP BY referenced_internal_id
                    ORDER BY backlink_count DESC
                    LIMIT %s
                    """,
                    (limit,),
                )

                results = []
                for row in cursor.fetchall():
                    internal_id = row[0]
                    backlink_count = row[1]

                    # Resolve entity ID
                    entity_id = self.state.vitess_client.id_resolver.resolve_entity_id(internal_id)
                    if entity_id:
                        results.append(
                            TopEntityByBacklinks(
                                entity_id=entity_id,
                                backlink_count=backlink_count,
                            )
                        )

                return results
