"""User statistics worker for computing daily analytics."""

import logging
from datetime import date, datetime, timezone

from models.config.settings import settings
from models.rest_api.v1.entitybase.services.user_stats_service import (
    UserStatsData,
    UserStatsService,
)
from models.workers.base_stats_worker import BaseStatsWorker

logger = logging.getLogger(__name__)


class UserStatsWorker(BaseStatsWorker):
    def get_enabled_setting(self) -> bool:
        """Check if user stats are enabled."""
        return settings.user_stats_enabled

    def get_schedule_setting(self) -> str:
        """Get the schedule for user stats."""
        return settings.user_stats_schedule

    async def run_daily_computation(self) -> None:
        """Run daily statistics computation and storage."""
        try:
            if not self.vitess_client:
                logger.error("Vitess client not initialized")
                return

            logger.info("Starting daily user statistics computation")

            # Compute statistics
            service = UserStatsService()
            stats = service.compute_daily_stats(self.vitess_client)

            # Store in database
            await self._store_statistics(stats)

            self.last_run = datetime.now(timezone.utc)
            logger.info(
                f"Completed user statistics computation: {stats.total_users} users, "
                f"{stats.active_users} active"
            )

        except Exception as e:
            logger.error(f"Failed to compute user statistics: {e}")
            raise

    async def _store_statistics(self, stats: UserStatsData) -> None:
        """Store computed statistics in database via repository."""
        if not self.vitess_client:
            return

        today = date.today().isoformat()

        with self.vitess_client.connection_manager.get_connection() as conn:
            self.vitess_client.user_repository.insert_user_statistics(
                conn=conn,
                date=today,
                total_users=stats.total_users,
                active_users=stats.active_users,
            )
            conn.commit()
