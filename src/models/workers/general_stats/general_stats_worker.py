"""General statistics worker for computing daily analytics."""

import asyncio
import logging
from datetime import date, datetime, timezone

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.rest_api.entitybase.v1.services.general_stats_service import (
    GeneralStatsData,
    GeneralStatsService,
)
from models.workers.base_stats_worker import BaseStatsWorker

try:
    import uvicorn
    from fastapi import FastAPI
except ImportError:
    uvicorn = None  # type: ignore
    FastAPI = None  # type: ignore

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
            service = GeneralStatsService(state=self.state)
            stats = service.compute_daily_stats()

            # Store in database
            await self._store_statistics(stats)

            self.last_run = datetime.now(timezone.utc)
            logger.info(
                f"Completed general statistics computation: {stats.total_statements} statements, "
                f"{stats.total_items} items, {stats.total_terms} terms"
            )

        except Exception as e:
            logger.error(f"Failed to compute general statistics: {e}")
            raise

    async def _store_statistics(self, stats: GeneralStatsData) -> None:
        """Store computed statistics in database via repository."""
        if not self.vitess_client:
            return

        today = date.today().isoformat()

        self.vitess_client.user_repository.insert_general_statistics(
            date=today,
            total_statements=stats.total_statements,
            total_qualifiers=stats.total_qualifiers,
            total_references=stats.total_references,
            total_items=stats.total_items,
            total_lexemes=stats.total_lexemes,
            total_properties=stats.total_properties,
            total_sitelinks=stats.total_sitelinks,
            total_terms=stats.total_terms,
            terms_per_language=stats.terms_per_language.model_dump(mode="json"),
            terms_by_type=stats.terms_by_type.model_dump(mode="json"),
        )


async def run_worker(worker: GeneralStatsWorker) -> None:
    await worker.start()


async def run_server(app: FastAPI) -> None:
    if uvicorn is None:
        raise RuntimeError("uvicorn not installed, cannot run server")
    config = uvicorn.Config(app, host="0.0.0.0", port=8005, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = GeneralStatsWorker()

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
