"""Repository for managing users in Vitess."""

import logging
from typing import Any, List

from models.common import OperationResult
from models.user import User
from models.user_activity import UserActivityItem

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for managing users in Vitess."""

    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def create_user(self, user_id: int) -> OperationResult:
        """Create a new user if not exists (idempotent)."""
        try:
            with self.connection_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO users (user_id)
                        VALUES (%s)
                        ON DUPLICATE KEY UPDATE user_id = user_id
                        """,
                        (user_id,),
                    )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def user_exists(self, user_id: int) -> bool:
        """Check if user exists."""
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM users WHERE user_id = %s",
                    (user_id,),
                )
                return cursor.fetchone() is not None

    def get_user(self, user_id: int) -> User | None:
        """Get user data by ID."""
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_id, created_at, preferences FROM users WHERE user_id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row:
                    return User(
                        user_id=row[0],
                        created_at=row[1],
                        preferences=row[2],
                    )
                return None

    def update_user_activity(self, user_id: int) -> OperationResult:
        """Update user's last activity timestamp."""
        if user_id <= 0:
            return OperationResult(success=False, error="Invalid user ID")

        try:
            with self.connection_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET last_activity = NOW() WHERE user_id = %s",
                        (user_id,),
                    )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def is_watchlist_enabled(self, user_id: int) -> bool:
        """Check if watchlist is enabled for user."""
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT watchlist_enabled FROM users WHERE user_id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                return bool(row[0]) if row else False

    def set_watchlist_enabled(self, user_id: int, enabled: bool) -> OperationResult:
        """Enable or disable watchlist for user."""
        if user_id <= 0:
            return OperationResult(success=False, error="Invalid user ID")

        try:
            with self.connection_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
                        (enabled, user_id),
                    )
            return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def disable_watchlist(self, user_id: int) -> OperationResult:
        """Disable watchlist for user (idempotent)."""
        return self.set_watchlist_enabled(user_id, False)

    def log_user_activity(
        self,
        user_id: int,
        activity_type: str,
        entity_id: str | None = None,
        revision_id: int | None = None,
    ) -> None:
        """Log a user activity."""
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO user_activity (user_id, activity_type, entity_id, revision_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, activity_type, entity_id, revision_id),
                )

    def get_user_preferences(self, user_id: int) -> Any | None:
        """Get user notification preferences."""
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT notification_limit, retention_hours FROM users WHERE user_id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row:
                    return {"notification_limit": row[0], "retention_hours": row[1]}
                return None

    def update_user_preferences(
        self, user_id: int, notification_limit: int, retention_hours: int
    ) -> None:
        """Update user notification preferences."""
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET notification_limit = %s, retention_hours = %s WHERE user_id = %s",
                    (notification_limit, retention_hours, user_id),
                )

    def get_user_activities(
        self,
        user_id: int,
        activity_type: str | None = None,
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> List[UserActivityItem]:
        """Get user's activities with filtering."""
        logger.debug(
            f"Getting activities for user {user_id}, type {activity_type}, hours {hours}"
        )
        with self.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT id, user_id, activity_type, entity_id, revision_id, created_at
                    FROM user_activity
                    WHERE user_id = %s AND created_at >= NOW() - INTERVAL %s HOUR
                """
                params: List[Any] = [user_id, hours]

                if activity_type:
                    query += " AND activity_type = %s"
                    params.append(activity_type)

                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()

        activities = []
        for row in rows:
            activities.append(
                UserActivityItem(
                    id=row[0],
                    user_id=row[1],
                    activity_type=row[2],
                    entity_id=row[3],
                    revision_id=row[4],
                    created_at=row[5],
                )
            )

        return activities
