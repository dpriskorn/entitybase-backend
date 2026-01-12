"""Watchlist auto-disable worker for inactive users."""

import sys

sys.path.insert(0, "src")

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from models.config.settings import settings
from models.infrastructure.vitess_client import VitessClient


class WatchlistAutoDisableWorker:
    """Worker that automatically disables watchlists for inactive users."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.vitess_client: VitessClient | None = None
        # Configurable threshold
        self.disable_threshold_days = 30

    @asynccontextmanager
    async def lifespan(self):
        """Lifespan context manager for startup/shutdown."""
        try:
            # Initialize client
            vitess_config = settings.to_vitess_config()
            self.vitess_client = VitessClient(vitess_config)
            self.logger.info("Watchlist auto-disable worker started")
            yield
        except Exception as e:
            self.logger.error(f"Failed to start watchlist auto-disable worker: {e}")
            raise
        finally:
            self.logger.info("Watchlist auto-disable worker stopped")

    async def run_auto_disable(self) -> None:
        """Run one auto-disable cycle."""
        try:
            self.logger.info("Starting watchlist auto-disable cycle")
            disabled_count = 0

            # Get inactive users
            inactive_users = self._get_inactive_users()

            # Disable watchlists for inactive users
            for user_id in inactive_users:
                try:
                    self.vitess_client.user_repository.disable_watchlist(user_id)
                    disabled_count += 1
                    self.logger.info(f"Disabled watchlist for inactive user {user_id}")
                except Exception as e:
                    self.logger.error(
                        f"Failed to disable watchlist for user {user_id}: {e}"
                    )

            self.logger.info(
                f"Auto-disable cycle complete: {disabled_count} watchlists disabled"
            )

        except Exception as e:
            self.logger.error(f"Error during auto-disable cycle: {e}")

    def _get_inactive_users(self) -> list[int]:
        """Get list of user IDs that are inactive and have enabled watchlists."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.disable_threshold_days)
        inactive_users = []

        with self.vitess_client.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT user_id FROM users
                    WHERE last_activity < %s AND watchlist_enabled = TRUE
                    """,
                    (cutoff_date,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    inactive_users.append(row[0])

        return inactive_users


async def main() -> None:
    """Main entry point for the watchlist auto-disable worker."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = WatchlistAutoDisableWorker()

    async with worker.lifespan():
        # Run auto-disable once (for manual execution or cron)
        await worker.run_auto_disable()


if __name__ == "__main__":
    asyncio.run(main())
