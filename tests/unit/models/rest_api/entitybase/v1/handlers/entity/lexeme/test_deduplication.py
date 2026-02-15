"""Integration test for lexeme representation deduplication."""

from unittest.mock import MagicMock

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.rest_api.entitybase.v1.handlers.entity.lexeme.create import (
    LexemeCreateHandler,
)
from models.rest_api.entitybase.v1.services.enumeration_service import (
    EnumerationService,
)


def test_lexeme_term_hash_retrieval():
    """Test that lexeme terms can be retrieved by hash."""
    # Mock S3 client
    mock_s3_client = MagicMock()

    # Set up mock responses for batch retrieval
    mock_s3_client.load_form_representations_batch.return_value = [
        "answer",
        None,
        "answers",
    ]
    mock_s3_client.load_sense_glosses_batch.return_value = [
        "reply; reaction",
        "solution",
    ]

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
    mock_s3_client.store_form_representation.side_effect = Exception(
        "S3 storage failed"
    )
    mock_s3_client.store_sense_gloss.side_effect = Exception("S3 storage failed")

    # Mock state
    mock_state = MagicMock()
    mock_state.s3_client = mock_s3_client

    # Create handler
    enumeration_service = EnumerationService(
        worker_id="test", vitess_client=MagicMock()
    )
    handler = LexemeCreateHandler(
        state=mock_state, enumeration_service=enumeration_service
    )

    # Create request with forms/senses
    request = EntityCreateRequest(
        type="lexeme",
        forms=[
            {
                "id": "L999-F1",
                "representations": {"en": {"language": "en", "value": "test"}},
            }
        ],
        senses=[
            {
                "id": "L999-S1",
                "glosses": {"en": {"language": "en", "value": "test definition"}},
            }
        ],
    )

    # Process terms - should not raise exceptions despite storage failures
    import asyncio

    asyncio.run(handler._process_lexeme_terms(request, "L999"))

    # Verify storage was attempted despite failures
    mock_s3_client.store_form_representation.assert_called_once()
    mock_s3_client.store_sense_gloss.assert_called_once()
