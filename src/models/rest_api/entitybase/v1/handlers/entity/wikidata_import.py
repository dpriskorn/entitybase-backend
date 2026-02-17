"""Wikidata import handlers for entity migration."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import HTTPException

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityJsonImportRequest
from models.data.rest_api.v1.entitybase.response import EntityJsonImportResponse
from models.infrastructure.s3.client import MyS3Client
from models.services.wikidata_import_service import WikidataImportService
from .create import EntityCreateHandler
from ...handler import Handler

logger = logging.getLogger(__name__)


class EntityJsonImportHandler(Handler):
    """Handler for importing entities from Wikidata JSONL dump files."""

    def _create_error_log_path(self, worker_id: str | None) -> Path:
        """Generate error log file path with timestamp and worker ID.

        Args:
            worker_id: Optional worker identifier

        Returns:
            Path for error log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        worker_suffix = f"_{worker_id}" if worker_id else ""
        return Path(f"/tmp/wikidata_import_errors{worker_suffix}_{timestamp}.log")

    def _should_process_line(
        self, line_num: int, start_line: int, end_line: int
    ) -> bool:
        """Check if a line should be processed based on range.

        Args:
            line_num: Current line number
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (0 means end of file)

        Returns:
            True if line should be processed, False otherwise
        """
        if line_num < start_line:
            return False
        if end_line != 0 and line_num > end_line:
            return False
        return True

    async def _process_single_entity(
        self,
        entity_data: dict[str, Any],
        line_num: int,
    ) -> tuple[bool, bool]:
        """Process a single entity with all error handling.

        Args:
            entity_data: Parsed entity data
            line_num: Line number for error logging

        Returns:
            Tuple of (success, failed)
        """
        create_handler = self._import_create_handler
        request = self._import_request
        validator = self._import_validator
        error_log_path = self._import_error_log_path
        try:
            create_request = WikidataImportService.transform_to_create_request(
                entity_data
            )

            entity_exists = EntityJsonImportHandler._check_entity_exists(
                entity_id=create_request.id, s3_client=self.state.s3_client
            )

            if entity_exists and not request.overwrite_existing:
                logger.debug(f"Entity {create_request.id} already exists, skipping")
                return False, False

            edit_headers_data = {
                "x_user_id": 0,
                "x_edit_summary": "Wikidata import",
            }

            await create_handler.create_entity(
                create_request,
                EditHeaders(**edit_headers_data),
                validator,
                auto_assign_id=False,
            )

            return True, False
        except Exception as e:
            logger.error(f"Failed to import entity from line {line_num}: {str(e)}")
            with open(error_log_path, "a", encoding="utf-8") as log_f:
                log_f.write(
                    f"[{datetime.now().isoformat()}] ERROR: Failed to import line {line_num}\n"
                )
                log_f.write(f"Entity ID: {entity_data.get('id', 'unknown')}\n")
                log_f.write(f"Error: {str(e)}\n")
            return False, True

    async def import_entities_from_jsonl(
        self,
        request: EntityJsonImportRequest,
        validator: Any | None = None,
    ) -> EntityJsonImportResponse:
        """Import entities from a JSONL dump file.

        Args:
            request: Import request with file path and options
            validator: Data validator

        Returns:
            Import response with counts and error details
        """
        processed_count = 0
        imported_count = 0
        failed_count = 0

        error_log_path = self._create_error_log_path(request.worker_id)

        self._import_request = request
        self._import_validator = validator
        self._import_error_log_path = error_log_path

        logger.info(
            f"Starting JSONL import from {request.jsonl_file_path}, lines {request.start_line}-{'end' if request.end_line == 0 else request.end_line}"
        )

        try:
            with open(request.jsonl_file_path, "r", encoding="utf-8") as f:
                create_handler = EntityCreateHandler(state=self.state)
                self._import_create_handler = create_handler

                for line_num, line in enumerate(f, 1):
                    if not self._should_process_line(
                        line_num, request.start_line, request.end_line
                    ):
                        continue

                    processed_count += 1

                    entity_data = EntityJsonImportHandler._process_entity_line(
                        line, line_num, error_log_path
                    )
                    if entity_data is None:
                        failed_count += 1
                        continue

                    success, failed = await self._process_single_entity(
                        entity_data,
                        line_num,
                    )
                    if success:
                        imported_count += 1
                        if imported_count % 1000 == 0:
                            logger.info(f"Imported {imported_count} entities so far")
                    elif failed:
                        failed_count += 1

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
