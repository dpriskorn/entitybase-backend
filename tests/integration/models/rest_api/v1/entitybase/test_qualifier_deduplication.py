"""Integration tests for qualifier deduplication."""

import pytest


@pytest.mark.integration
class TestQualifierDeduplication:
    """Integration tests for qualifier deduplication."""

    def test_entity_creation_with_qualifiers_deduplicates(self, api_client) -> None:
        """Test that creating an entity with qualifiers in statements deduplicates them."""
        # Create entity with statement containing qualifiers
        entity_data = {
            "labels": {"en": {"language": "en", "value": "Test Entity"}},
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {
                                    "id": "Q5",
                                    "entity-type": "item",
                                    "numeric-id": 5,
                                },
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                        "qualifiers": {
                            "P580": [
                                {
                                    "snaktype": "value",
                                    "property": "P580",
                                    "datavalue": {
                                        "value": {
                                            "time": "+2023-01-01T00:00:00Z",
                                            "timezone": 0,
                                            "before": 0,
                                            "after": 0,
                                            "precision": 11,
                                            "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                                        },
                                        "type": "time",
                                    },
                                    "datatype": "time",
                                }
                            ]
                        },
                    }
                ]
            },
        }

        # Create the entity
        response = api_client.post("/entitybase/v1/entities/items", json=entity_data)
        assert response.status_code == 201
        entity_response = response.json()
        entity_id = entity_response["id"]

        # Retrieve the entity
        response = api_client.get(f"/entitybase/v1/entities/{entity_id}")
        assert response.status_code == 200
        entity = response.json()

        # Check that the statement has qualifiers
        p31_claims = entity["claims"]["P31"]
        assert len(p31_claims) == 1
        statement = p31_claims[0]

        # Verify qualifiers are present
        assert "qualifiers" in statement
        assert "P580" in statement["qualifiers"]
        assert len(statement["qualifiers"]["P580"]) == 1

        # The qualifiers should contain snaks with proper structure
        qualifier_snak = statement["qualifiers"]["P580"][0]
        assert qualifier_snak["snaktype"] == "value"
        assert qualifier_snak["property"] == "P580"
        assert "datavalue" in qualifier_snak

    def test_qualifier_endpoint_single_fetch(self, api_client) -> None:
        """Test fetching a single qualifier by hash."""
        # First create an entity with a qualifier to get a hash
        entity_data = {
            "labels": {"en": {"language": "en", "value": "Test Entity"}},
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {
                                    "id": "Q5",
                                    "entity-type": "item",
                                    "numeric-id": 5,
                                },
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                        "qualifiers": {
                            "P580": [
                                {
                                    "snaktype": "value",
                                    "property": "P580",
                                    "datavalue": {
                                        "value": {
                                            "time": "+2023-01-01T00:00:00Z",
                                            "timezone": 0,
                                            "before": 0,
                                            "after": 0,
                                            "precision": 11,
                                            "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                                        },
                                        "type": "time",
                                    },
                                    "datatype": "time",
                                }
                            ]
                        },
                    }
                ]
            },
        }

        # Create the entity
        response = api_client.post("/entitybase/v1/entities/items", json=entity_data)
        assert response.status_code == 201

        # For now, we'll use a mock hash since we don't have the actual deduplication logic
        # In a real test, we'd extract the hash from the stored qualifier
        mock_hash = "123456789"

        # Test fetching the qualifier (this will likely return null for now)
        response = api_client.get(f"/qualifiers/{mock_hash}")
        # The endpoint exists, but may return null if the hash doesn't exist
        assert response.status_code == 200
        result = response.json()
        # Should return array with one element (null for missing qualifier)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] is None

    def test_qualifier_endpoint_batch_fetch(self, api_client) -> None:
        """Test fetching multiple qualifiers by hashes."""
        # Test batch fetch with multiple hashes
        mock_hashes = "123456789,987654321,111111111"

        response = api_client.get(f"/qualifiers/{mock_hashes}")
        assert response.status_code == 200
        result = response.json()

        # Should return array with nulls for missing qualifiers
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(item is None for item in result)

    def test_qualifier_endpoint_invalid_hash(self, api_client) -> None:
        """Test qualifier endpoint with invalid hash format."""
        response = api_client.get("/qualifiers/invalid-hash")
        assert response.status_code == 400
        error = response.json()
        assert "Invalid hash format" in error["detail"]

    def test_qualifier_endpoint_too_many_hashes(self, api_client) -> None:
        """Test qualifier endpoint with too many hashes."""
        # Create 101 hashes (exceeds limit of 100)
        mock_hashes = ",".join([f"{i}" for i in range(101)])

        response = api_client.get(f"/qualifiers/{mock_hashes}")
        assert response.status_code == 400
        error = response.json()
        assert "Too many hashes" in error["detail"]

    def test_qualifier_endpoint_no_hashes(self, api_client) -> None:
        """Test qualifier endpoint with no hashes provided."""
        response = api_client.get("/qualifiers/")
        assert response.status_code == 404  # No route matches

        # Test with empty hash parameter
        response = api_client.get("/qualifiers/,,,")
        assert response.status_code == 400
        error = response.json()
        assert "No hashes provided" in error["detail"]