"""Service for computing user statistics."""

import logging

from pydantic import BaseModel

from models.infrastructure.vitess.client import VitessClient
from models.rest_api.entitybase.v1.response.misc import UserStatsData
from models.rest_api.entitybase.v1.service import Service

logger = logging.getLogger(__name__)


class UserStatsService(Service):
    """Service for computing user statistics."""

    def compute_daily_stats(self: VitessClient) -> UserStatsData:
        """Compute comprehensive user statistics for current date."""
        total_users = self.get_total_users()
        active_users = self.get_active_users()

        return UserStatsData(
            total=total_users,
            active=active_users,
        )

    def get_total_users(self) -> int:
        """Count total users."""
        with self.state.vitess_client.connection_manager.get_connection() as _:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM users")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_active_users(self) -> int:
        """Count active users (active in last 30 days)."""
        with self.state.vitess_client.connection_manager.get_connection() as _:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE last_activity >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
                )
                result = cursor.fetchone()
                return result[0] if result else 0
