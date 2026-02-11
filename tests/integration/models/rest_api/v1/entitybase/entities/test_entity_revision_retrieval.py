import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_specific_revision_success(api_prefix: str) -> None:
    """Test getting a specific revision of an entity."""
    from models.rest_api.main import app

    from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

    entity_data = EntityCreateRequest(
        id="Q71001",
        type="item",
        labels={"en": {"value": "Initial Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q71001/revision/1")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["labels"]["en"]["value"] == "Initial Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_specific_revision_not_found(api_prefix: str) -> None:
    """Test getting a non-existent revision returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q99999/revision/1")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_specific_revision_ordering(api_prefix: str) -> None:
    """Test that revisions are returned in correct order."""
    from models.rest_api.main import app

    from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

    entity_data = EntityCreateRequest(
        id="Q71002",
        type="item",
        labels={"en": {"value": "Initial Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q71002/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q71002/revision/1")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["labels"]["en"]["value"] == "Initial Label"

        response = await client.get(f"{api_prefix}/entities/Q71002/revision/2")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["labels"]["en"]["value"] == "Updated Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_revision_json_success(api_prefix: str) -> None:
    """Test getting JSON representation of a specific revision."""
    from models.rest_api.main import app

    from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

    entity_data = EntityCreateRequest(
        id="Q71003",
        type="item",
        labels={"en": {"value": "JSON Test"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q71003/revision/1/json")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["labels"]["en"]["value"] == "JSON Test"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_revision_json_not_found(api_prefix: str) -> None:
    """Test getting JSON for non-existent revision returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q99999/revision/1/json")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_revision_ttl_success(api_prefix: str) -> None:
    """Test getting TTL representation of a specific revision."""
    from models.rest_api.main import app

    from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

    entity_data = EntityCreateRequest(
        id="Q71004",
        type="item",
        labels={"en": {"value": "TTL Test"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q71004/revision/1/ttl")
        assert response.status_code == 200
        assert response.headers.get("content-type") in [
            "text/turtle; charset=utf-8",
            "text/turtle",
        ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_revision_ttl_not_found(api_prefix: str) -> None:
    """Test getting TTL for non-existent revision returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q99999/revision/1/ttl")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_revision_ttl_formats(api_prefix: str) -> None:
    """Test getting TTL with different format options."""
    from models.rest_api.main import app

    from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

    entity_data = EntityCreateRequest(
        id="Q71005",
        type="item",
        labels={"en": {"value": "Format Test"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        formats = ["turtle", "rdfxml", "ntriples"]
        content_types = {
            "turtle": "text/turtle",
            "rdfxml": "application/rdf+xml",
            "ntriples": "application/n-triples",
        }

        for format_ in formats:
            response = await client.get(
                f"{api_prefix}/entities/Q71005/revision/1/ttl",
                params={"format": format_},
            )
            assert response.status_code == 200
            assert content_types[format_] in response.headers.get("content-type", "")
