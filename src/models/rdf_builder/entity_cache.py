"""RDF entity cache."""

import json
import logging
import time
from pathlib import Path

import requests

from models.rest_api.entitybase.v1.response import (
    EntityMetadataResponse,
    EntityMetadataBatchResponse,
)
from models.rest_api.entitybase.v1.response.entity.entitybase import (
    EntityAliasesResponse,
    EntityDescriptionsResponse,
)
from models.rest_api.entitybase.v1.response.entity.entitybase import (
    EntityLabelsResponse,
    EntitySitelinksResponse,
    EntityStatementsResponse,
)
from models.rest_api.entitybase.v1.response.rdf import MetadataLoadResponse

logger = logging.getLogger(__name__)


def fetch_entity_metadata_batch(entity_ids: list[str]) -> EntityMetadataBatchResponse:
    """Fetch labels and descriptions for multiple entities via SPARQL."""
    if not entity_ids:
        return EntityMetadataBatchResponse(metadata={})

    batch_size = 100
    results: dict[str, EntityMetadataResponse | None] = {}

    for i in range(0, len(entity_ids), batch_size):
        batch = entity_ids[i : i + batch_size]
        values_clause = " ".join([f"wd:{eid}" for eid in batch])

        query = f"""
        SELECT ?entity ?label ?description WHERE {{
          VALUES ?entity {{ {values_clause} }} .
          OPTIONAL {{ ?entity rdfs:label ?label . FILTER(LANG(?label) = 'en') }}
          OPTIONAL {{ ?entity schema:description ?description . FILTER(LANG(?description) = 'en') }}
        }}
        """

        try:
            response = requests.post(
                "https://query.wikidata.org/sparql",
                params={"query": query, "format": "json"},
                timeout=60,
                headers={
                    "User-Agent": "WikibaseBackend/1.0 (research@wikibase-backend.org)"
                },
            )
            response.raise_for_status()

            for row in response.json()["results"]["bindings"]:
                entity_uri = row["entity"]["value"]
                entity_id = entity_uri.rsplit("/", 1)[-1]
                label = row.get("label", {}).get("value", "")
                description = row.get("description", {}).get("value", "")

                metadata = {"id": entity_id}
                if label:
                    metadata["labels"] = {"en": {"language": "en", "value": label}}
                if description:
                    metadata["descriptions"] = {
                        "en": {"language": "en", "value": description}
                    }

                results[entity_id] = EntityMetadataResponse(  # type: ignore
                    id=metadata["id"],
                    labels=EntityLabelsResponse(data=metadata.get("labels", {})),
                    descriptions=EntityDescriptionsResponse(
                        data=metadata.get("descriptions", {})
                    ),
                    aliases=EntityAliasesResponse(data=metadata.get("aliases", {})),
                    statements=EntityStatementsResponse(
                        data=metadata.get("statements", [])
                    ),
                    sitelinks=EntitySitelinksResponse(
                        data=metadata.get("sitelinks", {})
                    ),
                )

            logger.info(
                f"Fetched metadata for {len(batch)} entities (batch {i // batch_size + 1})"
            )
            time.sleep(2)

        except Exception as e:
            logger.error(f"Failed to fetch batch {i // batch_size + 1}: {e}")
            for entity_id in batch:
                results[entity_id] = None

    return EntityMetadataBatchResponse(metadata=results)


def load_entity_metadata_batch(
    entity_ids: list[str], metadata_dir: Path
) -> MetadataLoadResponse:
    """Fetch and save metadata for multiple entities.

    Args:
        entity_ids: List of entity IDs to fetch metadata for
        metadata_dir: Directory to save metadata files

    Returns:
        MetadataLoadResponse with results mapping entity_id to success status (True/False)
    """
    metadata_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    fetched_metadata = fetch_entity_metadata_batch(entity_ids)

    for entity_id, metadata in fetched_metadata.metadata.items():
        if metadata:
            output_path = metadata_dir / f"{entity_id}.json"
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(metadata.model_dump(), f, indent=2, ensure_ascii=False)
                logger.info(f"Saved metadata for {entity_id} to {output_path}")
                results[entity_id] = True
            except Exception as e:
                logger.error(f"Failed to serialize metadata for {entity_id}: {e}")
                if output_path.exists():
                    output_path.unlink()
                results[entity_id] = False
        else:
            logger.warning(f"Failed to fetch metadata for {entity_id}")
            results[entity_id] = False

    return MetadataLoadResponse(results=results)


def load_entity_metadata(entity_id: str, metadata_dir: Path) -> EntityMetadataResponse:
    """Load entity metadata (labels, descriptions) from disk only."""
    json_path = metadata_dir / f"{entity_id}.json"

    if json_path.exists():
        data: dict = json.loads(json_path.read_text(encoding="utf-8"))
        return EntityMetadataResponse(  # type: ignore
            id=data["id"],
            labels=EntityLabelsResponse(data=data.get("labels", {})),
            descriptions=EntityDescriptionsResponse(data=data.get("descriptions", {})),
            aliases=EntityAliasesResponse(data=data.get("aliases", {})),
            statements=EntityStatementsResponse(data=data.get("statements", [])),
            sitelinks=EntitySitelinksResponse(data=data.get("sitelinks", {})),
        )

    raise FileNotFoundError(f"Entity {entity_id} not found at {json_path}")
