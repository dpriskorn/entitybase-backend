"""Entry point for the Meilisearch indexer worker."""

import asyncio

from models.workers.meilisearch_indexer.meilisearch_indexer_worker import main

if __name__ == "__main__":
    asyncio.run(main())
