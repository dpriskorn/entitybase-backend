"""Elasticsearch transformer module.

Transforms Wikibase entity JSON to Elasticsearch document format.
"""

import logging
from typing import Any

from pydantic import BaseModel

from models.data.infrastructure.elasticsearch import (
    ElasticsearchDocument,
    FlattenedClaims,
)

logger = logging.getLogger(__name__)


def transform_to_elasticsearch(entity_json: dict[str, Any]) -> ElasticsearchDocument:
    """Transform Wikibase entity JSON to Elasticsearch document format."""
    entities = entity_json.get("entities", {})

    if not entities:
        logger.warning("No entities found in input JSON")
        return ElasticsearchDocument(
            **{"@id": "", "@type": "", "lastrevid": 0, "modified": ""}
        )

    entity_id = list(entities.keys())[0]
    entity_data = entities[entity_id]

    claims_flat = _flatten_claims(entity_data.get("claims", {}))

    doc = ElasticsearchDocument(
        **{
            "@id": entity_id,
            "@type": entity_data.get("type", ""),
            "lastrevid": entity_data.get("lastrevid", 0),
            "modified": entity_data.get("modified", ""),
            "datatype": entity_data.get("datatype"),
            "labels": entity_data.get("labels", {}),
            "descriptions": entity_data.get("descriptions", {}),
            "aliases": entity_data.get("aliases", {}),
            "claims": entity_data.get("claims", {}),
            "claims_flat": claims_flat,
            "lemmas": entity_data.get("lemmas"),
            "forms": entity_data.get("forms"),
            "senses": entity_data.get("senses"),
            "language": entity_data.get("language"),
            "lexicalCategory": entity_data.get("lexicalCategory"),
        }
    )

    logger.debug(f"Transformed entity {entity_id} to ES format")
    return doc


def _flatten_claims(claims: dict[str, Any]) -> FlattenedClaims:
    """Flatten claims to simple property -> values mapping.

    Args:
        claims: Original claims dict from Wikibase format

    Returns:
        Flattened dict: property_id -> list of value IDs/values

    Example:
        Input:  {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q5"}}}}]}
        Output: {"P31": ["Q5"]}
    """
    logger.debug(f"Flattening {len(claims)} claims")
    flat: dict[str, list[str]] = {}

    for prop_id, statements in claims.items():
        values: list[str] = []

        for statement in statements:
            mainsnak = statement.get("mainsnak", {})
            datavalue = mainsnak.get("datavalue", {})
            value = datavalue.get("value")

            if value is None:
                continue

            snaktype = mainsnak.get("snaktype", "value")

            if snaktype == "value":
                extracted = _extract_claim_value(value)
                if extracted is not None:
                    values.append(extracted)

        if values:
            flat[prop_id] = values

    return FlattenedClaims(data=flat)


def _extract_claim_value(value: Any) -> str:
    """Extract a string value from a claim datavalue.

    Args:
        value: The datavalue value dict

    Returns:
        String representation of the value, or empty string if not extractable
    """
    if isinstance(value, dict):
        if "id" in value:
            return str(value["id"]) if value["id"] is not None else ""
        if "time" in value:
            return str(value["time"]) if value["time"] is not None else ""
        if "amount" in value:
            return str(value["amount"])
        return str(value)
    return str(value)
