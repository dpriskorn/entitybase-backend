"""Unit tests for Meilisearch client."""

import pytest
from unittest.mock import MagicMock, patch

from models.data.infrastructure.meilisearch import MeilisearchDocumentResponse
from models.services.meilisearch.client import MeilisearchClient


class TestMeilisearchClient:
    """Tests for MeilisearchClient class."""

    def test_init_defaults(self):
        """Test client initialization with defaults."""
        client = MeilisearchClient()

        assert client.host == "localhost"
        assert client.port == 7700
        assert client.api_key is None
        assert client.index_name == "entitybase"
        assert client.client is None

    def test_init_custom_values(self):
        """Test client initialization with custom values."""
        client = MeilisearchClient(
            host="meili.example.com",
            port=7701,
            api_key="test-key",
            index_name="myindex",
        )

        assert client.host == "meili.example.com"
        assert client.port == 7701
        assert client.api_key == "test-key"
        assert client.index_name == "myindex"

    @patch("models.services.meilisearch.client.meilisearch", None)
    def test_connect_no_library(self):
        """Test connect fails when meilisearch not installed."""
        client = MeilisearchClient()
        result = client.connect()

        assert result is False

    @patch("models.services.meilisearch.client.meilisearch")
    def test_connect_success(self, mock_meilisearch):
        """Test successful connection."""
        mock_client = MagicMock()
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        result = client.connect()

        assert result is True
        mock_meilisearch.Client.assert_called_once()

    @patch("models.services.meilisearch.client.meilisearch")
    def test_connect_failure(self, mock_meilisearch):
        """Test failed connection."""
        mock_meilisearch.Client.side_effect = Exception("Connection failed")

        client = MeilisearchClient()
        result = client.connect()

        assert result is False

    @patch("models.services.meilisearch.client.meilisearch")
    def test_index_document_not_connected(self, mock_meilisearch):
        """Test indexing without connection."""
        client = MeilisearchClient()
        result = client.index_document("Q42", {"test": "data"})

        assert result is False

    @patch("models.services.meilisearch.client.meilisearch")
    def test_index_document_success(self, mock_meilisearch):
        """Test successful document indexing."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_task = MagicMock()
        mock_task.task_uid = 12345
        mock_index.add_documents.return_value = mock_task
        mock_client.index.return_value = mock_index
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        client.connect()
        result = client.index_document("Q42", {"test": "data"})

        assert result is True
        mock_index.add_documents.assert_called_once()

    @patch("models.services.meilisearch.client.meilisearch")
    def test_index_document_failure(self, mock_meilisearch):
        """Test document indexing failure."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_index.add_documents.side_effect = Exception("Index failed")
        mock_client.index.return_value = mock_index
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        client.connect()
        result = client.index_document("Q42", {"test": "data"})

        assert result is False

    @patch("models.services.meilisearch.client.meilisearch")
    def test_delete_document_not_connected(self, mock_meilisearch):
        """Test deletion without connection."""
        client = MeilisearchClient()
        result = client.delete_document("Q42")

        assert result is False

    @patch("models.services.meilisearch.client.meilisearch")
    def test_delete_document_success(self, mock_meilisearch):
        """Test successful document deletion."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_task = MagicMock()
        mock_task.task_uid = 12345
        mock_index.delete_document.return_value = mock_task
        mock_client.index.return_value = mock_index
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        client.connect()
        result = client.delete_document("Q42")

        assert result is True
        mock_index.delete_document.assert_called_once_with("Q42")

    @patch("models.services.meilisearch.client.meilisearch")
    def test_delete_document_failure(self, mock_meilisearch):
        """Test document deletion failure."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_index.delete_document.side_effect = Exception("Delete failed")
        mock_client.index.return_value = mock_index
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        client.connect()
        result = client.delete_document("Q42")

        assert result is False

    @patch("models.services.meilisearch.client.meilisearch")
    def test_get_document_not_connected(self, mock_meilisearch):
        """Test get without connection."""
        client = MeilisearchClient()
        result = client.get_document("Q42")

        assert result == MeilisearchDocumentResponse(data=None)

    @patch("models.services.meilisearch.client.meilisearch")
    def test_get_document_success(self, mock_meilisearch):
        """Test successful document retrieval."""
        from models.data.infrastructure.meilisearch import MeilisearchDocument

        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_index.get_document.return_value = {
            "@id": "Q42",
            "@type": "item",
            "lastrevid": 12345,
            "modified": "2025-01-01T00:00:00Z",
            "labels": {"en": "Test"},
            "descriptions": {},
            "aliases": {},
            "claims": {},
            "claims_flat": {},
        }
        mock_client.index.return_value = mock_index
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        client.connect()
        result = client.get_document("Q42")

        assert result.data is not None
        assert result.data.entity_id == "Q42"

    @patch("models.services.meilisearch.client.meilisearch")
    def test_get_document_not_found(self, mock_meilisearch):
        """Test document not found."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_index.get_document.side_effect = Exception("Not found")
        mock_client.index.return_value = mock_index
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        client.connect()
        result = client.get_document("Q999")

        assert result == MeilisearchDocumentResponse(data=None)

    @patch("models.services.meilisearch.client.meilisearch")
    def test_close(self, mock_meilisearch):
        """Test close method."""
        mock_client = MagicMock()
        mock_meilisearch.Client.return_value = mock_client

        client = MeilisearchClient()
        client.connect()
        client.close()

        assert client.client is None
        assert client.index is None
