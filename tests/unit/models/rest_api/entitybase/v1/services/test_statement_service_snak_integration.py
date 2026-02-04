"""Unit tests for statement service with snak deduplication."""

from unittest.mock import Mock, patch

import pytest

from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.services.statement_service import StatementService


class TestStatementServiceSnakIntegration:
    """Test statement service snak deduplication integration."""
    
    @pytest.fixture
    def mock_state(self):
        """Create mock state object."""
        state = Mock()
        state.s3_client = Mock()
        state.vitess_client = Mock()
        return state
    
    @pytest.fixture
    def sample_statement_data(self):
        """Create sample statement data with mainsnak."""
        return {
            "type": "statement",
            "id": "Q123$1",
            "rank": "normal",
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": {"entity-type": "item", "numeric-id": 5, "id": "Q5"},
                    "type": "wikibase-entityid"
                }
            },
            "qualifiers": {
                "P585": [{
                    "snaktype": "value",
                    "property": "P585",
                    "datavalue": {"value": "+2010-01-01T00:00:00Z", "type": "time"}
                }]
            }
        }
    
    @pytest.fixture
    def sample_hash_result(self, sample_statement_data):
        """Create sample StatementHashResult."""
        return StatementHashResult(
            statements=[123456789],
            properties=["P31"],
            full_statements=[sample_statement_data]
        )
    
    
    def test_deduplicate_statements_handles_missing_mainsnak(
        self, mock_state
    ):
        """Test handling of statements without mainsnak."""
        statement_data = {
            "type": "statement",
            "id": "Q123$4",
            "rank": "normal",
        }
        
        hash_result = StatementHashResult(
            statements=[123456792],
            properties=[],
            full_statements=[statement_data]
        )
        
        service = StatementService(state=mock_state)
        mock_state.s3_client.read_statement.side_effect = Exception("Not found")
        mock_state.vitess_client.insert_statement_content.return_value = True
        
        with patch('models.rest_api.entitybase.v1.services.statement_service.SnakHandler') as MockSnakHandler:
            mock_snak_handler_instance = Mock()
            MockSnakHandler.return_value = mock_snak_handler_instance
            
            result = service.deduplicate_and_store_statements(hash_result)
            
            # Verify SnakHandler was never called
            assert mock_snak_handler_instance.store_snak.call_count == 0
            
        assert result.success is True
    
    def test_deduplicate_statements_replaces_mainsnak_with_hash(
        self, mock_state, sample_hash_result
    ):
        """Test that mainsnak is replaced with hash reference in stored statement."""
        service = StatementService(state=mock_state)
        
        s3_written_statements = []
        
        def capture_statement(hash_, data, schema_version):
            s3_written_statements.append(data)
        
        mock_state.s3_client.read_statement.side_effect = Exception("Not found")
        mock_state.s3_client.write_statement.side_effect = capture_statement
        mock_state.vitess_client.insert_statement_content.return_value = True
        
        with patch('models.rest_api.entitybase.v1.services.statement_service.SnakHandler') as MockSnakHandler:
            mock_snak_handler_instance = Mock()
            mock_snak_handler_instance.store_snak.return_value = 999999999
            MockSnakHandler.return_value = mock_snak_handler_instance
            
            result = service.deduplicate_and_store_statements(sample_hash_result)
            
            # Verify stored statement has hash reference instead of full mainsnak
            assert len(s3_written_statements) > 0
            stored_statement = s3_written_statements[0]
            assert "hash" in stored_statement["statement"]["mainsnak"]
            assert stored_statement["statement"]["mainsnak"]["hash"] == 999999999
            
        assert result.success is True