"""Base class for statistics workers."""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from types import SimpleNamespace

from pydantic import Field

from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.workers.vitess_worker import VitessWorker
from models.workers.utils import calculate_seconds_until_next_run

logger = logging.getLogger(__name__)


class BaseStatsWorker(VitessWorker, ABC):
    """Base class for statistics workers."""

    worker_id: str = Field(
        default_factory=lambda: os.getenv("WORKER_ID", f"stats-{os.getpid()}")
    )
    last_run: datetime | None = None

    @property
    def state(self) -> SimpleNamespace:
        """Return state object for service compatibility."""
        return SimpleNamespace(vitess_client=self.vitess_client)

    @abstractmethod
    async def run_daily_computation(self) -> None:
        """Run daily statistics computation and storage."""
        pass

    async def start(self) -> None:
        """Start the statistics worker."""
        await super().start()

        if not self.running:
            return

        logger.info(f"Starting {self.__class__.__name__} {self.worker_id}")

        while self.running:
            try:
                seconds_until_next = calculate_seconds_until_next_run(
                    self.get_schedule_setting()
                )
                logger.info(
                    f"Next {self.__class__.__name__} run in {seconds_until_next} seconds"
                )

                await asyncio.sleep(seconds_until_next)
                await self.run_daily_computation()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(300)

    async def stop(self) -> None:
        """Stop the worker."""
        logger.info(f"Stopping {self.__class__.__name__} {self.worker_id}")
        self.running = False

    @abstractmethod
    def get_schedule_setting(self) -> str:
        """Get the cron schedule for the worker."""
        pass

    async def health_check(self) -> WorkerHealthCheckResponse:
        """Health check for the worker."""
        status = "healthy" if self.running else "unhealthy"

        return WorkerHealthCheckResponse(
            status=status,
            worker_id=self.worker_id,
            details={
                "running": self.running,
                "last_run": self.last_run.isoformat() if self.last_run else None,
            },
            range_status={},
        )
