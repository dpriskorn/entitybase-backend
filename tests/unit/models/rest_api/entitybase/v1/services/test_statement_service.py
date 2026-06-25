"""Unit tests for statement_service."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.services.statement_service import (
    StatementProcessingContext,
    StatementService,
)


class TestStatementProcessingContext:
    """Unit tests for StatementProcessingContext."""

    def test_statement_processing_context_creation(self):
        """Test creating StatementProcessingContext with all fields."""
        context = StatementProcessingContext(
            statement_hash=12345,
            statement_data={"mainsnak": {}},
            schema_version="2.0.0",
            idx=0,
            total_statements=1,
        )
        assert context.statement_hash == 12345
        assert context.statement_data == {"mainsnak": {}}
        assert context.schema_version == "2.0.0"
        assert context.idx == 0
        assert context.total_statements == 1
        assert context.validator is None

    def test_statement_processing_context_validator_is_optional(self):
        """Test that validator field exists and is optional."""
        context = StatementProcessingContext(
            statement_hash=12345,
            statement_data={"mainsnak": {}},
            schema_version="2.0.0",
            idx=0,
            total_statements=1,
        )
        assert context.validator is None

    def test_statement_processing_context_extra_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError):
            StatementProcessingContext(
                statement_hash=12345,
                statement_data={"mainsnak": {}},
                schema_version="2.0.0",
                idx=0,
                total_statements=1,
                extra_field="not allowed",
            )


class TestStatementService:
    """Unit tests for StatementService."""

    def test_hash_entity_statements_empty_claims(self):
        """Test hashing entity with empty claims."""
        mock_entity_data = MagicMock(spec=PreparedRequestData)
        mock_entity_data.claims = {}

        result = StatementService.hash_entity_statements(mock_entity_data)

        assert result.success is True
        assert result.data is not None
        assert result.data.statements == []
        assert result.data.properties == []

    def test_hash_entity_statements_none_claims(self):
        """Test hashing entity with None claims."""
        mock_entity_data = MagicMock(spec=PreparedRequestData)
        mock_entity_data.claims = None

        result = StatementService.hash_entity_statements(mock_entity_data)

        assert result.success is True

    def test_hash_entity_statements_with_claims(self):
        """Test hashing entity with valid claims."""
        mock_entity_data = MagicMock(spec=PreparedRequestData)
        mock_entity_data.claims = {
            "P1": [
                {
                    "mainsnak": {
                        "property": "P1",
                        "datavalue": {"value": "test", "type": "string"},
                    }
                }
            ]
        }

        with patch(
            "models.rest_api.entitybase.v1.services.statement_service.StatementExtractor.extract_properties_from_claims"
        ) as mock_extract_props, patch(
            "models.rest_api.entitybase.v1.services.statement_service.StatementExtractor.compute_property_counts_from_claims"
        ) as mock_compute_counts, patch(
            "models.rest_api.entitybase.v1.services.statement_service.StatementHasher.compute_hash"
        ) as mock_hash:
            mock_extract_props.return_value = ["P1"]
            mock_compute_counts.return_value = {"P1": 1}
            mock_hash.return_value = 12345

            result = StatementService.hash_entity_statements(mock_entity_data)

            assert result.success is True
            assert result.data is not None
            assert len(result.data.statements) == 1

    def test_hash_entity_statements_exception(self):
        """Test hashing entity with exception during property extraction."""
        mock_entity_data = MagicMock(spec=PreparedRequestData)
        mock_entity_data.claims = {"P1": [{"mainsnak": {}}]}

        with patch(
            "models.rest_api.entitybase.v1.services.statement_service.StatementExtractor.extract_properties_from_claims",
            side_effect=Exception("Test error"),
        ):
            result = StatementService.hash_entity_statements(mock_entity_data)

            assert result.success is False
            assert "Test error" in str(result.error)

    def test_process_snak_item_with_dict(self):
        """Test _process_snak_item with a dict snak."""
        mock_snak_handler = MagicMock()
        mock_snak_handler.store_snak.return_value = 12345

        item = {"property": "P1", "datavalue": {"value": "test"}}

        result = StatementService._process_snak_item(item, mock_snak_handler)

        assert result.value == 12345
        mock_snak_handler.store_snak.assert_called_once()

    def test_process_snak_item_with_hash(self):
        """Test _process_snak_item with an existing hash."""
        mock_snak_handler = MagicMock()

        item = 12345

        result = StatementService._process_snak_item(item, mock_snak_handler)

        assert result.value == 12345
        mock_snak_handler.store_snak.assert_not_called()

    def test_process_snak_list_value(self):
        """Test _process_snak_list_value processes list correctly."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()
        mock_snak_handler.store_snak.side_effect = [111, 222]

        snak_list = [
            {"property": "P1", "datavalue": {"value": "test1"}},
            {"property": "P2", "datavalue": {"value": "test2"}},
        ]

        result = service._process_snak_list_value("P1", snak_list, mock_snak_handler)

        assert result.key == "P1"
        assert len(result.values) == 2
        assert result.values[0].value == 111
        assert result.values[1].value == 222

    def test_deduplicate_and_store_statements_empty(self):
        """Test deduplicate_and_store_statements with empty hash result."""
        service = StatementService(state=MagicMock())

        mock_hash_result = MagicMock()
        mock_hash_result.statements = []
        mock_hash_result.full_statements = []

        with patch(
            "models.rest_api.entitybase.v1.services.statement_service.logger"
        ) as mock_logger:
            result = service.deduplicate_and_store_statements(mock_hash_result)

            assert result.success is True
            mock_logger.debug.assert_any_call(
                f"Deduplicating and storing 0 statements (S3-first)"
            )

    def test_deduplicate_and_store_statements_calls_process_single(self):
        """Test deduplicate_and_store_statements calls _process_single_statement."""
        service = StatementService(state=MagicMock())

        mock_hash_result = MagicMock()
        mock_hash_result.statements = [12345]
        mock_hash_result.full_statements = [{"mainsnak": {"property": "P1"}}]

        mock_context = MagicMock()
        mock_context.statement_hash = 12345
        mock_context.statement_data = {"mainsnak": {"property": "P1"}}

        with patch.object(
            service, "_process_single_statement", return_value=OperationResult(success=True)
        ) as mock_process, patch(
            "models.rest_api.entitybase.v1.services.statement_service.StatementProcessingContext"
        ) as mock_context_class, patch(
            "models.rest_api.entitybase.v1.services.statement_service.settings"
        ) as mock_settings:
            mock_settings.s3_statement_version = "2.0.0"
            mock_context_class.return_value = mock_context

            result = service.deduplicate_and_store_statements(mock_hash_result)

            assert result.success is True

    def test_deduplicate_and_store_statements_process_error(self):
        """Test deduplicate_and_store_statements handles process error."""
        service = StatementService(state=MagicMock())

        mock_hash_result = MagicMock()
        mock_hash_result.statements = [12345]
        mock_hash_result.full_statements = [{"mainsnak": {"property": "P1"}}]

        mock_context = MagicMock()
        mock_context.statement_hash = 12345

        with patch.object(
            service,
            "_process_single_statement",
            return_value=OperationResult(success=False, error="Process error"),
        ), patch(
            "models.rest_api.entitybase.v1.services.statement_service.StatementProcessingContext"
        ) as mock_context_class, patch(
            "models.rest_api.entitybase.v1.services.statement_service.settings"
        ) as mock_settings:
            mock_settings.s3_statement_version = "2.0.0"
            mock_context_class.return_value = mock_context

            result = service.deduplicate_and_store_statements(mock_hash_result)

            assert result.success is False
            assert "Process error" in str(result.error)

    def test_deduplicate_and_store_statements_exception(self):
        """Test deduplicate_and_store_statements handles exception."""
        service = StatementService(state=MagicMock())

        mock_hash_result = MagicMock()
        mock_hash_result.statements = [12345]
        mock_hash_result.full_statements = [{"mainsnak": {"property": "P1"}}]

        with patch(
            "models.rest_api.entitybase.v1.services.statement_service.StatementProcessingContext",
            side_effect=Exception("Context error"),
        ), patch(
            "models.rest_api.entitybase.v1.services.statement_service.settings"
        ) as mock_settings:
            mock_settings.s3_statement_version = "2.0.0"

            result = service.deduplicate_and_store_statements(mock_hash_result)

            assert result.success is False
            assert "Failed to store statement" in str(result.error)

    def test_deduplicate_references_in_statements(self):
        """Test deduplicate_references_in_statements processes references."""
        service = StatementService(state=MagicMock())

        mock_hash_result = MagicMock()
        mock_hash_result.full_statements = [
            {"references": [{"snaks": {"P1": [{"property": "P1"}]}}]}
        ]

        with patch.object(
            service, "_process_statement_references"
        ) as mock_process_refs, patch(
            "models.rest_api.entitybase.v1.services.statement_service.SnakHandler"
        ) as mock_snak_handler_class:
            mock_snak_handler = MagicMock()
            mock_snak_handler_class.return_value = mock_snak_handler

            result = service.deduplicate_references_in_statements(mock_hash_result)

            assert result.success is True
            assert mock_process_refs.call_count == 1

    def test_deduplicate_qualifiers_in_statements(self):
        """Test deduplicate_qualifiers_in_statements processes qualifiers."""
        service = StatementService(state=MagicMock())

        mock_hash_result = MagicMock()
        mock_hash_result.full_statements = [
            {"qualifiers": {"P1": [{"property": "P1", "datavalue": {"value": "test"}}]}}
        ]

        with patch.object(
            service, "_process_statement_qualifiers"
        ) as mock_process_quals, patch(
            "models.rest_api.entitybase.v1.services.statement_service.SnakHandler"
        ) as mock_snak_handler_class:
            mock_snak_handler = MagicMock()
            mock_snak_handler_class.return_value = mock_snak_handler

            result = service.deduplicate_qualifiers_in_statements(mock_hash_result)

            assert result.success is True
            assert mock_process_quals.call_count == 1

    def test_deduplicate_qualifiers_in_statements_no_qualifiers(self):
        """Test deduplicate_qualifiers_in_statements with no qualifiers."""
        service = StatementService(state=MagicMock())

        mock_hash_result = MagicMock()
        mock_hash_result.full_statements = [{}]

        with patch.object(
            service, "_process_statement_qualifiers"
        ) as mock_process_quals, patch(
            "models.rest_api.entitybase.v1.services.statement_service.SnakHandler"
        ) as mock_snak_handler_class:
            mock_snak_handler = MagicMock()
            mock_snak_handler_class.return_value = mock_snak_handler

            result = service.deduplicate_qualifiers_in_statements(mock_hash_result)

            assert result.success is True
            mock_process_quals.assert_not_called()

    def test_process_qualifier_list(self):
        """Test _process_qualifier_list processes qualifier list."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()
        mock_snak_handler.store_snak.side_effect = [111, 222]

        qual_values = [
            {"property": "P1", "datavalue": {"value": "qual1"}},
            {"property": "P2", "datavalue": {"value": "qual2"}},
        ]

        result = service._process_qualifier_list(qual_values, mock_snak_handler)

        assert result == [111, 222]

    def test_process_qualifier_list_with_hashes(self):
        """Test _process_qualifier_list with existing hashes."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()

        qual_values = [111, 222]

        result = service._process_qualifier_list(qual_values, mock_snak_handler)

        assert result == [111, 222]
        mock_snak_handler.store_snak.assert_not_called()

    def test_process_qualifier_dict(self):
        """Test _process_qualifier_dict processes qualifier dict."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()
        mock_snak_handler.store_snak.return_value = 12345

        qual_values = {"property": "P1", "datavalue": {"value": "qualifier"}}

        result = service._process_qualifier_dict(qual_values, mock_snak_handler)

        assert result == [12345]
        mock_snak_handler.store_snak.assert_called_once()

    def test_process_statement_references_no_references(self):
        """Test _process_statement_references with no references."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()

        statement_data = {}

        service._process_statement_references(statement_data, mock_snak_handler)

        assert statement_data == {}

    def test_process_statement_references_empty_list(self):
        """Test _process_statement_references with empty references list."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()

        statement_data = {"references": []}

        service._process_statement_references(statement_data, mock_snak_handler)

        assert statement_data["references"] == []

    def test_process_statement_qualifiers_no_qualifiers(self):
        """Test _process_statement_qualifiers with no qualifiers."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()

        statement_data = {}

        service._process_statement_qualifiers(statement_data, mock_snak_handler)

        assert statement_data == {}

    def test_process_single_reference_with_hash(self):
        """Test _process_single_reference with an existing hash."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()

        result = service._process_single_reference(12345, mock_snak_handler)

        assert result == 12345
        mock_snak_handler.store_snak.assert_not_called()

    def test_process_single_reference_with_dict(self):
        """Test _process_single_reference with a dict."""
        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()
        mock_snak_handler.store_snak.return_value = 999

        ref_dict = {
            "hash": 0,
            "reference": {"snaks": {"P1": []}},
            "created_at": "2024-01-01T00:00:00Z",
        }

        with patch(
            "models.rest_api.entitybase.v1.services.statement_service.ReferenceHasher.compute_hash"
        ) as mock_hash:
            mock_hash.return_value = 54321
            result = service._process_single_reference(ref_dict, mock_snak_handler)

            assert result == 54321

    def test_process_single_reference_with_s3_reference_data(self):
        """Test _process_single_reference with S3ReferenceData."""
        from models.data.infrastructure.s3.revision.reference_data import S3ReferenceData

        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()
        service.state.s3_client.store_reference = MagicMock()

        ref_data = S3ReferenceData(
            hash=0,
            reference={"snaks": {"P1": []}},
            created_at="2024-01-01T00:00:00Z",
        )

        with patch(
            "models.rest_api.entitybase.v1.services.statement_service.ReferenceHasher.compute_hash"
        ) as mock_hash:
            mock_hash.return_value = 12345
            result = service._process_single_reference(ref_data, mock_snak_handler)

            assert result == 12345
            service.state.s3_client.store_reference.assert_called_once()

    def test_process_reference_snaks(self):
        """Test _process_reference_snaks processes snaks correctly."""
        from models.data.infrastructure.s3.revision.reference_data import S3ReferenceData

        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()
        mock_snak_handler.store_snak.return_value = 111

        ref = S3ReferenceData(
            hash=12345,
            reference={"snaks": {}},
            created_at="2024-01-01T00:00:00Z",
        )

        result = service._process_reference_snaks(ref, mock_snak_handler)

        assert result.snaks == {}
        assert result.snaks_order == []

    def test_process_reference_snaks_with_snaks(self):
        """Test _process_reference_snaks with snaks data."""
        from models.data.infrastructure.s3.revision.reference_data import S3ReferenceData

        service = StatementService(state=MagicMock())
        mock_snak_handler = MagicMock()
        mock_snak_handler.store_snak.return_value = 111

        ref = S3ReferenceData(
            hash=12345,
            reference={
                "snaks": {"P1": [{"property": "P1", "datavalue": {"value": "test"}}]}
            },
            created_at="2024-01-01T00:00:00Z",
        )

        result = service._process_reference_snaks(ref, mock_snak_handler)

        assert "P1" in result.snaks
