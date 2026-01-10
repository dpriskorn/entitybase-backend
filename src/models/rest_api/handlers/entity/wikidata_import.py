import logging
import tempfile
from pathlib import Path
from typing import Any


from models.api.entity import EntityImportRequest, EntityImportResponse
from models.services.wikidata_import_service import WikidataImportService
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from .create import EntityCreateHandler

logger = logging.getLogger(__name__)


class EntityImportHandler:
    """Handler for importing entities from Wikidata."""

    @staticmethod
    async def import_entities(
        request: EntityImportRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
    ) -> EntityImportResponse:
        """Import multiple entities from Wikidata.

        Args:
            request: Import request with entity IDs and options
            vitess_client: Database client
            s3_client: Storage client
            stream_producer: Event producer
            validator: Data validator

        Returns:
            Import response with counts and error details

        Raises:
            HTTPException: If any entity conflicts occur (when overwrite_existing=False)
        """
        imported_count = 0
        failed_count = 0
        errors = []
        log_entries = []

        # Create temporary log file
        log_file = (
            Path(tempfile.gettempdir())
            / f"wikibase-import-{int(__import__('time').time())}.log"
        )

        with open(log_file, "w") as log_f:
            log_f.write("Wikidata Import Log\n")
            log_f.write("=" * 50 + "\n")

            create_handler = EntityCreateHandler()

            for entity_id in request.entity_ids:
                try:
                    logger.info(f"Processing import for {entity_id}")

                    # Check if entity already exists
                    try:
                        # Try to read current revision - if exists, handle conflict
                        s3_client.read_revision(
                            entity_id, 1
                        )  # Check if any revision exists
                        entity_exists = True
                    except Exception:
                        entity_exists = False

                    if entity_exists and not request.overwrite_existing:
                        error_msg = f"Entity {entity_id} already exists and overwrite_existing=False"
                        errors.append(error_msg)
                        log_entries.append(f"ERROR: {error_msg}")
                        failed_count += 1
                        continue

                    # Fetch and transform entity
                    create_request = WikidataImportService.import_entity(entity_id)

                    # Create the entity using the existing handler
                    response = await create_handler.create_entity(
                        create_request,
                        vitess_client,
                        s3_client,
                        stream_producer,
                        validator,
                        auto_assign_id=False,  # Use the Wikidata ID
                    )

                    logger.info(f"Successfully imported {entity_id}")
                    imported_count += 1
                    log_entries.append(
                        f"SUCCESS: Imported {entity_id} as revision {response.revision_id}"
                    )

                except ValueError as e:
                    error_msg = f"Failed to import {entity_id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    log_entries.append(f"ERROR: {error_msg}")
                    failed_count += 1

                except Exception as e:
                    error_msg = f"Unexpected error importing {entity_id}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    log_entries.append(f"ERROR: {error_msg}")
                    failed_count += 1

            # Write log entries
            for entry in log_entries:
                log_f.write(entry + "\n")

        logger.info(
            f"Import complete: {imported_count} imported, {failed_count} failed"
        )

        return EntityImportResponse(
            imported_count=imported_count,
            failed_count=failed_count,
            errors=errors,
            log_file=str(log_file),
        )
