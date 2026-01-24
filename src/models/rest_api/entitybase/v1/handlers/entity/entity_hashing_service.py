"""Entity hashing service."""

import logging
from typing import Any, Dict

from models.common import raise_validation_error
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes

from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.service import Service
from models.rest_api.entitybase.v1.services.hash_service import HashService

logger = logging.getLogger(__name__)


class EntityHashingService(Service):
    """Service for handling entity data hashing operations."""

    async def hash_statements(
        self, request_data: Dict[str, Any]
    ) -> StatementHashResult:
        """Hash entity statements."""
        hash_operation = HashService(state=self.state).hash_entity_statements(
            request_data
        )
        if not hash_operation.success:
            raise_validation_error(
                hash_operation.error or "Failed to hash statements"
            )
        return hash_operation.data

    async def hash_terms(
        self,
        request_data: Dict[str, Any],
    ) -> HashMaps:
        """Hash entity terms (labels, descriptions, aliases)."""
        service = HashService(state=self.state)
        labels_hashes = service.hash_labels(request_data.get("labels", {}))
        descriptions_hashes = service.hash_descriptions(
            request_data.get("descriptions", {})
        )
        aliases_hashes = service.hash_aliases(request_data.get("aliases", {}))

        return HashMaps(
            labels=labels_hashes,
            descriptions=descriptions_hashes,
            aliases=aliases_hashes,
        )

    async def hash_sitelinks(self, request_data: Dict[str, Any]) -> SitelinksHashes:
        """Hash entity sitelinks."""
        return HashService(state=self.state).hash_sitelinks(
            request_data.get("sitelinks", {})
        )
