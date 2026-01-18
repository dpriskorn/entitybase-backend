"""Entity read and retrieval handlers."""

import logging

from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.vitess.terms_repository import TermsRepository
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.entitybase.response import (
    EntityResponse,
    EntityRevisionResponse,
)
from models.rest_api.entitybase.response.entity import EntityState
from models.rest_api.entitybase.response.entity import EntityHistoryEntry
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityReadHandler:
    """Handler for entity read operations"""

    @staticmethod
    def get_entity(
        entity_id: str,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
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
            data = revision.content.get("entity", {}).copy()

            terms_repo = TermsRepository(vitess_client.connection_manager)

            # Load metadata from Vitess/S3
            if fetch_metadata:
                # Reconstruct labels from per-language hashes (Vitess)
                labels_hashes = revision.content.get("labels_hashes", {})
                if labels_hashes:
                    data["labels"] = {}
                    for lang, hash_value in labels_hashes.items():
                        label_value = terms_repo.get_term(hash_value)
                        if label_value is not None:
                            data["labels"][lang] = {
                                "language": lang,
                                "value": label_value,
                            }

                # Reconstruct descriptions from per-language hashes (S3)
                descriptions_hashes = revision.content.get("descriptions_hashes", {})
                if descriptions_hashes:
                    data["descriptions"] = {}
                    for lang, hash_value in descriptions_hashes.items():
                        desc_value = s3_client.load_metadata("descriptions", hash_value)
                        data["descriptions"][lang] = {
                            "language": lang,
                            "value": desc_value,
                        }

                # Reconstruct aliases from per-language hash arrays (Vitess)
                aliases_hashes = revision.content.get("aliases_hashes", {})
                if aliases_hashes:
                    data["aliases"] = {}
                    for lang, hash_list in aliases_hashes.items():
                        data["aliases"][lang] = []
                        for hash_value in hash_list:
                            alias_value = terms_repo.get_term(hash_value)
                            if alias_value is not None:
                                data["aliases"][lang].append(
                                    {"language": lang, "value": alias_value}
                                )
            else:
                # For legacy compatibility, merge metadata into entity data
                entity_data = data["entity"]
                labels_hashes = revision.content.get("labels_hashes", {})
                if labels_hashes:
                    entity_data["labels"] = {}
                    for lang, hash_value in labels_hashes.items():
                        label_value = terms_repo.get_term(hash_value)
                        if label_value is not None:
                            entity_data["labels"][lang] = {
                                "language": lang,
                                "value": label_value,
                            }

                descriptions_hashes = revision.content.get("descriptions_hashes", {})
                if descriptions_hashes:
                    entity_data["descriptions"] = {}
                    for lang, hash_value in descriptions_hashes.items():
                        desc_value = s3_client.load_metadata("descriptions", hash_value)
                        entity_data["descriptions"][lang] = {
                            "language": lang,
                            "value": desc_value,
                        }

                aliases_hashes = revision.content.get("aliases_hashes", {})
                if aliases_hashes:
                    entity_data["aliases"] = {}
                    for lang, hash_list in aliases_hashes.items():
                        entity_data["aliases"][lang] = []
                        for hash_value in hash_list:
                            alias_value = terms_repo.get_term(hash_value)
                            if alias_value is not None:
                                entity_data["aliases"][lang].append(
                                    {"language": lang, "value": alias_value}
                                )

            response = EntityResponse(
                id=entity_id,
                rev_id=head_revision_id,
                data=data,
                state=EntityState(
                    sp=revision.content.get("is_semi_protected", False),
                    is_locked=revision.content.get("is_locked", False),
                    archived=revision.content.get("is_archived", False),
                    dangling=revision.content.get("is_dangling", False),
                    mep=revision.content.get("is_mass_edit_protected", False),
                ),
            )
            if not isinstance(response, EntityResponse):
                raise_validation_error("Invalid response type", status_code=500)
            return response
        except Exception as e:
            logger.error(f"Failed to read entity {entity_id}: {e}")
            raise_validation_error("Failed to read entity", status_code=500)

    @staticmethod
    def get_entity_history(  # type: ignore[return,func-returns-value]
        entity_id: str,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        limit: int = 20,
        offset: int = 0,
    ) -> list[EntityHistoryEntry]:
        """Get entity revision history."""
        if vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        try:
            return vitess_client.get_entity_history(entity_id, s3_client, limit, offset)  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to get entity history for {entity_id}: {e}")
            raise_validation_error("Failed to get entity history", status_code=500)

    @staticmethod
    def get_entity_revision(  # type: ignore[return]
        entity_id: str,
        revision_id: int,
        s3_client: MyS3Client,
    ) -> EntityRevisionResponse:
        """Get specific entity revision."""
        if s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        try:
            revision = s3_client.read_revision(entity_id, revision_id)
            data = revision.data.model_dump()
            entity_data = revision.data.entity.model_copy()

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
                revision_data=data,
            )
        except Exception as e:
            logger.error(
                f"Failed to read revision {revision_id} for entity {entity_id}: {e}"
            )
            raise_validation_error("Revision not found", status_code=404)
