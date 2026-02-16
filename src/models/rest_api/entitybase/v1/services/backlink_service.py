"""Service for extracting and managing entity backlinks."""

import logging
from typing import Any

from models.data.common import OperationResult
from models.internal_representation.statement_backlink_extractor import (
    StatementBacklinkExtractor,
)
from models.rest_api.entitybase.v1.service import Service

logger = logging.getLogger(__name__)


class BacklinkService(Service):
    """Service for extracting and storing backlinks from entity statements."""

    def extract_backlinks_from_entity(
        self,
        entity_id: str,
        claims: dict[str, list[dict[str, Any]]],
    ) -> list[tuple[int, int, str, str, str]]:
        """Extract backlinks from entity statements.

        Args:
            entity_id: The entity ID (e.g., "Q1")
            claims: Dictionary of property -> statements

        Returns:
            List of (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank) tuples
        """
        logger.debug(f"Extracting backlinks from entity {entity_id}")

        referencing_internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not referencing_internal_id:
            logger.warning(f"Could not resolve internal ID for entity {entity_id}")
            return []

        backlinks = []

        for property_id, statement_list in claims.items():
            for statement in statement_list:
                extracted = StatementBacklinkExtractor.extract_backlink_data(statement)
                for referenced_entity_id, prop_id, rank in extracted:
                    referenced_internal_id = self.vitess_client.id_resolver.resolve_id(
                        referenced_entity_id
                    )
                    if not referenced_internal_id:
                        logger.debug(
                            f"Skipping backlink: could not resolve {referenced_entity_id}"
                        )
                        continue

                    statement_hash = str(
                        hash(
                            f"{referencing_internal_id}:{referenced_internal_id}:{property_id}"
                        )
                    )

                    backlinks.append(
                        (
                            referenced_internal_id,
                            referencing_internal_id,
                            statement_hash,
                            property_id,
                            rank,
                        )
                    )

        logger.info(f"Extracted {len(backlinks)} backlinks from entity {entity_id}")
        return backlinks

    def extract_and_store_backlinks(
        self,
        entity_id: str,
        claims: dict[str, list[dict[str, Any]]],
    ) -> OperationResult:
        """Extract backlinks from entity statements and store them.

        Args:
            entity_id: The entity ID (e.g., "Q1")
            claims: Dictionary of property -> statements

        Returns:
            OperationResult indicating success or failure
        """
        logger.info(f"Extracting and storing backlinks for entity {entity_id}")

        backlinks = self.extract_backlinks_from_entity(entity_id, claims)

        if not backlinks:
            logger.debug(f"No backlinks found for entity {entity_id}")
            return OperationResult(success=True)

        result: OperationResult = (
            self.vitess_client.backlink_repository.insert_backlinks(backlinks)
        )

        if result.success:
            logger.info(
                f"Successfully stored {len(backlinks)} backlinks for {entity_id}"
            )
        else:
            logger.error(f"Failed to store backlinks for {entity_id}: {result.error}")

        return result
