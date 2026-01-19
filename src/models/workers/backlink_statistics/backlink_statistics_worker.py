"""Backlink statistics worker for computing daily analytics."""

import logging
from datetime import date, datetime, timezone
from typing import Any

from models.config.settings import settings
from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
    BacklinkStatisticsService,
)
from models.workers.base_stats_worker import BaseStatsWorker

logger = logging.getLogger(__name__)


class BacklinkStatisticsWorker(BaseStatsWorker):
    def get_enabled_setting(self) -> bool:
        """Check if backlink stats are enabled."""
        return settings.backlink_stats_enabled

    def get_schedule_setting(self) -> str:
        """Get the schedule for backlink stats."""
        return settings.backlink_stats_schedule

    async def run_daily_computation(self) -> None:
        """Run daily statistics computation and storage."""
        try:
            if not self.vitess_client:
                logger.error("Vitess client not initialized")
                return

            logger.info("Starting daily backlink statistics computation")

            # Compute statistics
            service = BacklinkStatisticsService(
                top_limit=settings.backlink_stats_top_limit
            )
            stats = service.compute_daily_stats(self.vitess_client)

            # Store in database
            await self._store_statistics(stats)

            self.last_run = datetime.now(timezone.utc)
            logger.info(
                f"Completed backlink statistics computation: {stats.total_backlinks} backlinks, "
                f"{stats.unique_entities_with_backlinks} entities with backlinks"
            )

        except Exception as e:
            logger.error(f"Failed to compute backlink statistics: {e}")
            raise

    async def _store_statistics(self, stats: Any) -> None:
        """Store computed statistics in database via repository."""
        if not self.vitess_client:
            return

        today = date.today().isoformat()

        with self.vitess_client.connection_manager.get_connection() as conn:
            self.vitess_client.backlink_repository.insert_backlink_statistics(
                conn=conn,
                date=today,
                total_backlinks=stats.total_backlinks,
                unique_entities_with_backlinks=stats.unique_entities_with_backlinks,
                top_entities_by_backlinks=stats.top_entities_by_backlinks,
            )
            conn.commit()
