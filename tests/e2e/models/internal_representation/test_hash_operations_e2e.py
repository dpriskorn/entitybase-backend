"""E2E tests for hash-based operations."""

import pytest


@pytest.mark.e2e
def test_batch_statements(
    e2e_api_client, e2e_base_url, sample_item_with_statements
) -> None:
    """E2E test: Retrieve multiple statements by their content hashes."""
    # Create entity with statements
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=sample_item_with_statements,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()

    # Get statement hashes
    entity_id = data["id"]
    response = e2e_api_client.get(f"{e2e_base_url}/entities/{entity_id}")
    assert response.status_code == 200
    entity_data = response.json()

    # Get batch statements
    statement_hashes = entity_data.get("statements", [])
    if statement_hashes:
        batch_request = {
            "content_hashes": statement_hashes[:1]  # Get first statement
        }
        response = e2e_api_client.post(
            f"{e2e_base_url}/entitybase/v1/statements/batch", json=batch_request
        )
        assert response.status_code == 200


@pytest.mark.e2e
def test_fetch_qualifiers(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Fetch qualifiers by hash(es)."""
    # Fetch qualifiers (may return empty if no hashes exist)
    response = e2e_api_client.get(f"{e2e_base_url}/qualifiers/123,456")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.e2e
def test_fetch_references(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Fetch references by hash(es)."""
    # Fetch references (may return empty if no hashes exist)
    response = e2e_api_client.get(f"{e2e_base_url}/references/123,456")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.e2e
def test_fetch_snaks(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Fetch snaks by hash(es)."""
    # Fetch snaks (may return empty if no hashes exist)
    response = e2e_api_client.get(f"{e2e_base_url}/snaks/123,456")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
