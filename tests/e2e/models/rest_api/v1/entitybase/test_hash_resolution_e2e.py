"""E2E tests for hash resolution endpoints.

Tests for resolving qualifiers, references, snaks, glosses, representations,
and batch statement operations.
"""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_qualifiers_by_hashes(api_prefix: str) -> None:
    """E2E test: Fetch qualifiers by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/qualifiers/123,456,789")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_single_qualifier_by_hash(api_prefix: str) -> None:
    """E2E test: Fetch a single qualifier by hash."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/qualifiers/123")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_references_by_hashes(api_prefix: str) -> None:
    """E2E test: Fetch references by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/references/123,456,789")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_single_reference_by_hash(api_prefix: str) -> None:
    """E2E test: Fetch a single reference by hash."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/references/123")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_snaks_by_hashes(api_prefix: str) -> None:
    """E2E test: Fetch snaks by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/snaks/123,456,789")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_single_snak_by_hash(api_prefix: str) -> None:
    """E2E test: Fetch a single snak by hash."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/snaks/123")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_glosses_by_hashes(api_prefix: str) -> None:
    """E2E test: Fetch sense glosses by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/glosses/123,456,789")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_single_gloss_by_hash(api_prefix: str) -> None:
    """E2E test: Fetch a single gloss by hash."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/glosses/123")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_representations_by_hashes(api_prefix: str) -> None:
    """E2E test: Fetch form representations by hash(es)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/representations/123,456,789")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_single_representation_by_hash(api_prefix: str) -> None:
    """E2E test: Fetch a single representation by hash."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/representations/123")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_batch_statements(api_prefix: str) -> None:
    """E2E test: Get batch statements for entities and properties."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity with statements
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Batch Test"}},
            "statements": [
                {
                    "property": {"id": "P31", "data_type": "wikibase-item"},
                    "value": {"type": "value", "content": "Q5"},
                    "rank": "normal",
                }
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Get batch statements
        batch_data = {"entity_ids": [entity_id], "property_ids": ["P31"]}
        response = await client.get(
            f"{api_prefix}/entitybase/v1/statements/batch",
            params=batch_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_post_batch_statements(api_prefix: str) -> None:
    """E2E test: Retrieve multiple statements by their content hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Get batch statements by hash
        response = await client.get(f"{api_prefix}/resolve/statements/123,456,789")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_empty_hashes_result(api_prefix: str) -> None:
    """E2E test: Get empty result for non-existent hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # All hash resolution endpoints should handle non-existent hashes gracefully
        endpoints_to_test = [
            f"{api_prefix}/resolve/qualifiers/999999999",
            f"{api_prefix}/resolve/references/999999999",
            f"{api_prefix}/resolve/snaks/999999999",
            f"{api_prefix}/resolve/glosses/999999999",
            f"{api_prefix}/resolve/representations/999999999",
        ]

        for endpoint in endpoints_to_test:
            response = await client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            # Should return empty dict or dict with null values
            assert isinstance(data, dict)
