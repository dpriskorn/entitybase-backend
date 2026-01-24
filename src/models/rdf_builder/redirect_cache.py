"""RDF redirect cache."""

import json
import logging
import time
from pathlib import Path
from typing import Any, List

import requests

from models.data.rest_api.v1.entitybase.response import RedirectBatchResponse, MetadataLoadResponse

logger = logging.getLogger(__name__)


def fetch_entity_redirects_batch(entity_ids: list[str]) -> RedirectBatchResponse:
    """Fetch redirects for multiple entities via MediaWiki API."""
    if not entity_ids:
        return RedirectBatchResponse(redirects={})

    batch_size = 50
    results = {}

    for i in range(0, len(entity_ids), batch_size):
        batch = entity_ids[i : i + batch_size]
        titles_param = "|".join(batch)

        try:
            response = requests.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "query",
                    "prop": "redirects",
                    "titles": titles_param,
                    "rdlimit": "max",
                    "format": "json",
                },
                timeout=60,
                headers={
                    "User-Agent": "WikibaseBackend/1.0 (research@wikibase-backend.org)"
                },
            )
            response.raise_for_status()

            pages_data = response.json()["query"]["pages"]
            for page_info in pages_data.values():
                entity_id = page_info["title"]
                if "redirects" in page_info:
                    redirects = [r["title"] for r in page_info["redirects"]]
                else:
                    redirects = []
                results[entity_id] = redirects

            logger.info(
                f"Fetched redirects for {len(batch)} entities (batch {i // batch_size + 1})"
            )
            time.sleep(2)

        except Exception as e:
            logger.error(f"Failed to fetch batch {i // batch_size + 1}: {e}")
            for entity_id in batch:
                results[entity_id] = []

    return RedirectBatchResponse(redirects=results)


def load_entity_redirects_batch(
    entity_ids: list[str], redirects_dir: Path
) -> MetadataLoadResponse:
    """Fetch and save redirects for multiple entities.

    Args:
        entity_ids: List of entity IDs to fetch redirects for
        redirects_dir: Directory to save redirect files

    Returns:
        MetadataLoadResponse with results mapping entity_id to success status (True/False)
    """
    redirects_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    fetched_redirects = fetch_entity_redirects_batch(entity_ids)

    for entity_id, redirects in fetched_redirects.redirects.items():
        output_path = redirects_dir / f"{entity_id}.json"
        cache_data = {"id": entity_id, "redirects": redirects}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved redirects for {entity_id} to {output_path}")
        results[entity_id] = True

    return MetadataLoadResponse(results=results)


def load_entity_redirects(entity_id: str, redirects_dir: Path) -> list[str]:
    """Load entity redirects from disk only."""
    json_path = redirects_dir / f"{entity_id}.json"

    if json_path.exists():
        data: Any = json.loads(json_path.read_text(encoding="utf-8"))
        redirects: List[str] = data.get("redirects", [])
        return redirects

    raise FileNotFoundError(f"Redirect data for {entity_id} not found at {json_path}")
