"""Integration tests for qualifier deduplication."""

import pytest


@pytest.mark.integration
class TestQualifierDeduplication:
    """Integration tests for qualifier deduplication."""

    def test_entity_creation_with_qualifiers_deduplicates(self, api_client) -> None:
        """Test that creating an entity with qualifiers in statements stores them as hash references."""
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

        # Verify qualifiers field is an integer hash, not an object
        assert "qualifiers" in statement
        assert isinstance(statement["qualifiers"], int)
        assert statement["qualifiers"] > 0

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
        entity_response = response.json()
        entity_id = entity_response["id"]

        # Retrieve the entity to get the qualifier hash
        response = api_client.get(f"/entitybase/v1/entities/{entity_id}")
        assert response.status_code == 200
        entity = response.json()

        # Extract the qualifier hash from the response
        statement = entity["claims"]["P31"][0]
        qualifier_hash = statement["qualifiers"]
        assert isinstance(qualifier_hash, int)

        # Test fetching the qualifier
        response = api_client.get(f"/qualifiers/{qualifier_hash}")
        assert response.status_code == 200
        result = response.json()
        # Should return array with one element containing the qualifier data
        assert isinstance(result, list)
        assert len(result) == 1
        # The qualifier should contain the snak structure
        assert result[0] is not None

    def test_qualifier_endpoint_batch_fetch(self, api_client) -> None:
        """Test fetching multiple qualifiers by hashes."""
        # Create an entity with multiple statements having different qualifiers
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
                    },
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {
                                    "id": "Q6",
                                    "entity-type": "item",
                                    "numeric-id": 6,
                                },
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                        "qualifiers": {
                            "P582": [
                                {
                                    "snaktype": "value",
                                    "property": "P582",
                                    "datavalue": {
                                        "value": {
                                            "time": "+2024-01-01T00:00:00Z",
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
                    },
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {
                                "value": {
                                    "id": "Q7",
                                    "entity-type": "item",
                                    "numeric-id": 7,
                                },
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                        "qualifiers": {
                            "P585": [
                                {
                                    "snaktype": "value",
                                    "property": "P585",
                                    "datavalue": {
                                        "value": {
                                            "time": "+2025-01-01T00:00:00Z",
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

        # Retrieve the entity to get qualifier hashes
        response = api_client.get(f"/entitybase/v1/entities/{entity_id}")
        assert response.status_code == 200
        entity = response.json()

        # Extract 2-3 different qualifier hashes
        p31_claims = entity["claims"]["P31"]
        qualifier_hashes = [claim["qualifiers"] for claim in p31_claims[:2]]

        # Convert to comma-separated string for batch API call
        hashes_str = ",".join(str(h) for h in qualifier_hashes)

        # Test batch fetch
        response = api_client.get(f"/qualifiers/{hashes_str}")
        assert response.status_code == 200
        result = response.json()

        # Should return array with qualifier data
        assert isinstance(result, list)
        assert len(result) == 2
        # All qualifiers should be present
        assert all(item is not None for item in result)

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