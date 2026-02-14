"""Integration tests for unified entity term endpoints.

Tests that both items (Q) and properties (P) work identically through the
unified /entities/{entity_id}/... endpoints.
"""

import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
class TestUnifiedLabelEndpoints:
    """Test unified label endpoints work for both items and properties."""

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_get_label_success(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test getting label for language works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71001"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            labels={"en": {"value": f"Test {entity_type.title()} Label"}},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/en")
            assert response.status_code == 200
            data = response.json()
            assert "value" in data

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_update_label_via_put(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test updating label via PUT works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71002"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            labels={"en": {"value": "Original Label"}},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.put(
                f"{api_prefix}/entities/{entity_id}/labels/en",
                json={"language": "en", "value": "Updated Label"},
                headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
            )
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_add_label_via_post(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test adding label via POST works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71003"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            labels={"en": {"value": "English Label"}},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.post(
                f"{api_prefix}/entities/{entity_id}/labels/de",
                json={"language": "de", "value": "German Label"},
                headers={"X-Edit-Summary": "add label", "X-User-ID": "0"},
            )
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_delete_label(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test deleting label works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71004"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            labels={"en": {"value": "Label to Delete"}, "de": {"value": "Keep This"}},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.delete(
                f"{api_prefix}/entities/{entity_id}/labels/en",
                headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
            )
            assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
class TestUnifiedDescriptionEndpoints:
    """Test unified description endpoints work for both items and properties."""

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_get_description_success(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test getting description works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71005"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            descriptions={"en": {"value": f"Test {entity_type.title()} Description"}},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.get(
                f"{api_prefix}/entities/{entity_id}/descriptions/en"
            )
            assert response.status_code == 200
            data = response.json()
            assert "value" in data

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_add_description_via_post(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test adding description via POST works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71006"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            descriptions={"en": {"value": "English Description"}},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.post(
                f"{api_prefix}/entities/{entity_id}/descriptions/fr",
                json={"language": "fr", "value": "French Description"},
                headers={"X-Edit-Summary": "add description", "X-User-ID": "0"},
            )
            assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
class TestUnifiedAliasEndpoints:
    """Test unified alias endpoints work for both items and properties."""

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_get_aliases_success(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test getting aliases works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71007"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}]},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_update_aliases_via_put(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test updating aliases via PUT works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71008"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            aliases={"en": [{"value": "Old Alias"}]},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.put(
                f"{api_prefix}/entities/{entity_id}/aliases/en",
                json=["New Alias 1", "New Alias 2"],
                headers={"X-Edit-Summary": "update aliases", "X-User-ID": "0"},
            )
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_add_single_alias_via_post(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test adding single alias via POST works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71009"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            labels={"en": {"value": "Test Entity"}},
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.post(
                f"{api_prefix}/entities/{entity_id}/aliases/en",
                json={"language": "en", "value": "New Alias"},
                headers={"X-Edit-Summary": "add alias", "X-User-ID": "0"},
            )
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "entity_type,entity_prefix", [("item", "Q"), ("property", "P")]
    )
    async def test_delete_aliases(
        self, api_prefix: str, entity_type: str, entity_prefix: str
    ) -> None:
        """Test deleting aliases works for both items and properties."""
        from models.rest_api.main import app

        entity_id = f"{entity_prefix}71010"
        entity_data = EntityCreateRequest(
            id=entity_id,
            type=entity_type,
            aliases={
                "en": [{"value": "Alias 1"}, {"value": "Alias 2"}],
                "de": [{"value": "Alias DE"}],
            },
            edit_summary="test",
            datatype="wikibase-item" if entity_type == "property" else None,
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            plural = "properties" if entity_type == "property" else f"{entity_type}s"
            create_url = f"{api_prefix}/entities/{plural}"
            response = await client.post(
                create_url,
                json=entity_data.model_dump(mode="json", exclude_none=True),
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.delete(
                f"{api_prefix}/entities/{entity_id}/aliases/en",
                headers={"X-Edit-Summary": "delete aliases", "X-User-ID": "0"},
            )
            assert response.status_code == 200

            response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/de")
            assert response.status_code == 200
