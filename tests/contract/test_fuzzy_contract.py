"""Fuzzy contract tests for entitybase-backend API endpoints.

These tests verify that the API handles invalid, malformed, and edge case
inputs gracefully by returning appropriate error codes (404, 422, 400)
instead of crashing or returning 500.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_numeric_entity_id_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Numeric entity ID like /entities/1 should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/1")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_negative_numeric_entity_id_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Negative numeric entity ID should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/-1")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_high_nonexistent_entity_id_returns_404(api_prefix: str) -> None:
    """Fuzzy test: High non-existent entity ID should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q99999999999")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_entity_prefix_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Invalid entity prefix like /entities/X123 should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/X123")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_entity_prefix_abc_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Invalid entity prefix like /entities/ABC should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/ABC")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_id_with_special_characters_returns_404(
    api_prefix: str,
) -> None:
    """Fuzzy test: Entity ID with special characters should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q$test")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_entity_id_with_percent_encoding_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Entity ID with percent encoding should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q%20test")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_very_long_entity_id_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Very long entity ID should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        long_id = "Q" + "a" * 1000
        response = await client.get(f"{api_prefix}/entities/{long_id}")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_revision_id_non_numeric_returns_422(api_prefix: str) -> None:
    """Fuzzy test: Non-numeric revision ID should return 422 (validation error)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/1/revision/abc")
        assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_revision_id_zero_returns_valid_response(api_prefix: str) -> None:
    """Fuzzy test: Revision ID zero returns valid response with rev_id=0."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/1/revision/0")
        assert response.status_code == 200
        data = response.json()
        assert data["rev_id"] == 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_revision_id_negative_returns_valid_response(api_prefix: str) -> None:
    """Fuzzy test: Negative revision ID returns valid response."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/1/revision/-1")
        assert response.status_code == 200
        data = response.json()
        assert data["rev_id"] == -1


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_statement_hash_non_numeric_returns_422(api_prefix: str) -> None:
    """Fuzzy test: Non-numeric statement hash should return 422 (validation error)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/statements/abc")
        assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_statement_hash_negative_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Negative statement hash should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/statements/-1")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_statement_hash_zero_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Zero statement hash should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/statements/0")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_label_hash_non_numeric_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Non-numeric label hash should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/labels/abc")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_label_hash_negative_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Negative label hash should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/labels/-1")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_limit_query_param_returns_422(api_prefix: str) -> None:
    """Fuzzy test: Invalid limit query parameter should return 422 (validation error)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?limit=-1")
        assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_limit_query_param_non_numeric_returns_422(
    api_prefix: str,
) -> None:
    """Fuzzy test: Non-numeric limit query parameter should return 422."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?limit=abc")
        assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_offset_query_param_negative_returns_422(api_prefix: str) -> None:
    """Fuzzy test: Negative offset query parameter should return 422."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?offset=-1")
        assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_offset_query_param_non_numeric_returns_422(
    api_prefix: str,
) -> None:
    """Fuzzy test: Non-numeric offset query parameter should return 422."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?offset=abc")
        assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_post_to_readonly_endpoint_returns_405(api_prefix: str) -> None:
    """Fuzzy test: POST to a read-only endpoint should return 405."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/Q1")
        assert response.status_code == 405


@pytest.mark.contract
@pytest.mark.asyncio
async def test_put_to_readonly_endpoint_returns_405(api_prefix: str) -> None:
    """Fuzzy test: PUT to a read-only endpoint should return 405."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(f"{api_prefix}/entities/Q1", json={})
        assert response.status_code == 405


@pytest.mark.contract
@pytest.mark.asyncio
async def test_patch_to_readonly_endpoint_returns_405(api_prefix: str) -> None:
    """Fuzzy test: PATCH to a read-only endpoint should return 405."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch(f"{api_prefix}/entities/Q1", json={})
        assert response.status_code == 405


@pytest.mark.contract
@pytest.mark.asyncio
async def test_malformed_json_body_returns_422(api_prefix: str) -> None:
    """Fuzzy test: Malformed JSON body should return 422."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            content=b"{invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_nonexistent_sitelink_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Non-existent sitelink should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q1/sitelinks/nonexistentwiki")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_nonexistent_lexeme_sense_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Non-existent lexeme sense should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/lexemes/senses/L9999999999-S1"
        )
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_nonexistent_lexeme_form_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Non-existent lexeme form should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/lexemes/forms/L9999999999-F1"
        )
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_invalid_entity_type_in_url_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Invalid entity type in URL should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/invalidtype/123")
        assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_double_slash_in_path_returns_404(api_prefix: str) -> None:
    """Fuzzy test: Double slash in path should return 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}//entities/Q1")
        assert response.status_code == 404
