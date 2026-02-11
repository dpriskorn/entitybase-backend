"""E2E tests for batch entity data operations."""

import pytest
import sys

sys.path.insert(0, "src")


@pytest.mark.e2e
def test_batch_aliases(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Get batch aliases by hashes."""
    # Create entity
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Get batch aliases (may return empty if no hashes exist yet)
    response = await client.get(
        f"{e2e_base_url}/v1/entitybase/entities/aliases/123,456"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.e2e
def test_batch_descriptions(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Get batch descriptions by hashes."""
    # Create entity
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Get batch descriptions (may return empty if no hashes exist yet)
    response = await client.get(
        f"{e2e_base_url}/v1/entitybase/entities/descriptions/123,456"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.e2e
def test_batch_labels(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Get batch labels by hashes."""
    # Create entity
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Get batch labels (may return empty if no hashes exist yet)
    response = await client.get(f"{e2e_base_url}/v1/entitybase/entities/labels/123,456")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.e2e
def test_batch_sitelinks(e2e_api_client, e2e_base_url, sample_item_data) -> None:
    """E2E test: Get batch sitelink titles by hashes."""
    # Create entity
    response = await client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Get batch sitelinks (may return empty if no hashes exist yet)
    response = await client.get(
        f"{e2e_base_url}/v1/entitybase/entities/sitelinks/123,456"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
