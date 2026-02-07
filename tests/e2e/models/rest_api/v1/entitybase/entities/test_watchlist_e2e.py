"""E2E tests for watchlist operations."""

import pytest


@pytest.mark.e2e
def test_add_watch(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Add a watchlist entry for user."""
    # Create user
    user_data = {"user_id": 90006}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Create entity
    entity_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Watch Test"}},
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=entity_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    entity_id = response.json()["id"]

    # Add watch
    watch_data = {"entity_id": entity_id, "properties": ["P31"]}
    response = e2e_api_client.post(
        f"{e2e_base_url}/users/90006/watchlist", json=watch_data
    )
    assert response.status_code == 200


@pytest.mark.e2e
def test_get_watchlist(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get user's watchlist."""
    # Create user
    user_data = {"user_id": 90007}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Create entity
    entity_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Watchlist Test"}},
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=entity_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    entity_id = response.json()["id"]

    # Add watch
    watch_data = {"entity_id": entity_id, "properties": ["P31"]}
    e2e_api_client.post(f"{e2e_base_url}/users/90007/watchlist", json=watch_data)

    # Get watchlist
    response = e2e_api_client.get(f"{e2e_base_url}/users/90007/watchlist")
    assert response.status_code == 200
    data = response.json()
    assert "watches" in data
    assert len(data["watches"]) > 0


@pytest.mark.e2e
def test_remove_watch_by_id(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Remove a watchlist entry by ID."""
    # Create user
    user_data = {"user_id": 90008}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Create entity
    entity_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Watch Remove Test"}},
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=entity_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    entity_id = response.json()["id"]

    # Add watch
    watch_data = {"entity_id": entity_id, "properties": ["P31"]}
    e2e_api_client.post(f"{e2e_base_url}/users/90008/watchlist", json=watch_data)

    # Get watchlist to get watch ID
    response = e2e_api_client.get(f"{e2e_base_url}/users/90008/watchlist")
    watch_id = response.json()["watches"][0]["id"]

    # Remove by ID
    response = e2e_api_client.delete(f"{e2e_base_url}/users/90008/watchlist/{watch_id}")
    assert response.status_code in [200, 204]


@pytest.mark.e2e
def test_toggle_watchlist(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Enable or disable watchlist for user."""
    # Create user
    user_data = {"user_id": 90009}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Toggle watchlist
    toggle_data = {"enabled": True}
    response = e2e_api_client.put(
        f"{e2e_base_url}/users/90009/watchlist/toggle", json=toggle_data
    )
    assert response.status_code == 200


@pytest.mark.e2e
def test_remove_watch_by_entity(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Remove a watchlist entry by entity."""
    # Create user
    user_data = {"user_id": 90010}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Create entity
    entity_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Watch Remove Entity Test"}},
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/entities/items",
        json=entity_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    entity_id = response.json()["id"]

    # Add watch
    watch_data = {"entity_id": entity_id, "properties": ["P31"]}
    e2e_api_client.post(f"{e2e_base_url}/users/90010/watchlist", json=watch_data)

    # Remove by entity
    response = e2e_api_client.post(
        f"{e2e_base_url}/users/90010/watchlist/remove", json={"entity_id": entity_id}
    )
    assert response.status_code == 200


@pytest.mark.e2e
def test_get_watchlist_stats(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get user's watchlist statistics."""
    # Create user
    user_data = {"user_id": 90011}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Get watchlist stats
    response = e2e_api_client.get(f"{e2e_base_url}/users/90011/watchlist/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_watches" in data or "count" in data


@pytest.mark.e2e
def test_get_watchlist_notifications(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Get user's recent watchlist notifications."""
    # Create user
    user_data = {"user_id": 90012}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Get notifications
    response = e2e_api_client.get(
        f"{e2e_base_url}/users/90012/watchlist/notifications?hours=24&limit=50&offset=0"
    )
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "notifications" in data


@pytest.mark.e2e
def test_mark_notification_checked(e2e_api_client, e2e_base_url) -> None:
    """E2E test: Mark a notification as checked."""
    # Create user
    user_data = {"user_id": 90013}
    e2e_api_client.post(f"{e2e_base_url}/users", json=user_data)

    # Mark notification as checked
    response = e2e_api_client.put(
        f"{e2e_base_url}/users/90013/watchlist/notifications/123/check"
    )
    # May succeed even if notification doesn't exist (idempotent)
    assert response.status_code in [200, 404]
