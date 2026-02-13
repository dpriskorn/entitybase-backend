"""Repository for managing users in Vitess."""

import json
import logging
from typing import Any, List

from models.data.common import OperationResult
from models.infrastructure.vitess.repository import Repository
from models.data.rest_api.v1.entitybase.request import UserActivityType
from models.data.rest_api.v1.entitybase.request.entity.context import (
    GeneralStatisticsContext,
)
from models.data.rest_api.v1.entitybase.response import UserResponse
from models.data.rest_api.v1.entitybase.response import (
    UserActivityItemResponse,
)
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class UserRepository(Repository):
    """Repository for managing users in Vitess."""

    def create_user(self, user_id: int) -> OperationResult:
        """Create a new user record if it does not exist (idempotent).

        Inserts a user into the users table. If the user already exists, the operation
        succeeds without changes due to the ON DUPLICATE KEY clause.

        Args:
            user_id: The unique ID of the user to create. Must be positive.

        Returns:
            OperationResult: Indicates success or failure. On success, success=True.
                On failure (e.g., database error), success=False with an error message.
        """
        try:
            with self.vitess_client.cursor as cursor:
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
        """Check if a user exists in the database.

        Queries the users table to determine if a record exists for the given user ID.

        Args:
            user_id: The ID of the user to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "SELECT 1 FROM users WHERE user_id = %s",
                (user_id,),
            )
            return cursor.fetchone() is not None

    def get_user(self, user_id: int) -> UserResponse | None:
        """Get user data by ID."""

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                "SELECT user_id, created_at, preferences FROM users WHERE user_id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                try:
                    user = UserResponse(
                        user_id=row[0],
                        created_at=row[1],
                        preferences=row[2],
                    )
                    logger.debug(
                        f"Successfully created UserResponse for user_id={user_id}"
                    )
                    return user
                except Exception as e:
                    logger.error(f"Failed to create UserResponse from row {row}: {e}")
                    raise_validation_error(f"Invalid user data: {e}", status_code=400)
            return None

    def update_user_activity(self, user_id: int) -> OperationResult:
        """Update user's last activity timestamp."""
        if user_id <= 0:
            return OperationResult(success=False, error="Invalid user ID")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "UPDATE users SET last_activity = NOW() WHERE user_id = %s",
                    (user_id,),
                )
                return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def is_watchlist_enabled(self, user_id: int) -> bool:
        """Check if watchlist is enabled for user."""

        with self.vitess_client.cursor as cursor:
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
            with self.vitess_client.cursor as cursor:
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
        activity_type: UserActivityType,
        entity_id: str,
        revision_id: int = 0,
    ) -> OperationResult:
        """Log a user activity for tracking interactions with entities.

        Inserts a record into the user_activity table to record user actions
        such as edits, views, or other interactions on entities.

        Note:
            Basic validation is performed on user_id and activity_type before insertion.
            Database errors (e.g., connection issues) are caught and returned as failures.
        """
        logger.debug(
            f"Logging user activity: user_id={user_id}, activity_type={activity_type}, "
            f"entity_id={entity_id}, revision_id={revision_id}"
        )
        if user_id <= 0 or not activity_type:
            return OperationResult(
                success=False, error="Invalid user ID or activity type"
            )

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    """
                    INSERT INTO user_activity (user_id, activity_type, entity_id, revision_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, activity_type.value, entity_id, revision_id),
                )
                return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_user_preferences(self, user_id: int = 0) -> OperationResult:
        """Get user notification preferences."""
        if user_id <= 0:
            return OperationResult(success=False, error="Invalid user ID")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "SELECT notification_limit, retention_hours FROM users WHERE user_id = %s",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row:
                    prefs = {
                        "notification_limit": row[0],
                        "retention_hours": row[1],
                    }
                    return OperationResult(success=True, data=prefs)
                return OperationResult(
                    success=False, error="User preferences not found"
                )
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def update_user_preferences(
        self,
        notification_limit: int,
        retention_hours: int,
        user_id: int = 0,
    ) -> OperationResult:
        """Update user notification preferences."""
        if user_id <= 0:
            return OperationResult(success=False, error="Invalid user ID")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    "UPDATE users SET notification_limit = %s, retention_hours = %s WHERE user_id = %s",
                    (notification_limit, retention_hours, user_id),
                )
                return OperationResult(success=True)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def get_user_activities(
        self,
        user_id: int,
        activity_type: UserActivityType | None = None,
        hours: int = 24,
        limit: int = 50,
        offset: int = 0,
    ) -> OperationResult:
        """Get user's activities with filtering."""
        errors = []
        if user_id <= 0:
            errors.append("user_id must be positive")
        if hours <= 0:
            errors.append("hours must be positive")
        if limit <= 0:
            errors.append("limit must be positive")
        if offset < 0:
            errors.append("offset must be non-negative")
        if errors:
            return OperationResult(success=False, error="; ".join(errors))

        try:
            logger.debug(
                f"Getting activities for user {user_id}, type {activity_type}, hours {hours}"
            )

            with self.vitess_client.cursor as cursor:
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
                        UserActivityItemResponse(
                            id=row[0],
                            user_id=row[1],
                            activity_type=row[2],
                            entity_id=row[3],
                            revision_id=row[4],
                            created_at=row[5],
                        )
                    )

                return OperationResult(success=True, data=activities)
        except Exception as e:
            return OperationResult(success=False, error=str(e))

    def insert_general_statistics(self, ctx: GeneralStatisticsContext) -> None:
        """Insert daily general statistics.

        Raises:
            ValueError: If input validation fails
            Exception: If database operation fails
        """
        # Input validation
        if not isinstance(ctx.date, str) or len(ctx.date) != 10:
            raise_validation_error(
                f"Invalid date format: {ctx.date}. Expected YYYY-MM-DD", status_code=400
            )
        for name, value in [
            ("total_statements", ctx.total_statements),
            ("total_qualifiers", ctx.total_qualifiers),
            ("total_references", ctx.total_references),
            ("total_items", ctx.total_items),
            ("total_lexemes", ctx.total_lexemes),
            ("total_properties", ctx.total_properties),
            ("total_sitelinks", ctx.total_sitelinks),
            ("total_terms", ctx.total_terms),
        ]:
            if value < 0:
                raise_validation_error(
                    f"{name} must be non-negative: {value}",
                    status_code=400,
                )

        logger.debug(f"Inserting general statistics for date {ctx.date}")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    """
                    INSERT INTO general_daily_stats
                    (stat_date, total_statements, total_qualifiers, total_references, total_items, total_lexemes, total_properties, total_sitelinks, total_terms, terms_per_language, terms_by_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    total_statements = VALUES(total_statements),
                    total_qualifiers = VALUES(total_qualifiers),
                    total_references = VALUES(total_references),
                    total_items = VALUES(total_items),
                    total_lexemes = VALUES(total_lexemes),
                    total_properties = VALUES(total_properties),
                    total_sitelinks = VALUES(total_sitelinks),
                    total_terms = VALUES(total_terms),
                    terms_per_language = VALUES(terms_per_language),
                    terms_by_type = VALUES(terms_by_type)
                    """,
                    (
                        ctx.date,
                        ctx.total_statements,
                        ctx.total_qualifiers,
                        ctx.total_references,
                        ctx.total_items,
                        ctx.total_lexemes,
                        ctx.total_properties,
                        ctx.total_sitelinks,
                        ctx.total_terms,
                        json.dumps(ctx.terms_per_language),
                        json.dumps(ctx.terms_by_type),
                    ),
                )
                logger.info(f"Successfully stored general statistics for {ctx.date}")
        except Exception as e:
            logger.error(f"Failed to insert general statistics for {ctx.date}: {e}")
            raise

    def insert_user_statistics(
        self,
        date: str,
        total_users: int,
        active_users: int,
    ) -> None:
        """Insert daily user statistics.

        Raises:
            ValueError: If input validation fails
            Exception: If database operation fails
        """
        # Input validation
        if not isinstance(date, str) or len(date) != 10:
            raise_validation_error(
                f"Invalid date format: {date}. Expected YYYY-MM-DD", status_code=400
            )
        if total_users < 0:
            raise_validation_error(
                f"total_users must be non-negative: {total_users}",
                status_code=400,
            )
        if active_users < 0:
            raise_validation_error(
                f"active_users must be non-negative: {active_users}",
                status_code=400,
            )

        logger.debug(f"Inserting user statistics for date {date}")

        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    """
                    INSERT INTO user_daily_stats
                    (stat_date, total_users, active_users)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    total_users = VALUES(total_users),
                    active_users = VALUES(active_users)
                    """,
                    (
                        date,
                        total_users,
                        active_users,
                    ),
                )
                logger.info(f"Successfully stored user statistics for {date}")
        except Exception as e:
            logger.error(f"Failed to insert user statistics for {date}: {e}")
            raise
