"""Vitess revision repository for revision operations."""

import json
import logging
from typing import Any

from models.common import OperationResult
from models.data.infrastructure.vitess.records.revision import (
    HistoryRevisionItemRecord,
    RevisionRecord,
)
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.vitess.repository import Repository
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class RevisionRepository(Repository):
    """Repository for entity revision database operations."""

    def insert(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: RevisionData,
    ) -> None:
        """Insert a new revision for an entity."""
        logger.debug(f"Inserting revision {revision_id} for entity {entity_id}")
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        is_mass_edit = entity_data.edit.is_mass_edit
        edit_type = entity_data.edit.edit_type
        statements = entity_data.hashes.statements.model_dump(mode="json") if entity_data.hashes and entity_data.hashes.statements else []
        properties = entity_data.properties.model_dump(mode="json") if entity_data.properties else {}
        property_counts = entity_data.property_counts.model_dump(mode="json") if entity_data.property_counts else {}
        labels_hashes = entity_data.hashes.labels.model_dump(mode="json") if entity_data.hashes and entity_data.hashes.labels else {}
        descriptions_hashes = entity_data.hashes.descriptions.model_dump(mode="json") if entity_data.hashes and entity_data.hashes.descriptions else {}
        aliases_hashes = entity_data.hashes.aliases.model_dump(mode="json") if entity_data.hashes and entity_data.hashes.aliases else {}
        sitelinks_hashes = entity_data.hashes.sitelinks.model_dump(mode="json") if entity_data.hashes and entity_data.hashes.sitelinks else {}
        user_id = entity_data.edit.user_id
        edit_summary = entity_data.edit.edit_summary

        cursor = self.vitess_client.cursor
        cursor.execute(
                "INSERT INTO entity_revisions (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts, labels_hashes, descriptions_hashes, aliases_hashes, sitelinks_hashes, user_id, edit_summary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    internal_id,
                    revision_id,
                    is_mass_edit,
                    edit_type,
                    json.dumps(statements or []),
                    json.dumps(properties or []),
                    property_counts,
                    labels_hashes,
                    descriptions_hashes,
                    aliases_hashes,
                    sitelinks_hashes,
                    user_id,
                    edit_summary,
                ),
            )

    def get_revision(
        self, internal_entity_id: int, revision_id: int, vitess_client: Any
    ) -> RevisionRecord | None:
        """Get a specific revision data."""
        logger.debug(f"Getting revision {revision_id} for entity {internal_entity_id}")
        with vitess_client.get_connection() as _:
            cursor = self.vitess_client.cursor
            cursor.execute(
                "SELECT statements, properties, property_counts, labels_hashes, descriptions_hashes, aliases_hashes, sitelinks_hashes FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
                (internal_entity_id, revision_id),
            )
            row = cursor.fetchone()
            if row:
                return RevisionRecord.model_validate(
                    {
                        "statements": json.loads(row[0]) if row[0] else [],
                        "properties": json.loads(row[1]) if row[1] else [],
                        "property_counts": json.loads(row[2]) if row[2] else {},
                        "labels_hashes": json.loads(row[3]) if row[3] else {},
                        "descriptions_hashes": json.loads(row[4]) if row[4] else {},
                        "aliases_hashes": json.loads(row[5]) if row[5] else {},
                        "sitelinks_hashes": json.loads(row[6]) if row[6] else {},
                    }
                )
            return None

    def get_history(
        self, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        """Get revision history for an entity."""
        logger.debug(f"Getting history for entity {entity_id}, limit {limit}")

        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return []

        cursor = self.vitess_client.cursor
        cursor.execute(
                "SELECT revision_id, created_at, user_id, edit_summary FROM entity_revisions WHERE internal_id = %s ORDER BY revision_id DESC LIMIT %s OFFSET %s",
                (internal_id, limit, offset),
            )
        result = [
            HistoryRevisionItemRecord(
                revision_id=row[0],
                created_at=row[1].isoformat() if row[1] else "",
                user_id=row[2],
                edit_summary=row[3] or "",
            )
            for row in cursor.fetchall()
        ]
        return result

    def delete(self, entity_id: str, revision_id: int) -> OperationResult:
        """Delete a revision (for rollback)."""
        logger.debug(f"Deleting revision {revision_id} for entity {entity_id}")
        if not self.connection_manager.connection:
            return OperationResult(
                success=False, error="Database connection not provided"
            )
        if not entity_id:
            return OperationResult(success=False, error="Entity ID is required")
        if revision_id <= 0:
            return OperationResult(success=False, error="Invalid revision ID")
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return OperationResult(success=False, error="Entity not found")
        cursor = self.vitess_client.cursor
        cursor.execute(
            "DELETE FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
            (internal_id, revision_id),
        )
        # Also delete from entity_head if it's the head
        cursor.execute(
            "UPDATE entity_head SET head_revision_id = head_revision_id - 1 WHERE internal_id = %s AND head_revision_id = %s",
            (internal_id, revision_id),
        )
        return OperationResult(success=True)

    def create_with_cas(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: RevisionData,
        expected_revision_id: int,
    ) -> bool:
        """Create a revision with compare-and-swap semantics."""
        logger.debug(
            f"Creating revision {revision_id} for entity {entity_id} with CAS, expected {expected_revision_id}"
        )
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            return False

        cursor = self.vitess_client.cursor
        cursor.execute(
                """INSERT INTO entity_revisions 
                        (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    internal_id,
                    revision_id,
                    entity_data.edit.is_mass_edit,
                    entity_data.edit.edit_type,
                    json.dumps(entity_data.hashes.statements.root if entity_data.hashes else []),
                    json.dumps(entity_data.properties),
                    entity_data.property_counts.model_dump(mode="json") if entity_data.property_counts else {},
                ),
            )

        cursor.execute(
                """UPDATE entity_head
                   SET head_revision_id = %s,
                        is_semi_protected = %s,
                        is_locked = %s,
                        is_archived = %s,
                        is_dangling = %s,
                        is_mass_edit_protected = %s
                    WHERE internal_id = %s AND head_revision_id = %s""",
            (
                revision_id,
                entity_data.state.is_semi_protected,
                entity_data.state.is_locked,
                entity_data.state.is_archived,
                entity_data.state.is_dangling,
                entity_data.state.is_mass_edit_protected,
                internal_id,
                expected_revision_id,
            ),
        )

        affected_rows = int(cursor.rowcount)
        return affected_rows > 0

    def insert_revision(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: RevisionData,
        expected_revision_id=None,
    ) -> None:
        """Insert a revision from RevisionData model."""
        if expected_revision_id is None:
            self.insert(entity_id, revision_id, entity_data)
        else:
            self.create_with_cas(entity_id, revision_id, entity_data, expected_revision_id)

    def create(self, entity_id: str, revision_id: int, entity_data: RevisionData) -> None:
        """Create a new revision for an entity."""
        logger.debug(f"Creating revision {revision_id} for entity {entity_id}")
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        cursor = self.vitess_client.cursor
        cursor.execute(
            """INSERT INTO entity_revisions 
                    (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                internal_id,
                revision_id,
                entity_data.edit.is_mass_edit,
                entity_data.edit.edit_type,
                json.dumps(entity_data.hashes.statements.root if entity_data.hashes else []),
                json.dumps(entity_data.properties),
                entity_data.property_counts.model_dump(mode="json") if entity_data.property_counts else {},
            ),
        )

        cursor.execute(
            """INSERT INTO entity_head
                   (internal_id, head_revision_id, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                internal_id,
                revision_id,
                entity_data.state.is_semi_protected,
                entity_data.state.is_locked,
                entity_data.state.is_archived,
                entity_data.state.is_dangling,
                entity_data.state.is_mass_edit_protected,
            ),
        )
