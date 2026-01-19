"""Entity validation service."""

import logging
from typing import Any, Dict

from pydantic import BaseModel

from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.vitess.vitess_client import VitessClient
from models.rest_api.entitybase.response import EntityResponse
from models.rest_api.entitybase.response.entity import EntityState
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityValidationService(BaseModel):
    """Service for entity validation operations."""

    def validate_protection_settings(
        self,
        entity_id: str,
        is_mass_edit: bool | None,
        is_not_autoconfirmed_user: bool | None,
        vitess_client: VitessClient,
    ) -> None:
        """Validate protection settings."""
        if is_mass_edit and is_not_autoconfirmed_user:
            if vitess_client.is_entity_semi_protected(entity_id):
                raise_validation_error(
                    "Semi-protected entity cannot be mass edited", status_code=403
                )

    def validate_idempotency(
        self,
        entity_id: str,
        head_revision_id: int,
        content_hash: int,
        request_data: Dict[str, Any],
        s3_client: MyS3Client,
    ) -> EntityResponse | None:
        """Check if request is idempotent."""
        if head_revision_id == 0:
            return None

        logger.debug(f"Checking idempotency against head revision {head_revision_id}")
        try:
            head_revision = s3_client.read_revision(entity_id, head_revision_id)
            head_content_hash = head_revision.data.get("content_hash")
            logger.debug(f"Head revision content hash: {head_content_hash}")

            if head_content_hash == content_hash:
                logger.debug(
                    f"Content unchanged, returning existing revision {head_revision_id}"
                )
                return EntityResponse(
                    id=entity_id,
                    rev_id=head_revision_id,
                    data=head_revision.entity,
                    state=EntityState(
                        sp=head_revision.data.get("is_semi_protected", False),
                        locked=head_revision.data.get("is_locked", False),
                        archived=head_revision.data.get("is_archived", False),
                        dangling=head_revision.data.get("is_dangling", False),
                        mep=head_revision.data.get("is_mass_edit_protected", False),
                    ),
                )
        except Exception as e:
            logger.warning(f"Failed to read head revision for idempotency check: {e}")

        return None