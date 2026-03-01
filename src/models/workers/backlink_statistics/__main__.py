"""Entry point for backlink statistics worker."""

from models.workers.backlink_statistics.backlink_statistics_worker import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
