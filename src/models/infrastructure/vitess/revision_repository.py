"""Vitess revision repository for revision operations."""

import json
from typing import Any

from pydantic import BaseModel

from models.validation.utils import raise_validation_error


class RevisionRepository:
    """Repository for entity revision database operations."""

    def __init__(self, connection_manager: Any, id_resolver: Any) -> None:
        self.connection_manager = connection_manager
        self.id_resolver = id_resolver

    def insert(
        self,
        entity_id: str,
        revision_id: int,
        data: dict,
    ) -> None:
        """Insert a new revision for an entity."""
        with self.connection_manager.get_connection() as conn:
            internal_id = self.id_resolver.resolve_id(conn, entity_id)
            if not internal_id:
                raise_validation_error(f"Entity {entity_id} not found", status_code=404)

            is_mass_edit = data.get("is_mass_edit", False)
            edit_type = data.get("edit_type", "")
            statements = data.get("statements", [])
            properties = data.get("properties", [])
            property_counts = data.get("property_counts", {})
            labels_hashes = data.get("labels_hashes")
            descriptions_hashes = data.get("descriptions_hashes")
            aliases_hashes = data.get("aliases_hashes")

            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
                    (internal_id, revision_id),
                )
                if cursor.fetchone() is not None:
                    return

                cursor.execute(
                    "INSERT INTO entity_revisions (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts, labels_hashes, descriptions_hashes, aliases_hashes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        internal_id,
                        revision_id,
                        is_mass_edit,
                        edit_type,
                        json.dumps(statements or []),
                        json.dumps(properties or []),
                        json.dumps(property_counts or {}),
                        json.dumps(labels_hashes or {}),
                        json.dumps(descriptions_hashes or {}),
                        json.dumps(aliases_hashes or {}),
                    ),
                )

    def get_history(
        self, conn: Any, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        """Get revision history for an entity."""
        from dataclasses import dataclass

        class RevisionRecord(BaseModel):
            """Revision record for history."""

            revision_id: int
            created_at: str | None

        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return []

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT revision_id, created_at FROM entity_revisions WHERE internal_id = %s ORDER BY revision_id DESC LIMIT %s OFFSET %s",
                (internal_id, limit, offset),
            )
            result = [
                RevisionRecord(
                    revision_id=row[0],
                    created_at=row[1].isoformat() if row[1] else None,
                )
                for row in cursor.fetchall()
            ]
            return result

    def delete(self, conn: Any, entity_id: str, revision_id: int) -> None:
        """Delete a revision (for rollback)."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
                (internal_id, revision_id),
            )
            # Also delete from entity_head if it's the head
            cursor.execute(
                "UPDATE entity_head SET head_revision_id = head_revision_id - 1 WHERE internal_id = %s AND head_revision_id = %s",
                (internal_id, revision_id),
            )

    def create_with_cas(
        self,
        conn: Any,
        entity_id: str,
        revision_id: int,
        data: dict,
        expected_revision_id: int,
    ) -> bool:
        """Create a revision with compare-and-swap semantics."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            return False

        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO entity_revisions 
                        (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    internal_id,
                    revision_id,
                    data.get("is_mass_edit", False),
                    data.get("edit_type", ""),
                    json.dumps(data.get("hashes", [])),
                    json.dumps(data.get("properties", [])),
                    json.dumps(data.get("property_counts", {})),
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
                    data.get("is_semi_protected", False),
                    data.get("is_locked", False),
                    data.get("is_archived", False),
                    data.get("is_dangling", False),
                    data.get("is_mass_edit_protected", False),
                    internal_id,
                    expected_revision_id,
                ),
            )

            affected_rows = int(cursor.rowcount)
            return affected_rows > 0

    def create(self, conn: Any, entity_id: str, revision_id: int, data: dict) -> None:
        """Create a new revision for an entity."""
        internal_id = self.id_resolver.resolve_id(conn, entity_id)
        if not internal_id:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)

        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO entity_revisions 
                        (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    internal_id,
                    revision_id,
                    data.get("is_mass_edit", False),
                    data.get("edit_type", ""),
                    json.dumps(data.get("hashes", [])),
                    json.dumps(data.get("properties", [])),
                    json.dumps(data.get("property_counts", {})),
                ),
            )

            cursor.execute(
                """INSERT INTO entity_head
                       (internal_id, head_revision_id, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    internal_id,
                    revision_id,
                    data.get("is_semi_protected", False),
                    data.get("is_locked", False),
                    data.get("is_archived", False),
                    data.get("is_dangling", False),
                    data.get("is_mass_edit_protected", False),
                ),
            )
