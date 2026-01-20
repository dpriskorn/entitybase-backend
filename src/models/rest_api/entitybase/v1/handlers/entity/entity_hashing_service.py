"""Entity hashing service."""

import logging
from typing import Any, Dict

from pydantic import BaseModel

from models.infrastructure.s3.hashes.hash_maps import (
    HashMaps,
    SitelinksHashes,
)
from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.vitess.client import VitessClient
from models.rest_api.entitybase.v1.handlers.entity.exceptions import EntityProcessingError
from models.rest_api.entitybase.v1.response import StatementHashResult
from models.rest_api.entitybase.v1.services.hash_service import HashService
from models.rest_api.entitybase.v1.services.statement_service import hash_entity_statements

logger = logging.getLogger(__name__)


class EntityHashingService(BaseModel):
    """Service for handling entity data hashing operations."""

    async def hash_statements(
        self, request_data: Dict[str, Any]
    ) -> StatementHashResult:
        """Hash entity statements."""
        hash_operation = hash_entity_statements(request_data)
        if not hash_operation.success:
            raise EntityProcessingError(
                hash_operation.error or "Failed to hash statements"
            )
        return hash_operation.data

    async def hash_terms(
        self,
        request_data: Dict[str, Any],
        s3_client: MyS3Client,
        vitess_client: VitessClient,
    ) -> HashMaps:
        """Hash entity terms (labels, descriptions, aliases)."""
        labels_hashes = HashService.hash_labels(
            request_data.get("labels", {}), s3_client, vitess_client
        )
        descriptions_hashes = HashService.hash_descriptions(
            request_data.get("descriptions", {}), s3_client, vitess_client
        )
        aliases_hashes = HashService.hash_aliases(
            request_data.get("aliases", {}), s3_client, vitess_client
        )

        return HashMaps(
            labels=labels_hashes,
            descriptions=descriptions_hashes,
            aliases=aliases_hashes,
        )

    async def hash_sitelinks(
        self, request_data: Dict[str, Any], s3_client: MyS3Client
    ) -> SitelinksHashes:
        """Hash entity sitelinks."""
        return HashService.hash_sitelinks(request_data.get("sitelinks", {}), s3_client)
