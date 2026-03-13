"""Elasticsearch client module."""

import logging
from typing import Any

from models.data.infrastructure.elasticsearch import (
    ElasticsearchDocument,
    ElasticsearchDocumentResponse,
)

logger = logging.getLogger(__name__)

try:
    from opensearchpy import OpenSearch
except ImportError:
    OpenSearch = None


class ElasticsearchClient:
    """Client for interacting with Elasticsearch/OpenSearch."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9200,
        index: str = "entitybase",
        username: str | None = None,
        password: str | None = None,
    ):
        """Initialize Elasticsearch client.

        Args:
            host: Elasticsearch host
            port: Elasticsearch port
            index: Default index name
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.host = host
        self.port = port
        self.index = index
        self.username = username
        self.password = password
        self.use_ssl = True
        self.verify_certs = True
        self.client = None

    def connect(self) -> bool:
        """Connect to Elasticsearch.

        Returns:
            True if connection successful, False otherwise
        """
        if OpenSearch is None:
            logger.error("opensearch-py not installed")
            return False

        try:
            auth = (
                (self.username, self.password)
                if self.username and self.password
                else None
            )

            self.client = OpenSearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_auth=auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                ssl_show_warn=False,
            )
            logger.info(f"Connected to Elasticsearch at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False

    def index_document(self, doc_id: str, document: dict[str, Any]) -> bool:
        """Index a document.

        Args:
            doc_id: Document ID
            document: Document to index

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Client not connected")
            return False

        try:
            response = self.client.index(
                index=self.index,
                id=doc_id,
                body=document,
                refresh=True,
            )
            logger.debug(f"Indexed document {doc_id}: {response.get('result')}")
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
        if not self.client:
            logger.error("Client not connected")
            return False

        try:
            self.client.delete(index=self.index, id=doc_id, refresh=True)
            logger.debug(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    def get_document(self, doc_id: str) -> ElasticsearchDocumentResponse:
        """Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            ElasticsearchDocumentResponse with the document if found
        """
        if not self.client:
            logger.error("Client not connected")
            return ElasticsearchDocumentResponse(data=None)

        try:
            response = self.client.get(index=self.index, id=doc_id)
            source = response.get("_source")
            if source:
                return ElasticsearchDocumentResponse(
                    data=ElasticsearchDocument(**source)
                )
            return ElasticsearchDocumentResponse(data=None)
        except Exception:
            return ElasticsearchDocumentResponse(data=None)

    def close(self) -> None:
        """Close the client connection."""
        if self.client:
            self.client.close()
            logger.info("Elasticsearch connection closed")
