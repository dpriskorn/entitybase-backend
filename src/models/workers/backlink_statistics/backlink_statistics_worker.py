"""Backlink statistics worker for computing daily analytics."""

import asyncio
import logging
from datetime import date, datetime, timezone

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response.entity.backlink_statistics import (
    BacklinkStatisticsData,
)
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
    BacklinkStatisticsService,
)
from models.workers.base_stats_worker import BaseStatsWorker

try:
    import uvicorn
    from fastapi import FastAPI
except ImportError:
    uvicorn = None  # type: ignore
    FastAPI = None  # type: ignore

logger = logging.getLogger(__name__)


class BacklinkStatisticsWorker(BaseStatsWorker):
    """Computes and stores backlink statistics for entities."""

    def get_enabled_setting(self) -> bool:
        """Check if backlink stats are enabled."""
        return settings.backlink_stats_worker_enabled

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
                state=self.state, top_limit=settings.backlink_stats_top_limit
            )
            stats = service.compute_daily_stats()

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

    async def _store_statistics(self, stats: BacklinkStatisticsData) -> None:
        """Store computed statistics in database via repository."""
        if not self.vitess_client:
            return

        today = date.today().isoformat()

        self.vitess_client.backlink_repository.insert_backlink_statistics(
            date=today,
            total_backlinks=stats.total_backlinks,
            unique_entities_with_backlinks=stats.unique_entities_with_backlinks,
            top_entities_by_backlinks=[
                entity.model_dump(mode="json")
                for entity in stats.top_entities_by_backlinks
            ],
        )


async def run_worker(worker: BacklinkStatisticsWorker) -> None:
    await worker.start()


async def run_server(app: FastAPI) -> None:
    if uvicorn is None:
        raise RuntimeError("uvicorn not installed, cannot run server")
    log_level = logging.getLevelName(settings.get_log_level())
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "handlers": ["default"],
            "level": log_level,
        },
    }
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8004,
        loop="asyncio",
        log_config=logging_config,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("Starting backlink statistics worker main()")
    print("DEBUG: Starting backlink statistics worker main()")

    try:
        worker = BacklinkStatisticsWorker()
        logger.info(f"Worker created, running={worker.running}")
        print(f"DEBUG: Worker created, running={worker.running}")

        if FastAPI is None:
            logger.warning(
                "FastAPI/uvicorn not installed, running worker without HTTP server"
            )
            await worker.start()
        else:
            app = FastAPI(response_model_by_alias=True)
            logger.info("FastAPI app created")
            print("DEBUG: FastAPI app created")

            @app.get("/health")
            async def health() -> WorkerHealthCheckResponse:
                return await worker.health_check()

            logger.info("Starting asyncio.gather() for worker and server")
            print("DEBUG: Starting asyncio.gather() for worker and server")

            try:
                await asyncio.gather(run_worker(worker), run_server(app))
            except Exception as e:
                logger.error(f"Error in asyncio.gather: {e}")
                print(f"ERROR in asyncio.gather: {e}")
                raise

    except Exception as e:
        logger.error(f"Fatal error in main(): {e}")
        print(f"FATAL ERROR in main(): {e}")
        raise
