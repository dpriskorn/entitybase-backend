"""User statistics worker for computing daily analytics."""

import asyncio
import logging
from datetime import date, datetime, timezone

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response import UserStatsData
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.rest_api.entitybase.v1.services.user_stats_service import (
    UserStatsService,
)
from models.workers.base_stats_worker import BaseStatsWorker

try:
    import uvicorn
    from fastapi import FastAPI
except ImportError:
    uvicorn = None  # type: ignore
    FastAPI = None  # type: ignore

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
            service = UserStatsService(state=self.state)
            stats = service.compute_daily_stats()

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

        self.vitess_client.user_repository.insert_user_statistics(
            date=today,
            total_users=stats.total_users,
            active_users=stats.active_users,
        )


async def run_worker(worker: UserStatsWorker) -> None:
    await worker.start()


async def run_server(app: FastAPI) -> None:
    if uvicorn is None:
        raise RuntimeError("uvicorn not installed, cannot run server")
    config = uvicorn.Config(app, host="0.0.0.0", port=8006, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = UserStatsWorker()

    if FastAPI is None:
        logger.warning(
            "FastAPI/uvicorn not installed, running worker without HTTP server"
        )
        await worker.start()
    else:
        app = FastAPI(response_model_by_alias=True)

        @app.get("/health")
        async def health() -> WorkerHealthCheckResponse:
            return await worker.health_check()

        await asyncio.gather(run_worker(worker), run_server(app))
