"""Unit tests for statement handler with snak reconstruction."""

from unittest.mock import Mock, patch

import pytest

from models.data.rest_api.v1.entitybase.request import StatementBatchRequest
from models.rest_api.entitybase.v1.handlers.statement import StatementHandler


class TestStatementHandlerSnakReconstruction:
    """Test statement handler snak reconstruction from hashes."""
    
    @pytest.fixture
    def mock_state(self):
        """Create mock state object."""
        state = Mock()
        state.s3_client = Mock()
        state.vitess_client = Mock()
        return state
    
    @pytest.fixture
    def sample_statement_data(self):
        """Create sample statement data using hash reference."""
        return {
            "type": "statement",
            "id": "Q123$1",
            "rank": "normal",
            "mainsnak": {"hash": 123456789},
            "qualifiers": 987654321,
        }
    
    def test_get_statement_reconstructs_mainsnak_from_hash(
        self, mock_state, sample_statement_data
    ):
        """Test that statement retrieval reconstructs mainsnak from hash."""
        handler = StatementHandler(state=mock_state)
        
        # Mock S3 storage
        mock_s3_statement = Mock()
        mock_s3_statement.schema_version = "2.0.0"
        mock_s3_statement.statement = sample_statement_data
        mock_s3_statement.created_at = "2024-01-01T00:00:00Z"
        mock_state.s3_client.read_statement.return_value = mock_s3_statement
        
        # Mock reconstructed snak
        with patch('models.rest_api.entitybase.v1.handlers.statement.SnakHandler') as MockSnakHandler:
            mock_snak_handler_instance = Mock()
            reconstructed_snak = {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": {"entity-type": "item", "numeric-id": 5, "id": "Q5"},
                    "type": "wikibase-entityid"
                }
            }
            mock_snak_handler_instance.get_snak.return_value = reconstructed_snak
            MockSnakHandler.return_value = mock_snak_handler_instance
            
            response = handler.get_statement(123456789)
            
            # Verify snak was reconstructed
            assert response.statement["mainsnak"] == reconstructed_snak
            assert "hash" not in response.statement["mainsnak"]
            
            # Verify SnakHandler was called with correct hash
            mock_snak_handler_instance.get_snak.assert_called_once_with(123456789)
    
    def test_get_statement_handles_missing_snak(
        self, mock_state, sample_statement_data
    ):
        """Test handling when snak is not found in S3."""
        handler = StatementHandler(state=mock_state)
        
        mock_s3_statement = Mock()
        mock_s3_statement.schema_version = "2.0.0"
        mock_s3_statement.statement = sample_statement_data
        mock_s3_statement.created_at = "2024-01-01T00:00:00Z"
        mock_state.s3_client.read_statement.return_value = mock_s3_statement
        
        with patch('models.rest_api.entitybase.v1.handlers.statement.SnakHandler') as MockSnakHandler:
            mock_snak_handler_instance = Mock()
            mock_snak_handler_instance.get_snak.return_value = None
            MockSnakHandler.return_value = mock_snak_handler_instance
            
            response = handler.get_statement(123456789)
            
            # Verify statement still returned even with missing snak
            assert response.statement["mainsnak"] == {"hash": 123456789}
    
    def test_get_statements_batch_reconstructs_multiple_snaks(
        self, mock_state
    ):
        """Test batch statement retrieval reconstructs all snaks."""
        handler = StatementHandler(state=mock_state)
        
        statement_data_1 = {
            "type": "statement",
            "id": "Q123$1",
            "rank": "normal",
            "mainsnak": {"hash": 111111111},
        }
        
        statement_data_2 = {
            "type": "statement",
            "id": "Q123$2",
            "rank": "normal",
            "mainsnak": {"hash": 222222222},
        }
        
        mock_s3_statement_1 = Mock()
        mock_s3_statement_1.schema_version = "2.0.0"
        mock_s3_statement_1.statement = statement_data_1
        mock_s3_statement_1.created_at = "2024-01-01T00:00:00Z"
        
        mock_s3_statement_2 = Mock()
        mock_s3_statement_2.schema_version = "2.0.0"
        mock_s3_statement_2.statement = statement_data_2
        mock_s3_statement_2.created_at = "2024-01-01T00:00:00Z"
        
        mock_state.s3_client.read_statement.side_effect = [mock_s3_statement_1, mock_s3_statement_2]
        
        with patch('models.rest_api.entitybase.v1.handlers.statement.SnakHandler') as MockSnakHandler:
            mock_snak_handler_instance = Mock()
            
            reconstructed_snak_1 = {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"value": "Q5", "type": "string"}
            }
            reconstructed_snak_2 = {
                "snaktype": "value",
                "property": "P569",
                "datavalue": {"value": "1990-01-01", "type": "string"}
            }
            mock_snak_handler_instance.get_snak.side_effect = [reconstructed_snak_1, reconstructed_snak_2]
            MockSnakHandler.return_value = mock_snak_handler_instance
            
            request = StatementBatchRequest(hashes=[111111111, 222222222])
            response = handler.get_statements_batch(request)
            
            # Verify both snaks were reconstructed
            assert len(response.statements) == 2
            assert response.statements[0].statement["mainsnak"]["property"] == "P31"
            assert response.statements[1].statement["mainsnak"]["property"] == "P569"
            
            # Verify SnakHandler.get_snak called twice
            assert mock_snak_handler_instance.get_snak.call_count == 2
    
    def test_get_entity_property_hashes_handles_hash_referenced_snaks(
        self, mock_state
    ):
        """Test getting entity property hashes with hash-referenced snaks."""
        handler = StatementHandler(state=mock_state)
        
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 1
        
        mock_revision_metadata = Mock()
        mock_revision_metadata.data = {
            "statements": [123456789, 987654321],
            "properties": ["P31"],
        }
        mock_state.s3_client.read_full_revision.return_value = mock_revision_metadata
        
        statement_data = {
            "type": "statement",
            "id": "Q123$1",
            "rank": "normal",
            "mainsnak": {"hash": 123456789},
        }
        
        mock_s3_statement = Mock()
        mock_s3_statement.statement = statement_data
        mock_state.s3_client.read_statement.return_value = mock_s3_statement
        
        with patch('models.rest_api.entitybase.v1.handlers.statement.SnakHandler') as MockSnakHandler:
            mock_snak_handler_instance = Mock()
            reconstructed_snak = {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"value": "Q5", "type": "string"}
            }
            mock_snak_handler_instance.get_snak.return_value = reconstructed_snak
            MockSnakHandler.return_value = mock_snak_handler_instance
            
            response = handler.get_entity_property_hashes("Q123", "P31")
            
            # Verify statement matched by property from reconstructed snak
            assert len(response.property_hashes) == 1
            assert 123456789 in response.property_hashes
            
            # Verify SnakHandler was called
            mock_snak_handler_instance.get_snak.assert_called_once_with(123456789)