"""Meilisearch indexer worker."""

from models.workers.meilisearch_indexer.meilisearch_indexer_worker import (
    MeilisearchIndexerWorker,
    main,
)

__all__ = ["MeilisearchIndexerWorker", "main"]