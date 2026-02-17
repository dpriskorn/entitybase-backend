"""JSON dump worker for generating weekly JSON dumps of entities."""

import asyncio
import gzip
import json
import logging
import os
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import uvicorn
    from fastapi import FastAPI
except ImportError:
    uvicorn = None  # type: ignore
    FastAPI = None  # type: ignore

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.utils.checksum import generate_file_sha256
from models.workers.utils import calculate_seconds_until_next_run

try:
    from models.infrastructure.s3.client import MyS3Client
    from models.infrastructure.s3.connection import S3ConnectionManager
except ImportError:
    MyS3Client = None  # type: ignore
    S3ConnectionManager = None  # type: ignore

try:
    from models.infrastructure.vitess.client import VitessClient
except ImportError:
    VitessClient = None  # type: ignore

from models.workers.dump_types import DumpMetadata, EntityDumpRecord
from models.workers.worker import Worker

logger = logging.getLogger(__name__)


class JsonDumpWorker(Worker):
    vitess_client: Any = None
    s3_client: Any = None
    running: bool = False
    last_run: datetime | None = None

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None, None]:
        """Initialize clients for the worker lifespan."""
        logger.info("Initializing JSON Dump Worker")

        if VitessClient is None:
            raise RuntimeError("Vitess client not available")

        if MyS3Client is None:
            raise RuntimeError("S3 client not available")

        vitess_config = settings.get_vitess_config
        self.vitess_client = VitessClient(config=vitess_config)

        s3_config = settings.get_s3_config
        s3_config.bucket = settings.s3_dump_bucket
        s3_connection = S3ConnectionManager(config=s3_config)  # type: ignore
        s3_connection.connect()  # type: ignore
        self.s3_client = MyS3Client(config=s3_config)  # type: ignore
        self.s3_client.connection_manager = s3_connection  # type: ignore

        yield

        logger.info("Shutting down JSON Dump Worker")

    async def start(self) -> None:
        if not settings.json_dump_enabled:
            logger.info("JSON Dump Worker disabled")
            return

        logger.info(f"Starting JSON Dump Worker {self.worker_id}")

        async with self.lifespan():
            self.running = True

            while self.running:
                try:
                    seconds_until_next = calculate_seconds_until_next_run(
                        settings.json_dump_schedule
                    )
                    logger.info(f"Next JSON dump run in {seconds_until_next} seconds")
                    await asyncio.sleep(seconds_until_next)

                    await self.run_weekly_dump()

                except Exception as e:
                    logger.error(f"Error in worker loop: {e}")
                    await asyncio.sleep(300)

    async def run_weekly_dump(self) -> None:
        try:
            logger.info("Starting weekly JSON dump generation")
            now = datetime.now(timezone.utc)
            week_start = now - timedelta(days=7)

            logger.info("Fetching entities for full dump")
            full_entities = await self._fetch_all_entities()
            logger.info(f"Found {len(full_entities)} entities for full dump")

            logger.info("Fetching entities for incremental dump")
            incremental_entities = await self._fetch_entities_for_week(week_start, now)
            logger.info(
                f"Found {len(incremental_entities)} entities for incremental dump"
            )

            dump_date = now.strftime("%Y-%m-%d")

            if full_entities:
                await self._generate_and_upload_dump(
                    full_entities, dump_date, "full", week_start, now
                )

            if incremental_entities:
                await self._generate_and_upload_dump(
                    incremental_entities, dump_date, "incremental", week_start, now
                )

            self.last_run = now
            logger.info("Completed weekly JSON dump generation")

        except Exception as e:
            logger.error(f"Failed to generate weekly JSON dump: {e}")
            raise

    async def _fetch_all_entities(self) -> list[EntityDumpRecord]:
        if not self.vitess_client:
            raise ValueError("Vitess client not initialized")

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT eim.entity_id, eh.internal_id, eh.head_revision_id
                   FROM entity_id_mapping eim
                   JOIN entity_head eh ON eim.internal_id = eh.internal_id
                   WHERE eh.is_deleted = FALSE"""
            )
            results = cursor.fetchall()
            return [
                EntityDumpRecord(
                    entity_id=row[0], internal_id=row[1], revision_id=row[2]
                )
                for row in results
            ]

    async def _fetch_entities_for_week(
        self, week_start: datetime, week_end: datetime
    ) -> list[EntityDumpRecord]:
        if not self.vitess_client:
            raise ValueError("Vitess client not initialized")

        entities = await self._fetch_all_entity_records()
        await self._filter_entities_by_week(entities, week_start, week_end)
        return [e for e in entities if e.updated_at is not None]

    async def _fetch_all_entity_records(self) -> list[EntityDumpRecord]:
        """Fetch all entity records from the database."""
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT eim.entity_id, eh.internal_id, eh.head_revision_id
                   FROM entity_id_mapping eim
                   JOIN entity_head eh ON eim.internal_id = eh.internal_id
                   WHERE eh.is_deleted = FALSE"""
            )
            results = cursor.fetchall()
            return [
                EntityDumpRecord(
                    entity_id=row[0], internal_id=row[1], revision_id=row[2]
                )
                for row in results
            ]

    async def _filter_entities_by_week(
        self, entities: list[EntityDumpRecord], week_start: datetime, week_end: datetime
    ) -> None:
        """Filter entities updated within the given week."""
        with self.vitess_client.cursor as cursor:
            for i in range(0, len(entities), settings.json_dump_batch_size):
                batch = entities[i : i + settings.json_dump_batch_size]
                await self._update_batch_with_revisions(cursor, batch, week_start, week_end)

    async def _update_batch_with_revisions(
        self, cursor: Any, batch: list[EntityDumpRecord], week_start: datetime, week_end: datetime
    ) -> None:
        """Update a batch of entities with their revision timestamps."""
        entity_ids = [e.entity_id for e in batch]
        entity_id_list = ",".join(f"'{eid}'" for eid in entity_ids)

        cursor.execute(
            f"""SELECT revision_id, internal_id, created_at
               FROM entity_revisions
               WHERE internal_id IN (
                   SELECT internal_id FROM entity_id_mapping WHERE entity_id IN ({entity_id_list})
               )
               AND created_at >= %s AND created_at < %s""",
            (week_start, week_end),
        )
        revision_results = cursor.fetchall()

        for rev_id, internal_id, created_at in revision_results:
            for entity in batch:
                if entity.internal_id == internal_id and entity.revision_id == rev_id:
                    entity.updated_at = created_at
                    break

    async def _generate_and_upload_dump(
        self,
        entities: list[EntityDumpRecord],
        dump_date: str,
        dump_type: str,
        week_start: datetime,
        week_end: datetime,
    ) -> None:
        logger.info(f"Generating {dump_type} JSON dump for {len(entities)} entities")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            filename = f"{dump_type}.json.gz"
            filepath = tmppath / filename

            await self._generate_json_dump(entities, filepath, week_start, week_end)

            checksum = ""
            if settings.json_dump_generate_checksums:
                checksum = generate_file_sha256(filepath)

            s3_key = f"weekly/{dump_date}/{filename}"
            await self._upload_to_s3(filepath, s3_key, checksum)

            metadata_file = tmppath / "metadata.json"
            metadata = DumpMetadata(
                dump_id=dump_date,
                generated_at=datetime.now(timezone.utc),
                time_range_start=week_start,
                time_range_end=week_end,
                entity_count=len(entities),
                format="canonical-json",
                file=filename,
                size_bytes=filepath.stat().st_size,
                sha256=checksum,
                compression=True,
                dump_type=dump_type,
            )
            with open(metadata_file, "w") as f:
                json.dump(metadata.model_dump(mode="json"), f, indent=2)

            metadata_key = f"weekly/{dump_date}/metadata.json"
            await self._upload_to_s3(metadata_file, metadata_key, "")

    async def _generate_json_dump(
        self,
        entities: list[EntityDumpRecord],
        output_path: Path,
        week_start: datetime,
        week_end: datetime,
    ) -> None:
        logger.info("Generating JSON dump file")

        if not self.s3_client:
            raise ValueError("S3 client not initialized")

        entity_data_list = []
        for i in range(0, len(entities), settings.json_dump_batch_size):
            batch = entities[i : i + settings.json_dump_batch_size]
            logger.info(
                f"Fetching batch {i // settings.json_dump_batch_size + 1}/{(len(entities) + settings.json_dump_batch_size - 1) // settings.json_dump_batch_size}"
            )

            tasks = [self._fetch_entity_data(record) for record in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for record, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to fetch {record.entity_id}: {result}")
                    continue
                if result:
                    entity_data_list.append(
                        {
                            "entity": result,
                            "metadata": {
                                "revision_id": record.revision_id,
                                "entity_id": record.entity_id,
                                "s3_uri": f"s3://{settings.s3_dump_bucket}/{record.entity_id}/r{record.revision_id}.json",
                                "updated_at": record.updated_at.isoformat()
                                if record.updated_at
                                else None,
                            },
                        }
                    )

        dump_data = {
            "dump_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "time_range": f"{week_start.isoformat()}/{week_end.isoformat()}",
                "entity_count": len(entity_data_list),
                "format": "canonical-json",
            },
            "entities": entity_data_list,
        }

        with gzip.open(output_path, "wb") as f:
            f.write(json.dumps(dump_data, indent=2).encode("utf-8"))  # type: ignore[arg-type]

    async def _fetch_entity_data(
        self, record: EntityDumpRecord
    ) -> dict[str, Any] | None:
        if not self.s3_client:
            return None

        try:
            revision_data = self.s3_client.read_revision(
                record.entity_id, record.revision_id
            )
            return revision_data.revision  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Error fetching {record.entity_id}: {e}")
            return None

    def _calculate_seconds_until_next_run(self) -> int:
        """Calculate seconds until next scheduled run."""
        return calculate_seconds_until_next_run(settings.json_dump_schedule)

    def _generate_checksum(self, filepath: Path) -> str:
        """Generate SHA256 checksum for a file."""
        return generate_file_sha256(filepath)

    async def _upload_to_s3(self, filepath: Path, s3_key: str, checksum: str) -> None:
        if not self.s3_client or not self.s3_client.connection_manager:
            raise ValueError("S3 connection manager not initialized")

        boto_client = self.s3_client.connection_manager.boto_client
        content_type = (
            "application/json"
            if not str(filepath).endswith(".gz")
            else "application/gzip"
        )

        extra_args: dict[str, Any] = {"ContentType": content_type}
        if checksum:
            extra_args["Metadata"] = {"sha256": checksum}

        boto_client.upload_file(
            str(filepath),
            settings.s3_dump_bucket,
            s3_key,
            ExtraArgs=extra_args,
        )

        logger.info(
            f"Uploaded {filepath.name} to s3://{settings.s3_dump_bucket}/{s3_key}"
        )

    def health_check(self) -> WorkerHealthCheckResponse:
        status = "healthy" if self.running else "unhealthy"
        return WorkerHealthCheckResponse(
            status=status, worker_id=self.worker_id, range_status={}
        )


async def run_worker(worker: JsonDumpWorker) -> None:
    await worker.start()


async def run_server(app: Any) -> None:
    if uvicorn is None:
        raise RuntimeError("uvicorn not installed, cannot run server")
    config = uvicorn.Config(app, host="0.0.0.0", port=8002, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = JsonDumpWorker()

    if FastAPI is None:
        logger.warning(
            "FastAPI/uvicorn not installed, running worker without HTTP server"
        )
        await worker.start()
    else:
        app = FastAPI(response_model_by_alias=True)

        @app.get("/health")
        def health() -> WorkerHealthCheckResponse:
            return worker.health_check()

        await asyncio.gather(
            run_worker(worker),
            run_server(app),
        )


if __name__ == "__main__":
    asyncio.run(main())
