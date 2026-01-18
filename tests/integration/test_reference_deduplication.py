"""Integration tests for reference deduplication."""

import pytest
from models.test_helpers import TestClient


@pytest.mark.integration
class TestReferenceDeduplication:
    """Integration tests for reference deduplication."""

    def test_entity_creation_with_references_deduplicates(self, test_client: TestClient):
        """Test that creating an entity with references deduplicates them."""
        # Create entity with statement containing references
        entity_data = {
            "labels": {"en": {"language": "en", "value": "Test Entity"}},
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datavalue": {"value": {"id": "Q5", "entity-type": "item", "numeric-id": 5}, "type": "wikibase-entityid"}
                        },
                        "type": "statement",
                        "rank": "normal",
                        "references": [
                            {
                                "snaks": {
                                    "P854": [{"snaktype": "value", "property": "P854", "datavalue": {"value": "http://example.com", "type": "string"}}]
                                },
                                "snaks-order": ["P854"]
                            }
                        ]
                    }
                ]
            }
        }

        # Create entity
        response = test_client.post("/entities", json=entity_data)
        assert response.status_code == 201
        entity_id = response.json()["id"]

        # Read entity back
        response = test_client.get(f"/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()

        # Check that references are hashes, not full objects
        references = data["claims"]["P31"][0]["references"]
        assert isinstance(references, list)
        for ref in references:
            assert isinstance(ref, int)  # Should be rapidhash

        # Verify reference can be fetched
        ref_hash = references[0]
        response = test_client.get(f"/references/{ref_hash}")
        assert response.status_code == 200
        ref_data = response.json()
        assert "snaks" in ref_data

    def test_reference_batch_endpoint(self, test_client: TestClient):
        """Test batch reference fetching."""
        # Assume some references exist from previous test
        response = test_client.get("/references/123,456")
        # Should return array with nulls for missing
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)