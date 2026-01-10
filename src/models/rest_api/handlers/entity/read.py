from typing import Any, Dict


from models.validation.utils import raise_validation_error

from models.api import EntityResponse, EntityRevisionResponse
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient

import logging

logger = logging.getLogger(__name__)


class EntityReadHandler:
    """Handler for entity read operations"""

    @staticmethod
    def get_entity(
        entity_id: str,
        vitess_client: VitessClient,
        s3_client: S3Client,
        fetch_metadata: bool = False,
    ) -> EntityResponse:
        """Get entity by ID."""
        if vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        if not vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity not found", status_code=404)

        try:
            revision = s3_client.read_revision(entity_id, head_revision_id)
            data = revision.data.get("entity", {}).copy()

            # Load metadata from S3
            if fetch_metadata:
                labels_hash = revision.data.get("labels_hash")
                if labels_hash:
                    data["labels"] = s3_client.load_metadata("labels", labels_hash)

                descriptions_hash = revision.data.get("descriptions_hash")
                if descriptions_hash:
                    data["descriptions"] = s3_client.load_metadata(
                        "descriptions", descriptions_hash
                    )

                aliases_hash = revision.data.get("aliases_hash")
                if aliases_hash:
                    data["aliases"] = s3_client.load_metadata("aliases", aliases_hash)
            else:
                # For legacy compatibility, merge metadata into entity data
                entity_data = data["entity"]
                labels_hash = revision.data.get("labels_hash")
                if labels_hash:
                    entity_data["labels"] = s3_client.load_metadata(
                        "labels", labels_hash
                    )

                descriptions_hash = revision.data.get("descriptions_hash")
                if descriptions_hash:
                    entity_data["descriptions"] = s3_client.load_metadata(
                        "descriptions", descriptions_hash
                    )

                aliases_hash = revision.data.get("aliases_hash")
                if aliases_hash:
                    entity_data["aliases"] = s3_client.load_metadata(
                        "aliases", aliases_hash
                    )

            return EntityResponse(
                id=entity_id,
                revision_id=head_revision_id,
                data=data,
                is_semi_protected=revision.data.get("is_semi_protected", False),
                is_locked=revision.data.get("is_locked", False),
                is_archived=revision.data.get("is_archived", False),
                is_dangling=revision.data.get("is_dangling", False),
                is_mass_edit_protected=revision.data.get(
                    "is_mass_edit_protected", False
                ),
            )
        except Exception as e:
            logger.error(f"Failed to read entity {entity_id}: {e}")
            raise_validation_error("Failed to read entity", status_code=500)

    @staticmethod
    def get_entity_history(  # type: ignore[return]
        entity_id: str,
        vitess_client: VitessClient,
        s3_client: S3Client,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Dict[str, Any]]:
        """Get entity revision history."""
        if vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        try:
            # For now, return a simple list. In a real implementation,
            # we'd need to get revision IDs from Vitess
            revisions: list[Dict[str, Any]] = []
            # This is a placeholder - actual implementation would query Vitess
            # for revision history
            logger.info(f"Getting history for {entity_id} (placeholder implementation)")
            return revisions
        except Exception as e:
            logger.error(f"Failed to get entity history for {entity_id}: {e}")
            raise_validation_error("Failed to get entity history", status_code=500)

    @staticmethod
    def get_entity_revision(  # type: ignore[return]
        entity_id: str,
        revision_id: int,
        s3_client: S3Client,
    ) -> EntityRevisionResponse:
        """Get specific entity revision."""
        if s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        try:
            revision = s3_client.read_revision(entity_id, revision_id)
            data = revision.data.copy()
            entity_data = data.get("entity", {}).copy()

            # Load metadata from S3
            labels_hash = data.get("labels_hash")
            if labels_hash:
                entity_data["labels"] = s3_client.load_metadata("labels", labels_hash)

            descriptions_hash = data.get("descriptions_hash")
            if descriptions_hash:
                entity_data["descriptions"] = s3_client.load_metadata(
                    "descriptions", descriptions_hash
                )

            aliases_hash = data.get("aliases_hash")
            if aliases_hash:
                entity_data["aliases"] = s3_client.load_metadata(
                    "aliases", aliases_hash
                )

            data["entity"] = entity_data

            return EntityRevisionResponse(
                entity_id=entity_id,
                revision_id=revision_id,
                data=data,
            )
        except Exception as e:
            logger.error(
                f"Failed to read revision {revision_id} for entity {entity_id}: {e}"
            )
            raise_validation_error("Revision not found", status_code=404)
