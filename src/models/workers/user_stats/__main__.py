"""Entry point for user statistics worker."""

from models.workers.user_stats.user_stats_worker import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
