"""Entry point for JSON dump worker."""

from models.workers.json_dumps.json_dump_worker import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
