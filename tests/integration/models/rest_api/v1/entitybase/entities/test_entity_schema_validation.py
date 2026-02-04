from pathlib import Path

import pytest
import yaml
from pathlib import Path
from jsonschema import Draft202012Validator
from typing import Any, cast


@pytest.mark.integration
class TestEntitySchemaValidation:
    """Validate /entities/{entity_id}.json responses against entity schema."""

    @pytest.fixture
    def entity_schema(self) -> dict:
        """Load entity schema."""
        schema_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "schemas"
            / "entitybase"
            / "entity"
            / "1.0.0"
            / "schema.yaml"
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            return cast(dict[str, Any], yaml.safe_load(f))

    @pytest.fixture
    def schema_validator(self, entity_schema: dict) -> Draft202012Validator:
        """Create schema validator."""
        return Draft202012Validator(entity_schema)

    def test_schema_loads_successfully(self, entity_schema: dict) -> None:
        """Test that schema can be loaded and is valid."""
        assert entity_schema is not None
        assert "type" in entity_schema
        assert entity_schema["type"] == "object"

    def test_create_item_and_validate_json_response(
        self,
        api_client: requests.Session,
        base_url: str,
        schema_validator: Draft202012Validator,
    ) -> None:
        """Create item via POST and validate JSON response against schema."""
        item_data = {
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Test Entity for Schema Validation"}
            },
            "edit_summary": "Test entity for schema validation"
        }

        response = api_client.post(
            f"{base_url}/entitybase/v1/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        create_result = response.json()
        entity_id = create_result["id"]
        assert entity_id.startswith("Q")

        json_response = api_client.get(f"{base_url}/entitybase/v1/entities/{entity_id}.json")
        assert json_response.status_code == 200
        entity_data = json_response.json()["data"]

        errors = list(schema_validator.iter_errors(entity_data))
        if errors:
            error_list = [
                f"Path: {'/'.join(str(p) for p in error.path) if error.path else '/'}"
                f" | Error: {error.message}"
                for error in errors
            ]
            pytest.fail(f"Schema validation failed:\n" + "\n".join(error_list))

        assert "id" in entity_data
        assert "type" in entity_data
        assert entity_data["type"] == "item"
        assert entity_data["id"].startswith("Q")

    def test_required_fields_present(
        self,
        api_client: requests.Session,
        base_url: str,
    ) -> None:
        """Verify required fields are present in response."""
        item_data = {
            "type": "item",
            "edit_summary": "Test required fields"
        }
        response = api_client.post(
            f"{base_url}/entitybase/v1/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        json_response = api_client.get(f"{base_url}/entitybase/v1/entities/{entity_id}.json")
        entity_data = json_response.json()["data"]

        assert "id" in entity_data
        assert "type" in entity_data

    def test_item_with_descriptions_validates(
        self,
        api_client: requests.Session,
        base_url: str,
        schema_validator: Draft202012Validator,
    ) -> None:
        """Test that items with descriptions validate against schema."""
        item_data = {
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Test Item"}
            },
            "descriptions": {
                "en": {"language": "en", "value": "A test item with descriptions"}
            },
            "edit_summary": "Test item with descriptions"
        }

        response = api_client.post(
            f"{base_url}/entitybase/v1/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        json_response = api_client.get(f"{base_url}/entitybase/v1/entities/{entity_id}.json")
        entity_data = json_response.json()["data"]

        errors = list(schema_validator.iter_errors(entity_data))
        if errors:
            pytest.fail(f"Schema validation failed: {errors[0].message}")

        assert "descriptions" in entity_data
        assert "en" in entity_data["descriptions"]

    def test_item_with_claims_validates(
        self,
        api_client: requests.Session,
        base_url: str,
        schema_validator: Draft202012Validator,
    ) -> None:
        """Test that items with claims validate against schema."""
        item_data = {
            "type": "item",
            "labels": {
                "en": {"language": "en", "value": "Test Item"}
            },
            "claims": {
                "P31": [{
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid"
                        }
                    },
                    "type": "statement",
                    "rank": "normal"
                }]
            },
            "edit_summary": "Test item with claims"
        }

        response = api_client.post(
            f"{base_url}/entitybase/v1/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        json_response = api_client.get(f"{base_url}/entitybase/v1/entities/{entity_id}.json")
        entity_data = json_response.json()["data"]

        errors = list(schema_validator.iter_errors(entity_data))
        if errors:
            pytest.fail(f"Schema validation failed: {errors[0].message}")

        assert "claims" in entity_data
        assert "P31" in entity_data["claims"]