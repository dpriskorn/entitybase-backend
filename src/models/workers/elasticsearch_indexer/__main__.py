"""Entry point for the Elasticsearch indexer worker."""

import asyncio

from models.workers.elasticsearch_indexer.elasticsearch_indexer_worker import main

if __name__ == "__main__":
    asyncio.run(main())
