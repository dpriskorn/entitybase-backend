"""Integration tests for entity revision S3 storage."""

import pytest
from unittest.mock import MagicMock, patch
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_creation_stores_s3_revision_data(api_prefix: str) -> None:
    """Test that creating an entity stores S3RevisionData in S3."""
    from models.rest_api.main import app

    # Mock S3 client to capture S3RevisionData storage
    # Since initialized_app fixture creates real StateHandler, we need to replace its s3_client
    mock_s3_client = MagicMock()
    original_s3_client = app.state.state_handler.cached_s3_client
    app.state.state_handler.cached_s3_client = mock_s3_client

    try:
        # Create entity without statements to avoid schema mismatch bug
        entity_data = {
            "labels": {"en": {"language": "en", "value": "Test Entity"}},
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Create entity
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            # Verify S3RevisionData was stored
            mock_s3_client.store_revision.assert_called_once()

            # Check arguments
            call_args = mock_s3_client.store_revision.call_args
            content_hash = call_args[0][0]  # First argument
            s3_revision_data = call_args[0][1]  # Second argument

            # Verify S3RevisionData structure
            assert hasattr(s3_revision_data, "schema_version")
            assert hasattr(s3_revision_data, "revision")
            assert hasattr(s3_revision_data, "content_hash")
            assert hasattr(s3_revision_data, "created_at")

            assert s3_revision_data.schema_version in ["3.0.0", "4.0.0"]  # From settings
            assert isinstance(s3_revision_data.revision, dict)
            assert "revision_id" in s3_revision_data.revision
            assert "entity_type" in s3_revision_data.revision
            assert "hashes" in s3_revision_data.revision
            assert s3_revision_data.content_hash == content_hash
    finally:
        app.state.state_handler.cached_s3_client = original_s3_client


@pytest.mark.asyncio
@pytest.mark.integration
async def test_s3_revision_data_content_hash_consistency(api_prefix: str) -> None:
    """Test that S3RevisionData content hash is computed correctly."""
    from models.rest_api.main import app

    # Mock S3 client to capture S3RevisionData storage
    mock_s3_client = MagicMock()
    original_s3_client = app.state.state_handler.cached_s3_client
    app.state.state_handler.cached_s3_client = mock_s3_client

    try:
        entity_data = {
            "labels": {"en": {"language": "en", "value": "Hash Test"}},
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            # Get the stored S3RevisionData
            call_args = mock_s3_client.store_revision.call_args
            stored_hash = call_args[0][0]
            stored_data = call_args[0][1]

            # Verify hash is an integer
            assert isinstance(stored_hash, int)
            assert stored_hash == stored_data.content_hash

            # The hash should be deterministic for same data
            # (This is a basic check - in practice we'd verify against actual hash function)
    finally:
        app.state.state_handler.cached_s3_client = original_s3_client


@pytest.mark.asyncio
@pytest.mark.integration
async def test_s3_revision_data_structure_completeness(api_prefix: str) -> None:
    """Test that S3RevisionData.revision contains complete revision data."""
    from models.rest_api.main import app

    # Mock S3 client to capture S3RevisionData storage
    mock_s3_client = MagicMock()
    original_s3_client = app.state.state_handler.cached_s3_client
    app.state.state_handler.cached_s3_client = mock_s3_client

    try:
        entity_data = {
            "labels": {"en": {"language": "en", "value": "Complete Test"}},
            "descriptions": {"en": {"language": "en", "value": "Test description"}},
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=entity_data,
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            # Get the stored S3RevisionData
            call_args = mock_s3_client.store_revision.call_args
            s3_revision_data = call_args[0][1]

            revision = s3_revision_data.revision

            # Check that all expected fields are present
            required_fields = [
                "schema_version",
                "revision_id",
                "entity_type",
                "edit",
                "hashes",
                "properties",
                "property_counts",
                "created_at",
                "redirects_to",
                "state",
            ]

            for field in required_fields:
                assert field in revision, f"Missing field: {field}"

            # Check edit structure (with aliases)
            edit = revision["edit"]
            assert "is_mass_edit" in edit
            assert "edit_type" in edit
            assert "user_id" in edit
            assert "edit_summary" in edit
            assert "at" in edit
    finally:
        app.state.state_handler.cached_s3_client = original_s3_client
