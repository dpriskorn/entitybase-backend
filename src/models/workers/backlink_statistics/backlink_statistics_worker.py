"""Backlink statistics worker for computing daily analytics."""

import asyncio
import logging
import os
from datetime import datetime, date
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

        # Run initial computation
        await self.run_daily_computation()

        # Schedule daily runs
        while self.running:
            try:
                # Wait until next day (simplified - in production use proper scheduler)
                await asyncio.sleep(86400)  # 24 hours
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
