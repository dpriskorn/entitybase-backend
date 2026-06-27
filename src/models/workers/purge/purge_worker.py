"""Purge worker for cleaning S3 buckets and truncating database tables."""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

from minio.error import S3Error
from pydantic import Field

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.workers.mysql_worker import MysqlWorker
from models.workers.utils import calculate_seconds_until_next_run

logger = logging.getLogger(__name__)

S3_BUCKETS = ["revisions", "entitybase-dumps"]

DB_TABLES = [
    "entity_backlinks",
    "entity_id_mapping",
    "entity_head",
    "entity_redirects",
    "statement_content",
    "statements",
    "qualifiers",
    "refs",
    "snaks",
    "backlink_statistics",
    "user_daily_stats",
    "general_daily_stats",
    "metadata_content",
    "sitelinks",
    "entity_revisions",
    "entity_terms",
    "id_ranges",
    "users",
    "watchlist",
    "user_notifications",
    "user_activity",
    "user_thanks",
    "user_statement_endorsements",
    "lexeme_terms",
]


class PurgeWorker(MysqlWorker):
    """Worker that periodically purges all S3 buckets and truncates database tables."""

    s3_client: Any = Field(default=None, exclude=True)
    last_run: datetime | None = None

    def get_enabled_setting(self) -> bool:
        """Check if purge worker is enabled."""
        return settings.purge_worker_enabled

    def get_schedule_setting(self) -> str:
        """Get the schedule for purge worker."""
        return settings.purge_schedule

    async def start(self) -> None:
        """Start the purge worker."""
        if not self.get_enabled_setting():
            logger.info(f"{self.__class__.__name__} disabled")
            return

        logger.info(f"Starting {self.__class__.__name__} {self.worker_id}")

        await super().start()
        if not self.running:
            return

        self._init_s3_client()

        while self.running:
            try:
                seconds_until_next = calculate_seconds_until_next_run(
                    self.get_schedule_setting()
                )
                logger.info(
                    f"Next {self.__class__.__name__} purge in {seconds_until_next} seconds"
                )

                await asyncio.sleep(seconds_until_next)
                await self.run_daily_computation()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                logger.info(f"Retrying in 1 hour...")
                await asyncio.sleep(3600)

    def _init_s3_client(self) -> None:
        """Initialize S3 client."""
        from minio import Minio

        s3_config = settings.get_s3_config
        endpoint = s3_config.endpoint_url
        if endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        elif endpoint.startswith("https://"):
            endpoint = endpoint[8:]
        if "/" in endpoint:
            endpoint = endpoint.split("/")[0]
        self.s3_client = Minio(
            endpoint,
            access_key=s3_config.access_key,
            secret_key=s3_config.secret_key,
            secure=False,
        )
        logger.info("S3 client initialized for purge worker")

    async def run_daily_computation(self) -> None:
        """Run the purge operation."""
        logger.info("Starting purge operation")
        start_time = datetime.now(timezone.utc)

        s3_deleted = await self._purge_s3_buckets()
        db_truncated = await self._truncate_tables()

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        logger.info(
            f"Purge completed: {s3_deleted} S3 objects deleted, "
            f"{db_truncated} tables truncated in {duration:.2f} seconds"
        )

        self.last_run = end_time

    async def _purge_s3_buckets(self) -> int:
        """Delete all objects from all S3 buckets."""
        total_deleted = 0

        for bucket in S3_BUCKETS:
            deleted = await self._purge_bucket(bucket)
            total_deleted += deleted

        return total_deleted

    async def _purge_bucket(self, bucket: str) -> int:
        """Delete all objects from a single S3 bucket."""
        logger.info(f"Purging S3 bucket: {bucket}")
        deleted_count = 0

        try:
            objects = self.s3_client.list_objects(bucket)
            for obj in objects:
                self.s3_client.remove_object(bucket, obj.object_name)
                deleted_count += 1
                logger.debug(f"Deleted object {obj.object_name} from {bucket}")

        except S3Error as e:
            if e.code == "NoSuchBucket":
                logger.warning(f"Bucket {bucket} does not exist, skipping")
            else:
                logger.error(f"Error purging bucket {bucket}: {e}")

        logger.info(f"Deleted {deleted_count} objects from bucket {bucket}")
        return deleted_count

    async def _truncate_tables(self) -> int:
        """Truncate all database tables."""
        logger.info("Truncating database tables")
        truncated = 0

        if not self.db_client:
            logger.error("Database client not initialized")
            return 0

        with self.db_client.cursor as cursor:
            for table in DB_TABLES:
                try:
                    cursor.execute(f"TRUNCATE TABLE {table}")
                    truncated += 1
                    logger.debug(f"Truncated table: {table}")
                except Exception as e:
                    logger.error(f"Error truncating table {table}: {e}")

        logger.info(f"Truncated {truncated} tables")
        return truncated

    async def health_check(self) -> WorkerHealthCheckResponse:
        """Health check for the worker."""
        is_enabled = self.get_enabled_setting()
        status = "healthy" if is_enabled else "disabled"

        return WorkerHealthCheckResponse(
            status=status,
            worker_id=self.worker_id,
            details={
                "running": self.running,
                "next_run_seconds": calculate_seconds_until_next_run(
                    self.get_schedule_setting()
                ),
                "last_run": self.last_run.isoformat() if self.last_run else None,
                "enabled": is_enabled,
            },
            range_status={},
        )


async def run_worker(worker: PurgeWorker) -> None:
    """Run the purge worker."""
    await worker.start()


async def run_server(app: Any) -> None:
    """Run the FastAPI server for health checks."""
    try:
        import uvicorn
    except ImportError:
        logger.warning("uvicorn not installed, running worker without HTTP server")
        return

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
        port=8008,
        loop="asyncio",
        log_config=logging_config,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Main entry point for the purge worker."""
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    worker = PurgeWorker()

    try:
        import uvicorn
        from fastapi import FastAPI
    except ImportError:
        logger.warning(
            "FastAPI/uvicorn not installed, running worker without HTTP server"
        )
        await worker.start()
        return

    app = FastAPI(response_model_by_alias=True)

    @app.get("/health")
    async def health() -> WorkerHealthCheckResponse:
        return await worker.health_check()

    await asyncio.gather(run_worker(worker), run_server(app))


if __name__ == "__main__":
    asyncio.run(main())
