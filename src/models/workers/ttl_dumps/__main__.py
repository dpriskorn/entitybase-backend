"""Entry point for TTL dump worker."""
from models.workers.ttl_dumps.ttl_dump_worker import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
