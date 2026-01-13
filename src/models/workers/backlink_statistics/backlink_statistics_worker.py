"""Backlink statistics worker for computing daily analytics."""

import asyncio
import logging
import os
from datetime import datetime, date, time, timedelta
from typing import Any

from pydantic import BaseModel, Field

from models.config.settings import settings
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.response.health import WorkerHealthCheck
from models.rest_api.services.backlink_statistics_service import (
    BacklinkStatisticsService,
)

logger = logging.getLogger(__name__)


class BacklinkStatisticsWorker(BaseModel):
    """Background worker for computing backlink statistics."""

    worker_id: str = Field(
        default_factory=lambda: os.getenv("WORKER_ID", f"backlink-stats-{os.getpid()}")
    )
    vitess_client: VitessClient | None = None
    running: bool = Field(default=False)
    last_run: datetime | None = None

    async def start(self) -> None:
        """Start the backlink statistics worker."""
        if not settings.backlink_stats_enabled:
            logger.info("Backlink statistics worker disabled")
            return

        logger.info(f"Starting Backlink Statistics Worker {self.worker_id}")

        # Initialize Vitess client
        vitess_config = settings.to_vitess_config()
        self.vitess_client = VitessClient(config=vitess_config)

        self.running = True

        # Schedule runs according to cron setting
        while self.running:
            try:
                # Calculate seconds until next run
                seconds_until_next = self._calculate_seconds_until_next_run()
                logger.info(f"Next backlink statistics run in {seconds_until_next} seconds")

                await asyncio.sleep(seconds_until_next)
                await self.run_daily_computation()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes

    async def stop(self) -> None:
        """Stop the worker."""
        logger.info(f"Stopping Backlink Statistics Worker {self.worker_id}")
        self.running = False

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

            self.last_run = datetime.utcnow()
            logger.info(
                f"Completed backlink statistics computation: {stats.total_backlinks} backlinks, "
                f"{stats.unique_entities_with_backlinks} entities with backlinks"
            )

        except Exception as e:
            logger.error(f"Failed to compute backlink statistics: {e}")
            raise

    async def _store_statistics(self, stats: Any) -> None:
        """Store computed statistics in database."""
        if not self.vitess_client:
            return

        today = date.today().isoformat()

        with self.vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Insert or update statistics
                cursor.execute(
                    """
                    INSERT INTO backlink_statistics
                    (date, total_backlinks, unique_entities_with_backlinks, top_entities_by_backlinks)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        total_backlinks = VALUES(total_backlinks),
                        unique_entities_with_backlinks = VALUES(unique_entities_with_backlinks),
                        top_entities_by_backlinks = VALUES(top_entities_by_backlinks),
                        created_at = CURRENT_TIMESTAMP
                    """,
                    (
                        today,
                        stats.total_backlinks,
                        stats.unique_entities_with_backlinks,
                        str(stats.top_entities_by_backlinks),  # JSON serialization
                    ),
                )
                conn.commit()

    def _calculate_seconds_until_next_run(self) -> float:
        """Calculate seconds until next scheduled run based on backlink_stats_schedule."""
        # Parse the cron schedule (currently "0 2 * * *" - daily at 2:00 AM)
        schedule_parts = settings.backlink_stats_schedule.split()
        if len(schedule_parts) >= 2:
            minute = int(schedule_parts[0])
            hour = int(schedule_parts[1])
        else:
            # Fallback to 2 AM
            minute, hour = 0, 2

        now = datetime.utcnow()
        target_time = time(hour, minute, 0)

        # Next run is today if not yet passed, otherwise tomorrow
        if now.time() < target_time:
            next_run = datetime.combine(now.date(), target_time)
        else:
            next_run = datetime.combine(now.date() + timedelta(days=1), target_time)

        seconds_until = (next_run - now).total_seconds()
        return max(seconds_until, 0)  # Ensure non-negative

    async def health_check(self) -> WorkerHealthCheck:
        """Health check for the worker."""
        status = "healthy" if self.running else "unhealthy"

        details = {
            "worker_id": self.worker_id,
            "running": self.running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
        }

        return WorkerHealthCheck(
            status=status,
            worker_id=self.worker_id,
            details=details,
        )
