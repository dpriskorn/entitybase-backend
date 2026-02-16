"""Incremental RDF worker package."""

from models.workers.incremental_rdf.incremental_rdf_worker import (
    IncrementalRDFWorker,
    main,
)

__all__ = ["IncrementalRDFWorker", "main"]
