"""Entry point for the Incremental RDF worker."""

import asyncio

from models.workers.incremental_rdf.incremental_rdf_worker import main

if __name__ == "__main__":
    asyncio.run(main())
