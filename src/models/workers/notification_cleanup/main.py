"""Notification cleanup worker for enforcing age and count limits."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

from models.config.settings import settings
from models.infrastructure.vitess.client import VitessClient

logger = logging.getLogger(__name__)


class NotificationCleanupWorker:
    """Worker that periodically cleans up old notifications to enforce limits."""

    def __init__(self) -> None:
        logger = logging.getLogger(__name__)
        self.vitess_client | None = None
        # Configurable limits
        self.max_age_days = 30
        self.max_per_user = 500

    @asynccontextmanager
    async def lifespan(self) -> AsyncGenerator[None, None]:
        """Lifespan context manager for startup/shutdown."""
        try:
            # Initialize client
            vitess_config = settings.to_vitess_config()
            self.vitess_client = VitessClient(vitess_config)
            logger.info("Notification cleanup worker started")
            yield
        except Exception as e:
            logger.error(f"Failed to start notification cleanup worker: {e}")
            raise
        finally:
            logger.info("Notification cleanup worker stopped")

    async def run_cleanup(self) -> None:
        """Run one cleanup cycle."""
        try:
            logger.info("Starting notification cleanup cycle")
            deleted_count = 0

            # 1. Delete notifications older than max_age_days
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.max_age_days)
            age_deleted = self._delete_old_notifications(cutoff_date)
            deleted_count += age_deleted
            logger.info(
                f"Deleted {age_deleted} notifications older than {self.max_age_days} days"
            )

            # 2. Enforce per-user limits
            user_deleted = self._enforce_user_limits()
            deleted_count += user_deleted
            logger.info(
                f"Deleted {user_deleted} excess notifications to enforce {self.max_per_user} per user limit"
            )

            logger.info(
                f"Cleanup cycle complete: {deleted_count} total notifications deleted"
            )

        except Exception as e:
            logger.error(f"Error during cleanup cycle: {e}")

    def _delete_old_notifications(self, cutoff_date: datetime) -> int:
        """Delete notifications older than cutoff date."""
        assert self.vitess_client is not None
        with self.vitess_client.connection_manager.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_notifications WHERE event_timestamp < %s",
                (cutoff_date.isoformat() + "Z",),
            )
            return int(cursor.rowcount)

    def _enforce_user_limits(self) -> int:
        """For each user with > max_per_user notifications, keep only the latest max_per_user."""
        total_deleted = 0

        # Get users with excess notifications
        assert self.vitess_client is not None
        with self.vitess_client.cursor as cursor:
            # Find users with too many notifications
            cursor.execute(
                """
                SELECT user_id, COUNT(*) as count
                FROM user_notifications
                GROUP BY user_id
                HAVING COUNT(*) > %s
                """,
                (self.max_per_user,),
            )
            users_with_excess = cursor.fetchall()

            for user_id, count in users_with_excess:
                # Delete oldest excess notifications
                excess = count - self.max_per_user
                cursor.execute(
                    """
                    DELETE FROM user_notifications
                    WHERE user_id = %s
                    ORDER BY event_timestamp ASC
                    LIMIT %s
                    """,
                    (user_id, excess),
                )
                total_deleted += cursor.rowcount

        return total_deleted


async def main() -> None:
    """Main entry point for the notification cleanup worker."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = NotificationCleanupWorker()

    # noinspection PyArgumentList
    async with worker.lifespan():
        # Run cleanup once (for manual execution or cron)
        await worker.run_cleanup()


if __name__ == "__main__":
    asyncio.run(main())
