"""Entity read and retrieval handlers."""

import logging

from models.data.infrastructure.s3.entity_state import EntityState
from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.response import (
    EntityRevisionResponse,
)
from models.data.rest_api.v1.entitybase.response import EntityHistoryEntry
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityReadHandler(Handler):
    """Handler for entity read operations"""

    def get_entity(
        self,
        entity_id: str,
    ) -> EntityResponse:
        """Get entity by ID."""
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity not found", status_code=404)

        try:
            revision = self.state.s3_client.read_revision(entity_id, head_revision_id)
            data = revision.revision

            # Resolve terms
            if "labels_hashes" in data:
                resolved_labels = {}
                for lang, hash_val in data["labels_hashes"].items():
                    text = self.state.s3_client.load_term_metadata(hash_val)
                    resolved_labels[lang] = {"language": lang, "value": text}
                data["labels"] = resolved_labels
            if "descriptions_hashes" in data:
                resolved_descriptions = {}
                for lang, hash_val in data["descriptions_hashes"].items():
                    text = self.state.s3_client.load_term_metadata(hash_val)
                    resolved_descriptions[lang] = {"language": lang, "value": text}
                data["descriptions"] = resolved_descriptions
            if "aliases_hashes" in data:
                resolved_aliases = {}
                for lang, hashes in data["aliases_hashes"].items():
                    resolved_aliases[lang] = [{"language": lang, "value": self.state.s3_client.load_term_metadata(h)} for h in hashes]
                data["aliases"] = resolved_aliases

            # Resolve sitelinks
            if "sitelinks" in data:
                resolved_sitelinks = {}
                for wiki, sitelink in data["sitelinks"].items():
                    title = self.state.s3_client.load_sitelink_metadata(sitelink["title_hash"])
                    resolved_sitelinks[wiki] = {"site": wiki, "title": title, "badges": sitelink["badges"]}
                data["sitelinks"] = resolved_sitelinks

            response = EntityResponse(
                id=entity_id,
                rev_id=head_revision_id,
                data=data,
                state=EntityState(
                    sp=data.get("is_semi_protected", False),
                    locked=data.get("is_locked", False),
                    archived=data.get("is_archived", False),
                    dangling=data.get("is_dangling", False),
                    mep=data.get("is_mass_edit_protected", False),
                ),
            )
            return response
        except Exception as e:
            logger.error(f"Failed to read entity {entity_id}: {e}")
            raise_validation_error(f"Failed to read entity {entity_id}: {type(e).__name__}: {str(e)}", status_code=500)

    def get_entity_history(
        self,  # type: ignore[return,func-returns-value]
        entity_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[EntityHistoryEntry]:
        """Get entity revision history."""
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        try:
            return self.state.vitess_client.get_entity_history(entity_id, limit, offset)  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to get entity history for {entity_id}: {e}")
            raise_validation_error(f"Failed to get entity history: {type(e).__name__}: {str(e)}", status_code=500)

    def get_entity_revision(
        self,  # type: ignore[return]
        entity_id: str,
        revision_id: int,
    ) -> EntityRevisionResponse:
        """Get specific entity revision."""
        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        try:
            revision = self.state.s3_client.read_revision(entity_id, revision_id)
            revision_data = revision.revision
            return EntityRevisionResponse(
                entity_id=entity_id,
                revision_id=revision_id,
                revision_data=revision_data,
            )
        except Exception as e:
            logger.error(
                f"Failed to read revision {revision_id} for entity {entity_id}: {e}"
            )
            raise_validation_error(f"Failed to read revision: {type(e).__name__}: {str(e)}", status_code=404)
