"""Purge worker for cleaning S3 buckets and truncating database tables."""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from pydantic import Field

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.infrastructure.vitess.client import VitessClient
from models.workers.vitess_worker import VitessWorker
from models.workers.utils import calculate_seconds_until_next_run

logger = logging.getLogger(__name__)

S3_BUCKETS = ["revisions", "wikibase-dumps"]

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


class PurgeWorker(VitessWorker):
    """Worker that periodically purges all S3 buckets and truncates database tables."""

    s3_client: Any = Field(default=None, exclude=True)
    last_run: datetime | None = None

    def get_enabled_setting(self) -> bool:
        """Check if purge worker is enabled."""
        return settings.purge_enabled

    def get_schedule_setting(self) -> str:
        """Get the schedule for purge worker."""
        return settings.purge_schedule

    async def start(self) -> None:
        """Start the purge worker."""
        if not self.get_enabled_setting():
            logger.info(f"{self.__class__.__name__} disabled")
            return

        logger.info(f"Starting {self.__class__.__name__} {self.worker_id}")

        vitess_config = settings.get_vitess_config
        self.vitess_client = VitessClient(config=vitess_config)

        self._init_s3_client()

        self.running = True

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
        import boto3
        from botocore.config import Config

        s3_config = settings.get_s3_config
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=s3_config.endpoint_url,
            aws_access_key_id=s3_config.access_key,
            aws_secret_access_key=s3_config.secret_key,
            config=Config(signature_version="s3v4", region_name="us-east-1"),
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
            while True:
                response = self.s3_client.list_objects_v2(Bucket=bucket)
                contents = response.get("Contents", [])

                if not contents:
                    break

                objects_to_delete = [{"Key": obj["Key"]} for obj in contents]

                if objects_to_delete:
                    self.s3_client.delete_objects(
                        Bucket=bucket, Delete={"Objects": objects_to_delete}
                    )
                    deleted_count += len(objects_to_delete)
                    logger.debug(
                        f"Deleted {len(objects_to_delete)} objects from {bucket}"
                    )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchBucket":
                logger.warning(f"Bucket {bucket} does not exist, skipping")
            else:
                logger.error(f"Error purging bucket {bucket}: {e}")

        logger.info(f"Deleted {deleted_count} objects from bucket {bucket}")
        return deleted_count

    async def _truncate_tables(self) -> int:
        """Truncate all database tables."""
        logger.info("Truncating database tables")
        truncated = 0

        if not self.vitess_client:
            logger.error("Vitess client not initialized")
            return 0

        with self.vitess_client.cursor as cursor:
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

    config = uvicorn.Config(app, host="0.0.0.0", port=8008, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Main entry point for the purge worker."""
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
