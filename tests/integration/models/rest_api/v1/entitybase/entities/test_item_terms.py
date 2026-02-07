import logging

import pytest
import requests

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_get_item_label_success(api_client: requests.Session, api_url: str) -> None:
    """Test getting item label for language."""
    entity_data = EntityCreateRequest(
        id="Q70001",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )
    url = f"{api_url}/entities/items"
    logger.debug(f"sending API post request to {url}")
    response = api_client.post(
        url,
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    # logger.debug("Got response")
    assert response.status_code == 200
    logger.debug("Got 200 response")

    url2 = f"{api_url}/entities/items/Q70001/labels/en"
    logger.debug(f"sending API get request to {url2}")
    response = api_client.get(url2)
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert data["value"] == "Test Label"


@pytest.mark.integration
def test_get_item_label_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test getting item label for non-existent language returns 404."""
    entity_data = EntityCreateRequest(
        id="Q70002",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/items/Q70002/labels/de")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.integration
def test_get_item_label_multiple_languages(api_client: requests.Session, api_url: str) -> None:
    """Test getting item labels for multiple languages."""
    entity_data = EntityCreateRequest(
        id="Q70003",
        type="item",
        labels={
            "en": {"value": "Test English"},
            "de": {"value": "Test German"},
            "fr": {"value": "Test French"},
        },
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    for lang, expected in [("en", "Test English"), ("de", "Test German"), ("fr", "Test French")]:
        response = api_client.get(f"{api_url}/entities/items/Q70003/labels/{lang}")
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == expected


@pytest.mark.integration
def test_update_item_label_success(api_client: requests.Session, api_url: str) -> None:
    """Test updating item label for language."""
    entity_data = EntityCreateRequest(
        id="Q70004",
        type="item",
        labels={"en": {"value": "Original Label"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q70004/labels/en",
        json={"language": "en", "value": "Updated Label"},
        headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["labels"]["en"]["value"] == "Updated Label"


@pytest.mark.integration
def test_update_item_label_creates_new(api_client: requests.Session, api_url: str) -> None:
    """Test updating item label creates new language if not exists."""
    entity_data = EntityCreateRequest(
        id="Q70005",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q70005/labels/de",
        json={"language": "de", "value": "Neues Label"},
        headers={"X-Edit-Summary": "add german label", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "de" in data["data"]["labels"]
    assert data["data"]["labels"]["de"]["value"] == "Neues Label"


@pytest.mark.integration
def test_update_item_label_entity_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test updating item label for non-existent entity returns 404."""
    response = api_client.put(
        f"{api_url}/entities/items/Q99999/labels/en",
        json={"language": "en", "value": "Updated Label"},
        headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_item_label_success(api_client: requests.Session, api_url: str) -> None:
    """Test deleting item label for language."""
    entity_data = EntityCreateRequest(
        id="Q70006",
        type="item",
        labels={"en": {"value": "Label to Delete"}, "de": {"value": "German Label"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.delete(
        f"{api_url}/entities/items/Q70006/labels/en",
        headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "en" not in data["data"]["labels"]
    assert "de" in data["data"]["labels"]


@pytest.mark.integration
def test_delete_item_label_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test deleting non-existent item label returns 404."""
    entity_data = EntityCreateRequest(
        id="Q70007",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.delete(
        f"{api_url}/entities/items/Q70007/labels/de",
        headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_delete_item_label_entity_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test deleting item label for non-existent entity returns 404."""
    response = api_client.delete(
        f"{api_url}/entities/items/Q99999/labels/en",
        headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_get_item_description_success(api_client: requests.Session, api_url: str) -> None:
    """Test getting item description for language."""
    entity_data = EntityCreateRequest(
        id="Q70008",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/items/Q70008/descriptions/en")
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert data["value"] == "Test Description"


@pytest.mark.integration
def test_get_item_description_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test getting item description for non-existent language returns 404."""
    entity_data = EntityCreateRequest(
        id="Q70009",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/items/Q70009/descriptions/de")
    assert response.status_code == 404


@pytest.mark.integration
def test_update_item_description_success(api_client: requests.Session, api_url: str) -> None:
    """Test updating item description for language."""
    entity_data = EntityCreateRequest(
        id="Q70010",
        type="item",
        descriptions={"en": {"value": "Original Description"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q70010/descriptions/en",
        json={"language": "en", "value": "Updated Description"},
        headers={"X-Edit-Summary": "update description", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["descriptions"]["en"]["value"] == "Updated Description"


@pytest.mark.integration
def test_update_item_description_creates_new(api_client: requests.Session, api_url: str) -> None:
    """Test updating item description creates new language if not exists."""
    entity_data = EntityCreateRequest(
        id="Q70011",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q70011/descriptions/de",
        json={"language": "de", "value": "Neue Beschreibung"},
        headers={"X-Edit-Summary": "add german description", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "de" in data["data"]["descriptions"]
    assert data["data"]["descriptions"]["de"]["value"] == "Neue Beschreibung"


@pytest.mark.integration
def test_delete_item_description_success(api_client: requests.Session, api_url: str) -> None:
    """Test deleting item description for language."""
    entity_data = EntityCreateRequest(
        id="Q70012",
        type="item",
        descriptions={"en": {"value": "Description to Delete"}, "de": {"value": "German Description"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.delete(
        f"{api_url}/entities/items/Q70012/descriptions/en",
        headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "en" not in data["data"]["descriptions"]
    assert "de" in data["data"]["descriptions"]


@pytest.mark.integration
def test_delete_item_description_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test deleting non-existent item description returns 404."""
    entity_data = EntityCreateRequest(
        id="Q70013",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.delete(
        f"{api_url}/entities/items/Q70013/descriptions/de",
        headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_get_item_aliases_success(api_client: requests.Session, api_url: str) -> None:
    """Test getting item aliases for language."""
    entity_data = EntityCreateRequest(
        id="Q70014",
        type="item",
        aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}]},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/items/Q70014/aliases/en")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "Alias 1" in data
    assert "Alias 2" in data


@pytest.mark.integration
def test_get_item_aliases_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test getting item aliases for non-existent language returns 404."""
    entity_data = EntityCreateRequest(
        id="Q70015",
        type="item",
        aliases={"en": [{"value": "Test Alias"}]},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/items/Q70015/aliases/de")
    assert response.status_code == 404


@pytest.mark.integration
def test_get_item_aliases_multiple(api_client: requests.Session, api_url: str) -> None:
    """Test getting multiple item aliases for language."""
    entity_data = EntityCreateRequest(
        id="Q70016",
        type="item",
        aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}, {"value": "Alias 3"}]},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.get(f"{api_url}/entities/items/Q70016/aliases/en")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.integration
def test_update_item_aliases_replace(api_client: requests.Session, api_url: str) -> None:
    """Test updating item aliases replaces existing ones."""
    entity_data = EntityCreateRequest(
        id="Q70017",
        type="item",
        aliases={"en": [{"value": "Old Alias 1"}, {"value": "Old Alias 2"}]},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q70017/aliases/en",
        json=["New Alias 1", "New Alias 2"],
        headers={"X-Edit-Summary": "replace aliases", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    aliases = data["data"]["aliases"]["en"]
    assert len(aliases) == 2
    assert aliases[0]["value"] == "New Alias 1"
    assert aliases[1]["value"] == "New Alias 2"


@pytest.mark.integration
def test_update_item_aliases_add(api_client: requests.Session, api_url: str) -> None:
    """Test updating item aliases creates new if not exists."""
    entity_data = EntityCreateRequest(
        id="Q70018",
        type="item",
        labels={"en": {"value": "Test Item"}},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q70018/aliases/en",
        json=["Alias 1", "Alias 2"],
        headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "en" in data["data"]["aliases"]
    assert len(data["data"]["aliases"]["en"]) == 2


@pytest.mark.integration
def test_update_item_aliases_clear(api_client: requests.Session, api_url: str) -> None:
    """Test updating item aliases with empty list clears them."""
    entity_data = EntityCreateRequest(
        id="Q70019",
        type="item",
        aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}]},
        edit_summary="test",
    )

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    response = api_client.put(
        f"{api_url}/entities/items/Q70019/aliases/en",
        json=[],
        headers={"X-Edit-Summary": "clear aliases", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "en" not in data["data"]["aliases"] or len(data["data"]["aliases"]["en"]) == 0
