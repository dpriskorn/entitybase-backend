"""TTL (RDF Turtle) dump worker for generating weekly RDF dumps of entities."""

import asyncio
import gzip
import hashlib
import logging
import tempfile
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta, timezone
from io import StringIO
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

try:
    from models.rdf_builder.property_registry.loader import load_property_registry
except ImportError:
    load_property_registry = None  # type: ignore

from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.writers.triple import TripleWriters
from models.workers.dump_types import DumpMetadata, EntityDumpRecord
from models.workers.worker import Worker

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.infrastructure.s3.client import MyS3Client
from models.infrastructure.s3.connection import S3ConnectionManager
from models.infrastructure.vitess.client import VitessClient
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.writers.triple import TripleWriters
from models.workers.dump_types import DumpMetadata, EntityDumpRecord
from models.workers.worker import Worker

logger = logging.getLogger(__name__)


class TtlDumpWorker(Worker):
    vitess_client: Any = None
    s3_client: Any = None
    converter: Any = None
    running: bool = False
    last_run: datetime | None = None

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None, None]:
        """Initialize clients for the worker lifespan."""
        logger.info("Initializing TTL Dump Worker")

        if VitessClient is None:
            raise RuntimeError("Vitess client not available")

        if MyS3Client is None:
            raise RuntimeError("S3 client not available")

        if load_property_registry is None:
            raise RuntimeError("Property registry loader not available")

        vitess_config = settings.get_vitess_config
        self.vitess_client = VitessClient(config=vitess_config)

        s3_config = settings.get_s3_config
        s3_config.bucket = settings.s3_dump_bucket
        s3_connection = S3ConnectionManager(config=s3_config)  # type: ignore
        s3_connection.connect()  # type: ignore
        self.s3_client = MyS3Client(config=s3_config)  # type: ignore
        self.s3_client.connection_manager = s3_connection  # type: ignore

        property_registry = load_property_registry(settings.property_registry_path)
        self.converter = EntityConverter(
            property_registry=property_registry,
            vitess_client=self.vitess_client,
            enable_deduplication=True,
        )

        yield

        logger.info("Shutting down TTL Dump Worker")

    async def start(self) -> None:
        if not settings.ttl_dump_enabled:
            logger.info("TTL Dump Worker disabled")
            return

        logger.info(f"Starting TTL Dump Worker {self.worker_id}")

        async with self.lifespan():
            self.running = True

            while self.running:
                try:
                    seconds_until_next = self._calculate_seconds_until_next_run()
                    logger.info(f"Next TTL dump run in {seconds_until_next} seconds")
                    await asyncio.sleep(seconds_until_next)

                    await self.run_weekly_dump()

                except Exception as e:
                    logger.error(f"Error in worker loop: {e}")
                    await asyncio.sleep(300)

    async def run_weekly_dump(self) -> None:
        try:
            logger.info("Starting weekly TTL dump generation")
            now = datetime.now(timezone.utc)
            week_start = now - timedelta(days=7)

            logger.info("Fetching entities for full dump")
            full_entities = await self._fetch_all_entities()
            logger.info(f"Found {len(full_entities)} entities for full dump")

            logger.info("Fetching entities for incremental dump")
            incremental_entities = await self._fetch_entities_for_week(week_start, now)
            logger.info(f"Found {len(incremental_entities)} entities for incremental dump")

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
            logger.info("Completed weekly TTL dump generation")

        except Exception as e:
            logger.error(f"Failed to generate weekly TTL dump: {e}")
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

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT eim.entity_id, eh.internal_id, eh.head_revision_id
                   FROM entity_id_mapping eim
                   JOIN entity_head eh ON eim.internal_id = eh.internal_id
                   WHERE eh.is_deleted = FALSE"""
            )
            results = cursor.fetchall()
            entities = [
                EntityDumpRecord(
                    entity_id=row[0], internal_id=row[1], revision_id=row[2]
                )
                for row in results
            ]

            for i in range(0, len(entities), settings.ttl_dump_batch_size):
                batch = entities[i : i + settings.ttl_dump_batch_size]
                entity_ids = [e.entity_id for e in batch]
                entity_id_list = ",".join(f"'{eid}'" for eid in entity_ids)

                cursor.execute(
                    f"""SELECT revision_id, internal_id, updated_at
                       FROM entity_revisions
                       WHERE internal_id IN (
                           SELECT internal_id FROM entity_id_mapping WHERE entity_id IN ({entity_id_list})
                       )
                       AND updated_at >= %s AND updated_at < %s""",
                    (week_start, week_end),
                )
                revision_results = cursor.fetchall()

                entity_map = {e.entity_id: e for e in batch}
                for rev_id, internal_id, updated_at in revision_results:
                    for entity in batch:
                        if entity.internal_id == internal_id and entity.revision_id == rev_id:
                            entity.updated_at = updated_at
                            break

            return [e for e in entities if e.updated_at is not None]

    async def _generate_and_upload_dump(
        self,
        entities: list[EntityDumpRecord],
        dump_date: str,
        dump_type: str,
        week_start: datetime,
        week_end: datetime,
    ) -> None:
        logger.info(f"Generating {dump_type} TTL dump for {len(entities)} entities")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            filename = f"{dump_type}.ttl"
            if settings.ttl_dump_compression:
                filename += ".gz"
            filepath = tmppath / filename

            entity_count, triples_count = await self._generate_ttl_dump(
                entities, filepath, week_start, week_end
            )

            checksum = ""
            if settings.ttl_dump_generate_checksums:
                checksum = self._generate_checksum(filepath)

            s3_key = f"weekly/{dump_date}/{filename}"
            await self._upload_to_s3(filepath, s3_key, checksum)

            metadata_file = tmppath / "metadata.json"
            metadata = DumpMetadata(
                dump_id=dump_date,
                generated_at=datetime.now(timezone.utc),
                time_range_start=week_start,
                time_range_end=week_end,
                entity_count=entity_count,
                format="turtle",
                file=filename,
                size_bytes=filepath.stat().st_size,
                sha256=checksum,
                compression=settings.ttl_dump_compression,
                dump_type=dump_type,
            )
            metadata_dict = metadata.model_dump()
            metadata_dict["triples_count"] = triples_count

            with open(metadata_file, "w") as f:
                import json
                json.dump(metadata_dict, f, indent=2)

            metadata_key = f"weekly/{dump_date}/metadata.json"
            await self._upload_to_s3(metadata_file, metadata_key, "")

    async def _generate_ttl_dump(
        self,
        entities: list[EntityDumpRecord],
        output_path: Path,
        week_start: datetime,
        week_end: datetime,
    ) -> tuple[int, int]:
        logger.info("Generating TTL dump file")

        if not self.s3_client or not self.converter:
            raise ValueError("S3 client or converter not initialized")

        writers = TripleWriters()

        opener = gzip.open if settings.ttl_dump_compression else open
        mode = "wt" if settings.ttl_dump_compression else "w"

        entity_count = 0
        triples_count = 0

        with opener(output_path, mode, encoding="utf-8") as f:
            writers.write_header(f)

            now = datetime.now(timezone.utc).isoformat()
            week_start_iso = week_start.isoformat()

            f.write(f"""# Dump metadata
[] a schema:DataDownload ;
    schema:dateModified "{now}"^^xsd:dateTime ;
    schema:temporalCoverage "{week_start_iso}/{now}" ;
    dcat:downloadURL <https://s3.amazonaws.com/{settings.s3_dump_bucket}/weekly/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}/full.ttl> ;
    schema:encodingFormat "text/turtle" ;
    schema:name "Wikibase Weekly RDF Dump" .

""")

            for i in range(0, len(entities), settings.ttl_dump_batch_size):
                batch = entities[i : i + settings.ttl_dump_batch_size]
                logger.info(
                    f"Processing batch {i // settings.ttl_dump_batch_size + 1}/{(len(entities) + settings.ttl_dump_batch_size - 1) // settings.ttl_dump_batch_size}"
                )

                tasks = [
                    self._fetch_and_convert_entity(record, writers)
                    for record in batch
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for record, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to process {record.entity_id}: {result}")
                        continue
                    if result:
                        f.write(result)
                        f.write("\n")
                        entity_count += 1
                        triples_count += result.count(";")

        return entity_count, triples_count

    async def _fetch_and_convert_entity(
        self, record: EntityDumpRecord, writers: TripleWriters
    ) -> str | None:
        if not self.s3_client or not self.converter:
            return None

        try:
            revision_data = self.s3_client.read_revision(
                record.entity_id, record.revision_id
            )

            from models.data.rest_api.v1.entitybase.response import EntityMetadataResponse

            entity_response = EntityMetadataResponse(
                id=record.entity_id,
                type=revision_data.revision.get("type", "item"),
                labels={"data": revision_data.revision.get("labels", {})},
                descriptions={"data": revision_data.revision.get("descriptions", {})},
                aliases={"data": revision_data.revision.get("aliases", {})},
                sitelinks={"data": revision_data.revision.get("sitelinks", {})},
                statements={"data": revision_data.revision.get("claims", [])},
            )

            output = StringIO()
            self.converter.convert_to_turtle(entity_response, output)
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error processing {record.entity_id}: {e}")
            return None

    def _generate_checksum(self, filepath: Path) -> str:
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def _upload_to_s3(self, filepath: Path, s3_key: str, checksum: str) -> None:
        if not self.s3_client or not self.s3_client.connection_manager:
            raise ValueError("S3 connection manager not initialized")

        boto_client = self.s3_client.connection_manager.boto_client
        content_type = "text/turtle" if not str(filepath).endswith(".gz") else "application/gzip"

        extra_args = {"ContentType": content_type}
        if checksum:
            extra_args["Metadata"] = {"sha256": checksum}

        boto_client.upload_file(
            str(filepath),
            settings.s3_dump_bucket,
            s3_key,
            ExtraArgs=extra_args,
        )

        logger.info(f"Uploaded {filepath.name} to s3://{settings.s3_dump_bucket}/{s3_key}")

    def _calculate_seconds_until_next_run(self) -> float:
        schedule_str = settings.ttl_dump_schedule
        schedule_parts = schedule_str.split()
        if len(schedule_parts) >= 2:
            minute = int(schedule_parts[0])
            hour = int(schedule_parts[1])
        else:
            minute, hour = 0, 3

        now = datetime.now(timezone.utc)
        target_time = time(hour, minute, 0)

        if now.time() < target_time:
            next_run = datetime.combine(now.date(), target_time)
        else:
            next_run = datetime.combine(now.date() + timedelta(days=1), target_time)

        seconds_until = (next_run - now).total_seconds()
        return max(seconds_until, 0)

    def health_check(self) -> WorkerHealthCheckResponse:
        status = "healthy" if self.running else "unhealthy"
        return WorkerHealthCheckResponse(
            status=status, worker_id=self.worker_id, range_status={}
        )


async def run_worker(worker: TtlDumpWorker) -> None:
    await worker.start()


async def run_server(app: Any) -> None:
    if uvicorn is None:
        raise RuntimeError("uvicorn not installed, cannot run server")
    config = uvicorn.Config(app, host="0.0.0.0", port=8003, loop="asyncio")  # type: ignore
    server = uvicorn.Server(config)  # type: ignore
    await server.serve()


async def main() -> None:
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = TtlDumpWorker()

    if FastAPI is None:
        logger.warning("FastAPI/uvicorn not installed, running worker without HTTP server")
        await worker.start()
    else:
        app = FastAPI()

        @app.get("/health")
        def health() -> WorkerHealthCheckResponse:
            return worker.health_check()

        await asyncio.gather(
            run_worker(worker),
            run_server(app),
        )


if __name__ == "__main__":
    asyncio.run(main())
