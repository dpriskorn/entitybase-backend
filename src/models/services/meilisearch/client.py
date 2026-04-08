"""Meilisearch client module."""

import logging
from typing import Any

from pydantic import BaseModel, Field

from models.data.infrastructure.meilisearch import (
    MeilisearchDocument,
    MeilisearchDocumentResponse,
)

logger = logging.getLogger(__name__)

try:
    import meilisearch
    from meilisearch.client import Client as MeilisearchClientType
    from meilisearch.index import Index as MeilisearchIndexType
except ImportError:
    MeilisearchClientType = None
    MeilisearchIndexType = None
    meilisearch = None


class MeilisearchClient(BaseModel):
    """Client for interacting with Meilisearch."""

    model_config = {"arbitrary_types_allowed": True}

    host: str = Field(default="localhost")
    port: int = Field(default=7700)
    api_key: str | None = Field(default=None)
    index_name: str = Field(default="entitybase")
    client: MeilisearchClientType | None = Field(default=None, exclude=True)
    _index: MeilisearchIndexType | None = Field(default=None, exclude=True)

    def model_post_init(self, context: Any) -> None:
        """Post-initialization hook."""
        pass

    def connect(self) -> bool:
        """Connect to Meilisearch.

        Returns:
            True if connection successful, False otherwise
        """
        if meilisearch is None:
            logger.error("meilisearch not installed")
            return False

        try:
            url = f"http://{self.host}:{self.port}"
            self.client = meilisearch.Client(url, self.api_key)
            self._index = self.client.index(self.index_name)
            logger.info(f"Connected to Meilisearch at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Meilisearch: {e}")
            return False

    def index_document(self, doc_id: str, document: dict[str, Any]) -> bool:
        """Index a document.

        Args:
            doc_id: Document ID
            document: Document to index

        Returns:
            True if successful, False otherwise
        """
        if not self.client or not self._index:
            logger.error("Client not connected")
            return False

        try:
            doc_with_id = {"id": doc_id, **document}
            task = self._index.add_documents([doc_with_id])
            logger.debug(f"Indexed document {doc_id}, task UID: {task.task_uid}")
            return True
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            return False

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document.

        Args:
            doc_id: Document ID to delete

        Returns:
            True if successful, False otherwise
        """
        if not self.client or not self._index:
            logger.error("Client not connected")
            return False

        try:
            task = self._index.delete_document(doc_id)
            logger.debug(f"Deleted document {doc_id}, task UID: {task.task_uid}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    def get_document(self, doc_id: str) -> MeilisearchDocumentResponse:
        """Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            MeilisearchDocumentResponse with the document if found
        """
        if not self.client or not self._index:
            logger.error("Client not connected")
            return MeilisearchDocumentResponse(data=None)

        try:
            response = self._index.get_document(doc_id)
            if response:
                return MeilisearchDocumentResponse(
                    data=MeilisearchDocument(**response)
                )
            return MeilisearchDocumentResponse(data=None)
        except Exception:
            return MeilisearchDocumentResponse(data=None)

    def close(self) -> None:
        """Close the client connection."""
        self.client = None
        self._index = None
        logger.info("Meilisearch connection closed")