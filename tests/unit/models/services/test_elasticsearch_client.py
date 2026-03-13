"""Unit tests for Elasticsearch client."""

import pytest
from unittest.mock import MagicMock, patch

from models.services.elasticsearch.client import ElasticsearchClient


class TestElasticsearchClient:
    """Tests for ElasticsearchClient class."""

    def test_init_defaults(self):
        """Test client initialization with defaults."""
        client = ElasticsearchClient()

        assert client.host == "localhost"
        assert client.port == 9200
        assert client.index == "entitybase"
        assert client.username is None
        assert client.password is None
        assert client.use_ssl is True
        assert client.verify_certs is True

    def test_init_custom_values(self):
        """Test client initialization with custom values."""
        client = ElasticsearchClient(
            host="es.example.com",
            port=9201,
            index="myindex",
            username="user",
            password="pass",
        )

        assert client.host == "es.example.com"
        assert client.port == 9201
        assert client.index == "myindex"
        assert client.username == "user"
        assert client.password == "pass"

    @patch("models.services.elasticsearch.client.OpenSearch", None)
    def test_connect_no_library(self):
        """Test connect fails when opensearch-py not installed."""
        client = ElasticsearchClient()
        result = client.connect()

        assert result is False

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_connect_success(self, mock_opensearch):
        """Test successful connection."""
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        result = client.connect()

        assert result is True
        mock_opensearch.assert_called_once()

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_connect_failure(self, mock_opensearch):
        """Test failed connection."""
        mock_opensearch.side_effect = Exception("Connection failed")

        client = ElasticsearchClient()
        result = client.connect()

        assert result is False

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_index_document_not_connected(self, mock_opensearch):
        """Test indexing without connection."""
        client = ElasticsearchClient()
        result = client.index_document("Q42", {"test": "data"})

        assert result is False

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_index_document_success(self, mock_opensearch):
        """Test successful document indexing."""
        mock_client = MagicMock()
        mock_client.index.return_value = {"result": "created"}
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        client.connect()
        result = client.index_document("Q42", {"test": "data"})

        assert result is True
        mock_client.index.assert_called_once()

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_index_document_failure(self, mock_opensearch):
        """Test document indexing failure."""
        mock_client = MagicMock()
        mock_client.index.side_effect = Exception("Index failed")
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        client.connect()
        result = client.index_document("Q42", {"test": "data"})

        assert result is False

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_delete_document_not_connected(self, mock_opensearch):
        """Test deletion without connection."""
        client = ElasticsearchClient()
        result = client.delete_document("Q42")

        assert result is False

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_delete_document_success(self, mock_opensearch):
        """Test successful document deletion."""
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        client.connect()
        result = client.delete_document("Q42")

        assert result is True
        mock_client.delete.assert_called_once()

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_delete_document_failure(self, mock_opensearch):
        """Test document deletion failure."""
        mock_client = MagicMock()
        mock_client.delete.side_effect = Exception("Delete failed")
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        client.connect()
        result = client.delete_document("Q42")

        assert result is False

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_get_document_not_connected(self, mock_opensearch):
        """Test get without connection."""
        client = ElasticsearchClient()
        result = client.get_document("Q42")

        assert result is None

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_get_document_success(self, mock_opensearch):
        """Test successful document retrieval."""
        mock_client = MagicMock()
        mock_client.get.return_value = {"_source": {"test": "data"}}
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        client.connect()
        result = client.get_document("Q42")

        assert result == {"test": "data"}

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_get_document_not_found(self, mock_opensearch):
        """Test document not found."""
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Not found")
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        client.connect()
        result = client.get_document("Q999")

        assert result is None

    @patch("models.services.elasticsearch.client.OpenSearch")
    def test_close(self, mock_opensearch):
        """Test close method."""
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client

        client = ElasticsearchClient()
        client.connect()
        client.close()

        mock_client.close.assert_called_once()
