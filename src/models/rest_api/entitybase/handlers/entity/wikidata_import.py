"""Wikidata import handlers for entity migration."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import HTTPException

from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess.vitess_client import VitessClient
from models.services.wikidata_import_service import WikidataImportService
from .create import EntityCreateHandler
from models.rest_api.entitybase.request import EntityJsonImportRequest
from models.rest_api.entitybase.response import EntityJsonImportResponse

logger = logging.getLogger(__name__)


class EntityJsonImportHandler:
    """Handler for importing entities from Wikidata JSONL dump files."""

    @staticmethod
    async def import_entities_from_jsonl(
        request: EntityJsonImportRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
    ) -> EntityJsonImportResponse:
        """Import entities from a JSONL dump file.

        Args:
            request: Import request with file path and options
            vitess_client: Database client
            s3_client: Storage client
            stream_producer: Event producer
            validator: Data validator

        Returns:
            Import response with counts and error details
        """
        processed_count = 0
        imported_count = 0
        failed_count = 0

        # Create error log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        worker_suffix = f"_{request.worker_id}" if request.worker_id else ""
        error_log_path = Path(
            f"/tmp/wikidata_import_errors{worker_suffix}_{timestamp}.log"
        )

        logger.info(
            f"Starting JSONL import from {request.jsonl_file_path}, lines {request.start_line}-{'end' if request.end_line == 0 else request.end_line}"
        )
        try:
            with open(request.jsonl_file_path, "r", encoding="utf-8") as f:
                create_handler = EntityCreateHandler()

                for line_num, line in enumerate(f, 1):
                    # Skip lines before start_line
                    if line_num < request.start_line:
                        continue

                    # Stop at end_line if specified
                    if request.end_line != 0 and line_num > request.end_line:
                        break

                    processed_count += 1

                    # Process the line
                    entity_data = EntityJsonImportHandler._process_entity_line(
                        line, line_num, error_log_path
                    )
                    if entity_data is None:
                        failed_count += 1
                        continue

                    try:
                        # Transform to create request
                        create_request = (
                            WikidataImportService.transform_to_create_request(
                                entity_data
                            )
                        )

                        # Check if entity already exists
                        entity_exists = EntityJsonImportHandler._check_entity_exists(
                            create_request.id, s3_client
                        )

                        if entity_exists and not request.overwrite_existing:
                            logger.debug(
                                f"Entity {create_request.id} already exists, skipping"
                            )
                            failed_count += 1
                            continue

                        # Create the entity using the existing handler
                        await create_handler.create_entity(
                            create_request,
                            vitess_client,
                            s3_client,
                            stream_producer,
                            validator,
                            auto_assign_id=False,  # Use the Wikidata ID
                        )

                        imported_count += 1

                        # Log progress every 1000 entities
                        if imported_count % 1000 == 0:
                            logger.info(f"Imported {imported_count} entities so far")

                    except Exception as e:
                        logger.error(
                            f"Failed to import entity from line {line_num}: {str(e)}"
                        )
                        failed_count += 1

                        # Log error details
                        with open(error_log_path, "a", encoding="utf-8") as log_f:
                            log_f.write(
                                f"[{datetime.now().isoformat()}] ERROR: Failed to import line {line_num}\n"
                            )
                            log_f.write(
                                f"Entity ID: {entity_data.get('id', 'unknown')}\n"
                            )
                            log_f.write(f"Error: {str(e)}\n")
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

        logger.info(
            f"JSONL import complete: {processed_count} processed, {imported_count} imported, {failed_count} failed"
        )

        return EntityJsonImportResponse(
            processed_count=processed_count,
            imported_count=imported_count,
            failed_count=failed_count,
            error_log_path=str(error_log_path),
        )

    @staticmethod
    def _process_entity_line(
        line: str, line_num: int, error_log_path: Path
    ) -> Optional[Any]:
        """Process a single line from the JSONL file, handling trailing commas and parsing."""
        logger.debug(f"Processing entity line {line_num}")
        line = line.strip()
        if not line:
            return None

        # Remove trailing comma if present
        if line.endswith(","):
            line = line[:-1]

        try:
            parsed: Dict[str, Any] = json.loads(line)
            return parsed
        except json.JSONDecodeError as e:
            # Log malformed line
            with open(error_log_path, "a", encoding="utf-8") as log_f:
                log_f.write(
                    f"[{datetime.now().isoformat()}] ERROR: Failed to parse line {line_num}\n"
                )
                log_f.write(f"Original line: {line}\n")
                log_f.write(f"Error: {str(e)}\n")
                log_f.write("---\n")
            return None

    @staticmethod
    def _check_entity_exists(entity_id: str, s3_client: MyS3Client) -> bool:
        """Check if an entity already exists by trying to read its latest revision."""
        try:
            s3_client.read_revision(entity_id, 1)  # Try to read revision 1
            return True
        except Exception:
            return False
