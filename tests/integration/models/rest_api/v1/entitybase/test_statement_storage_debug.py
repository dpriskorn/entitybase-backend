"""Integration test for diagnosing statement storage issues."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_statement_storage_diagnostic(api_prefix: str) -> None:
    """Diagnostic test to trace S3 statement storage and retrieval."""
    from models.rest_api.main import app

    entity_data = {
        "type": "item",
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
                    "qualifiers": {},
                    "references": [],
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        print(f"\n=== ENTITY CREATION ===")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Failed to create entity: {response.status_code}"
        entity_response = response.json()
        entity_id = entity_response["id"]
        print(f"Entity ID: {entity_id}")

        # Retrieve the entity
        print(f"\n=== ENTITY RETRIEVAL ===")
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        print(f"Status: {response.status_code}")
        entity = response.json()
        print(f"Entity keys: {list(entity.keys())}")
        
        # Get statement hashes from revision
        if "data" in entity and "revision" in entity["data"]:
            revision = entity["data"]["revision"]
            print(f"Revision keys: {list(revision.keys())}")
            
            if "hashes" in revision:
                hashes = revision["hashes"]
                print(f"Hashes keys: {list(hashes.keys())}")
                
                if "statements" in hashes:
                    statement_hashes = hashes["statements"]
                    print(f"Statement hashes: {statement_hashes}")
                    
                    # Try to resolve each statement hash
                    print(f"\n=== STATEMENT RESOLUTION ===")
                    for stmt_hash in statement_hashes:
                        print(f"\nResolving statement hash: {stmt_hash}")
                        resolve_response = await client.get(
                            f"{api_prefix}/resolve/statements/{stmt_hash}"
                        )
                        print(f"Resolve status: {resolve_response.status_code}")
                        print(f"Resolve response: {resolve_response.json()}")
                else:
                    print("No 'statements' key in hashes!")
            else:
                print("No 'hashes' key in revision!")
        else:
            print("No 'data' or 'revision' key in entity!")
            print(f"Entity keys: {list(entity.keys())}")
