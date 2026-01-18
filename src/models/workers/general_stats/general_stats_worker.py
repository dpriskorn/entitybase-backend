"""General statistics worker for computing daily analytics."""

import logging
from datetime import date, datetime

from models.config.settings import settings
from models.rest_api.entitybase.services.general_stats_service import (
    GeneralStatsService,
)
from models.workers.base_stats_worker import BaseStatsWorker

logger = logging.getLogger(__name__)


class GeneralStatsWorker(BaseStatsWorker):

    def get_enabled_setting(self) -> bool:
        """Check if general stats are enabled."""
        return settings.general_stats_enabled

    def get_schedule_setting(self) -> str:
        """Get the schedule for general stats."""
        return settings.general_stats_schedule

    async def run_daily_computation(self) -> None:
        """Run daily statistics computation and storage."""
        try:
            if not self.vitess_client:
                logger.error("Vitess client not initialized")
                return

            logger.info("Starting daily general statistics computation")

            # Compute statistics
            service = GeneralStatsService()
            stats = service.compute_daily_stats(self.vitess_client)

            # Store in database
            await self._store_statistics(stats)

            self.last_run = datetime.utcnow()
            logger.info(
                f"Completed general statistics computation: {stats.total_statements} statements, "
                f"{stats.total_items} items, {stats.total_terms} terms"
            )

        except Exception as e:
            logger.error(f"Failed to compute general statistics: {e}")
            raise

    async def _store_statistics(self, stats) -> None:
        """Store computed statistics in database via repository."""
        if not self.vitess_client:
            return

        today = date.today().isoformat()

        with self.vitess_client.connection_manager.get_connection() as conn:
            self.vitess_client.user_repository.insert_general_statistics(
                conn=conn,
                date=today,
                total_statements=stats.total_statements,
                total_qualifiers=stats.total_qualifiers,
                total_references=stats.total_references,
                total_items=stats.total_items,
                total_lexemes=stats.total_lexemes,
                total_properties=stats.total_properties,
                total_sitelinks=stats.total_sitelinks,
                total_terms=stats.total_terms,
                terms_per_language=stats.terms_per_language,
                terms_by_type=stats.terms_by_type,
            )
            conn.commit()