"""Repository for managing watchlists in Vitess."""

import json
from typing import Any, List

from models.watchlist import WatchlistEntry


class WatchlistRepository:
    """Repository for managing watchlists in Vitess."""

    def __init__(self, connection_manager: Any, id_resolver: Any) -> None:
        self.connection_manager = connection_manager
        self.id_resolver = id_resolver

    def get_entity_watch_count(self, user_id: int) -> int:
        """Get count of entity watches (whole entity, no properties) for user."""
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM watchlist WHERE user_id = %s AND watched_properties IS NULL",
                    (user_id,),
                )
                return int(cursor.fetchone()[0])

    def get_property_watch_count(self, user_id: int) -> int:
        """Get count of entity-property watches (with properties) for user."""
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM watchlist WHERE user_id = %s AND watched_properties IS NOT NULL",
                    (user_id,),
                )
                return int(cursor.fetchone()[0])

    def add_watch(
        self, user_id: int, entity_id: str, properties: List[str] | None
    ) -> None:
        """Add a watchlist entry."""
        internal_entity_id = self.id_resolver.resolve_id(self._get_conn(), entity_id)
        properties_json = ",".join(properties) if properties else None

        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO watchlist (user_id, internal_entity_id, watched_properties)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE watched_properties = VALUES(watched_properties)
                    """,
                    (user_id, internal_entity_id, properties_json),
                )

    def remove_watch(
        self, user_id: int, entity_id: str, properties: List[str] | None
    ) -> None:
        """Remove a watchlist entry."""
        internal_entity_id = self.id_resolver.resolve_id(self._get_conn(), entity_id)
        properties_json = ",".join(properties) if properties else None

        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM watchlist
                    WHERE user_id = %s AND internal_entity_id = %s AND watched_properties <=> %s
                    """,
                    (user_id, internal_entity_id, properties_json),
                )

    def get_watches_for_user(self, user_id: int) -> List[dict]:
        """Get all watchlist entries for a user."""
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT internal_entity_id, watched_properties
                    FROM watchlist
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()

        watches = []
        for row in rows:
            internal_entity_id, properties_json = row
            entity_id = self.id_resolver.resolve_entity_id(conn, internal_entity_id)
            properties = properties_json.split(",") if properties_json else None
            watches.append({"entity_id": entity_id, "properties": properties})

        return watches

    def get_watchers_for_entity(self, entity_id: str) -> List[dict]:
        """Get all watchers for an entity (for notifications)."""
        internal_entity_id = self.id_resolver.resolve_id(self._get_conn(), entity_id)

        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_id, watched_properties
                    FROM watchlist
                    WHERE internal_entity_id = %s
                    """,
                    (internal_entity_id,),
                )
                rows = cursor.fetchall()

        watchers = []
        for row in rows:
            user_id, properties_json = row
            properties = properties_json.split(",") if properties_json else None
            watchers.append({"user_id": user_id, "properties": properties})

        return watchers

    def get_notification_count(self, user_id: int) -> int:
        """Get count of active notifications for user."""
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM user_notifications WHERE user_id = %s",
                    (user_id,),
                )
                return int(cursor.fetchone()[0])

    def get_user_notifications(
        self, user_id: int, hours: int = 24, limit: int = 50, offset: int = 0
    ) -> List[dict]:
        """Get recent notifications for a user within time span."""
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, entity_id, revision_id, change_type, changed_properties,
                           event_timestamp, is_checked, checked_at
                    FROM user_notifications
                    WHERE user_id = %s AND event_timestamp >= NOW() - INTERVAL %s HOUR
                    ORDER BY event_timestamp DESC
                    LIMIT %s OFFSET %s
                    """,
                    (user_id, hours, limit, offset),
                )
                rows = cursor.fetchall()

        notifications = []
        for row in rows:
            notifications.append(
                {
                    "id": row[0],
                    "entity_id": row[1],
                    "revision_id": row[2],
                    "change_type": row[3],
                    "changed_properties": json.loads(row[4]) if row[4] else None,
                    "event_timestamp": row[5],
                    "is_checked": bool(row[6]),
                    "checked_at": row[7],
                }
            )

        return notifications

    def mark_notification_checked(self, notification_id: int, user_id: int) -> None:
        """Mark a notification as checked."""
        with self._get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE user_notifications
                    SET is_checked = TRUE, checked_at = NOW()
                    WHERE id = %s AND user_id = %s
                    """,
                    (notification_id, user_id),
                )

    def _get_conn(self) -> Any:
        """Get database connection."""
        return self.connection_manager.connect()
