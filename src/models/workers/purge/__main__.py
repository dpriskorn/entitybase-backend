"""Entry point for purge worker."""

from models.workers.purge.purge_worker import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
