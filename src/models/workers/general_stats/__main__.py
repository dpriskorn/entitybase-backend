"""Entry point for general statistics worker."""

from models.workers.general_stats.general_stats_worker import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
