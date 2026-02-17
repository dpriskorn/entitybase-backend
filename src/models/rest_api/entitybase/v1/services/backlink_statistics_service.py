"""Service for computing backlink statistics."""

import logging

from pydantic import Field

from models.data.rest_api.v1.entitybase.response import (
    TopEntityByBacklinks,
    BacklinkStatisticsData,
)
from models.rest_api.entitybase.v1.service import Service

logger = logging.getLogger(__name__)


class BacklinkStatisticsService(Service):
    """Service for computing backlink statistics."""

    top_limit: int = Field(default=100, description="Number of top entities to include")

    def compute_daily_stats(self) -> BacklinkStatisticsData:
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
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM entity_backlinks")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_entities_with_backlinks(self) -> int:
        """Count entities that have incoming backlinks."""
        cursor = self.state.vitess_client.cursor
        cursor.execute(
            "SELECT COUNT(DISTINCT referenced_internal_id) FROM entity_backlinks"
        )
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_top_entities_by_backlinks(
        self, limit: int = 0
    ) -> list[TopEntityByBacklinks]:
        """Get top entities ranked by backlink count."""
        if not limit:
            limit = self.top_limit
        logger.debug("Getting top %d entities by backlinks", limit)
        cursor = self.state.vitess_client.cursor
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
            entity_id = self.state.vitess_client.id_resolver.resolve_entity_id(
                internal_id
            )
            if entity_id:
                results.append(
                    TopEntityByBacklinks(
                        entity_id=entity_id,
                        backlink_count=backlink_count,
                    )
                )

        return results
