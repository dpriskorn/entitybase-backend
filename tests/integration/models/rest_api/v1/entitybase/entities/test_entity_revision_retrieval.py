import logging

import pytest
import requests

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_get_specific_revision_success(api_client: requests.Session, api_url: str) -> None:
    """Test getting a specific revision of an entity."""
    entity_data = EntityCreateRequest(
        id="Q71001",
        type="item",
        labels={"en": {"value": "Initial Label"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/Q71001/revision/1")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["labels"]["en"]["value"] == "Initial Label"


@pytest.mark.integration
def test_get_specific_revision_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test getting a non-existent revision returns 404."""
    response = api_client.get(f"{api_url}/entities/Q99999/revision/1")
    assert response.status_code == 404


@pytest.mark.integration
def test_get_specific_revision_ordering(api_client: requests.Session, api_url: str) -> None:
    """Test that revisions are returned in correct order."""
    entity_data = EntityCreateRequest(
        id="Q71002",
        type="item",
        labels={"en": {"value": "Initial Label"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q71002/labels/en",
        json={"language": "en", "value": "Updated Label"},
        headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/Q71002/revision/1")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["labels"]["en"]["value"] == "Initial Label"

    response = api_client.get(f"{api_url}/entities/Q71002/revision/2")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["labels"]["en"]["value"] == "Updated Label"


@pytest.mark.integration
def test_get_revision_json_success(api_client: requests.Session, api_url: str) -> None:
    """Test getting JSON representation of a specific revision."""
    entity_data = EntityCreateRequest(
        id="Q71003",
        type="item",
        labels={"en": {"value": "JSON Test"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/Q71003/revision/1/json")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["labels"]["en"]["value"] == "JSON Test"


@pytest.mark.integration
def test_get_revision_json_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test getting JSON for non-existent revision returns 404."""
    response = api_client.get(f"{api_url}/entities/Q99999/revision/1/json")
    assert response.status_code == 404


@pytest.mark.integration
def test_get_revision_ttl_success(api_client: requests.Session, api_url: str) -> None:
    """Test getting TTL representation of a specific revision."""
    entity_data = EntityCreateRequest(
        id="Q71004",
        type="item",
        labels={"en": {"value": "TTL Test"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/Q71004/revision/1/ttl")
    assert response.status_code == 200
    assert response.headers.get("content-type") in ["text/turtle; charset=utf-8", "text/turtle"]


@pytest.mark.integration
def test_get_revision_ttl_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test getting TTL for non-existent revision returns 404."""
    response = api_client.get(f"{api_url}/entities/Q99999/revision/1/ttl")
    assert response.status_code == 404


@pytest.mark.integration
def test_get_revision_ttl_formats(api_client: requests.Session, api_url: str) -> None:
    """Test getting TTL with different format options."""
    entity_data = EntityCreateRequest(
        id="Q71005",
        type="item",
        labels={"en": {"value": "Format Test"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
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
        response = api_client.get(
            f"{api_url}/entities/Q71005/revision/1/ttl",
            params={"format": format_},
        )
        assert response.status_code == 200
        assert content_types[format_] in response.headers.get("content-type", "")
