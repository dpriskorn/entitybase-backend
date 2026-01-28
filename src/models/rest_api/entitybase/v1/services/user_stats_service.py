"""Service for computing user statistics."""

import logging

from models.data.rest_api.v1.entitybase.response import UserStatsData
from models.rest_api.entitybase.v1.service import Service

logger = logging.getLogger(__name__)


class UserStatsService(Service):
    """Service for computing user statistics."""

    def compute_daily_stats(self) -> UserStatsData:
        """Compute comprehensive user statistics for current date."""
        total_users = self.get_total_users()
        active_users = self.get_active_users()

        return UserStatsData(
            total=total_users,
            active=active_users,
        )

    def get_total_users(self) -> int:
        """Count total users."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_active_users(self) -> int:
        """Count active users (active in last 30 days)."""
        cursor = self.state.vitess_client.cursor
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE last_activity >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        )
        result = cursor.fetchone()
        return result[0] if result else 0
