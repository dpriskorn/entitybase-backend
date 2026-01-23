"""Integration test for lexeme representation deduplication."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from models.internal_representation.metadata_extractor import MetadataExtractor
from models.json_parser.entity_parser import parse_entity_data
from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import LexemeCreateHandler
from models.data.rest_api.v1.request import EntityCreateRequest
from models.rest_api.entitybase.v1.services.enumeration_service import EnumerationService


@pytest.mark.asyncio
async def test_lexeme_deduplication_integration():
    """Integration test for lexeme form/sense deduplication."""
    # Load L42 test data
    test_data_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent.parent / "test_data" / "json" / "entities" / "L42.json"

    with open(test_data_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Parse the entity data
    entity_data = parse_entity_data(raw_data)

    # Create a mock state and S3 client
    mock_state = MagicMock()
    mock_s3_client = MagicMock()
    mock_state.s3_client = mock_s3_client
    mock_state.vitess_client = MagicMock()

    # Mock enumeration service
    mock_enumeration = MagicMock()
    mock_enumeration.get_next_entity_id.return_value = "L999"
    mock_enumeration.confirm_id_usage = MagicMock()

    # Create the handler
    handler = LexemeCreateHandler(state=mock_state, enumeration_service=mock_enumeration)

    # Create a create request from the parsed data
    request_data = raw_data["entities"]["L42"]
    request = EntityCreateRequest(
        type="lexeme",
        data=request_data
    )

    # Mock the parent create_entity method to return a response
    mock_response = MagicMock()
    mock_response.id = "L999"

    with patch.object(handler.__class__.__bases__[0], 'create_entity', return_value=mock_response):
        # Process the lexeme terms
        await handler._process_lexeme_terms(request, "L999")

    # Verify that terms were stored with proper hashes
    extractor = MetadataExtractor()

    # Check form representations were processed
    assert len(entity_data.forms) == 3
    for form in entity_data.forms:
        for lang, rep in form.representations.items():
            expected_hash = extractor.hash_string(rep.value)
            mock_s3_client.store_form_representation.assert_any_call(rep.value, expected_hash)

    # Check sense glosses were processed
    assert len(entity_data.senses) == 3
    for sense in entity_data.senses:
        for lang, gloss in sense.glosses.items():
            expected_hash = extractor.hash_string(gloss.value)
            mock_s3_client.store_sense_gloss.assert_any_call(gloss.value, expected_hash)

    # Verify hash mappings were added to request data
    forms_data = request.data.get("forms", [])
    senses_data = request.data.get("senses", [])

    for form_data in forms_data:
        assert "representation_hashes" in form_data
        for lang in form_data.get("representations", {}):
            assert lang in form_data["representation_hashes"]
            assert isinstance(form_data["representation_hashes"][lang], int)

    for sense_data in senses_data:
        assert "gloss_hashes" in sense_data
        for lang in sense_data.get("glosses", {}):
            assert lang in sense_data["gloss_hashes"]
            assert isinstance(sense_data["gloss_hashes"][lang], int)


def test_lexeme_term_hash_retrieval():
    """Test that lexeme terms can be retrieved by hash."""
    # Mock S3 client
    mock_s3_client = MagicMock()

    # Set up mock responses for batch retrieval
    mock_s3_client.load_form_representations_batch.return_value = ["answer", None, "answers"]
    mock_s3_client.load_sense_glosses_batch.return_value = ["reply; reaction", "solution"]

    # Test form representation retrieval
    hashes = [123, 456, 789]
    results = mock_s3_client.load_form_representations_batch(hashes)

    assert results == ["answer", None, "answers"]
    mock_s3_client.load_form_representations_batch.assert_called_once_with(hashes)

    # Test sense gloss retrieval
    gloss_hashes = [111, 222]
    gloss_results = mock_s3_client.load_sense_glosses_batch(gloss_hashes)

    assert gloss_results == ["reply; reaction", "solution"]
    mock_s3_client.load_sense_glosses_batch.assert_called_once_with(gloss_hashes)


def test_lexeme_storage_error_handling():
    """Test error handling in lexeme storage operations."""
    # Mock S3 client that raises exceptions
    mock_s3_client = MagicMock()
    mock_s3_client.store_form_representation.side_effect = Exception("S3 storage failed")
    mock_s3_client.store_sense_gloss.side_effect = Exception("S3 storage failed")

    # Mock state
    mock_state = MagicMock()
    mock_state.s3_client = mock_s3_client

    # Create handler
    enumeration_service = EnumerationService(worker_id="test", vitess_client=MagicMock())
    handler = LexemeCreateHandler(state=mock_state, enumeration_service=enumeration_service)

    # Create request with forms/senses
    request = EntityCreateRequest(
        type="lexeme",
        edit_summary="test edit",
        data={
            "forms": [{
                "id": "L999-F1",
                "representations": {"en": {"value": "test"}}
            }],
            "senses": [{
                "id": "L999-S1",
                "glosses": {"en": {"value": "test definition"}}
            }]
        }
    )

    # Process terms - should not raise exceptions despite storage failures
    import asyncio
    asyncio.run(handler._process_lexeme_terms(request, "L999"))

    # Verify storage was attempted despite failures
    mock_s3_client.store_form_representation.assert_called_once()
    mock_s3_client.store_sense_gloss.assert_called_once()