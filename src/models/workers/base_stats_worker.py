"""Base class for statistics workers."""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, time, timedelta, timezone
from typing import Any

from pydantic import Field

from models.config.settings import settings
from models.infrastructure.vitess.client import VitessClient
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.workers.worker import Worker

logger = logging.getLogger(__name__)


class BaseStatsWorker(Worker, ABC):
    """Base class for statistics workers."""

    vitess_client: Any
    worker_id: str = Field(
        default_factory=lambda: os.getenv("WORKER_ID", f"stats-{os.getpid()}")
    )
    running: bool = Field(default=False)
    last_run: datetime | None = None

    @abstractmethod
    async def run_daily_computation(self) -> None:
        """Run daily statistics computation and storage."""
        pass

    async def start(self) -> None:
        """Start the statistics worker."""
        if not self.get_enabled_setting():
            logger.info(f"{self.__class__.__name__} disabled")
            return

        logger.info(f"Starting {self.__class__.__name__} {self.worker_id}")

        # Initialize Vitess client
        vitess_config = settings.get_vitess_config
        self.vitess_client = VitessClient(config=vitess_config)

        self.running = True

        # Schedule runs according to cron setting
        while self.running:
            try:
                # Calculate seconds until next run
                seconds_until_next = self._calculate_seconds_until_next_run()
                logger.info(
                    f"Next {self.__class__.__name__} run in {seconds_until_next} seconds"
                )

                await asyncio.sleep(seconds_until_next)
                await self.run_daily_computation()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes

    async def stop(self) -> None:
        """Stop the worker."""
        logger.info(f"Stopping {self.__class__.__name__} {self.worker_id}")
        self.running = False

    @abstractmethod
    def get_enabled_setting(self) -> bool:
        """Check if the worker is enabled."""
        pass

    @abstractmethod
    def get_schedule_setting(self) -> str:
        """Get the cron schedule for the worker."""
        pass

    def _calculate_seconds_until_next_run(self) -> float:
        """Calculate seconds until next scheduled run based on schedule setting."""
        schedule_str = self.get_schedule_setting()
        schedule_parts = schedule_str.split()
        if len(schedule_parts) >= 2:
            minute = int(schedule_parts[0])
            hour = int(schedule_parts[1])
        else:
            # Fallback to 2 AM
            minute, hour = 0, 2

        now = datetime.now(timezone.utc)
        target_time = time(hour, minute, 0)

        # Next run is today if not yet passed, otherwise tomorrow
        if now.time() < target_time:
            next_run = datetime.combine(now.date(), target_time)
        else:
            next_run = datetime.combine(now.date() + timedelta(days=1), target_time)

        seconds_until = (next_run - now).total_seconds()
        return max(seconds_until, 0)  # Ensure non-negative

    async def health_check(self) -> WorkerHealthCheckResponse:
        """Health check for the worker."""
        status = "healthy" if self.running else "unhealthy"

        return WorkerHealthCheckResponse(
            status=status, worker_id=self.worker_id, range_status={}
        )
