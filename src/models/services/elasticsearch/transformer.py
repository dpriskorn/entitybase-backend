"""Elasticsearch transformer module.

Transforms Wikibase entity JSON to Elasticsearch document format.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def transform_to_elasticsearch(entity_json: dict[str, Any]) -> dict[str, Any]:
    """Transform Wikibase entity JSON to Elasticsearch document format.

    Args:
        entity_json: Entity JSON in Wikibase API format (with "entities" wrapper)

    Returns:
        Elasticsearch document with flattened structure

    Example input:
        {
            "entities": {
                "Q42": {
                    "type": "item",
                    "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
                    "descriptions": {...},
                    "aliases": {...},
                    "claims": {...}
                }
            }
        }

    Example output:
        {
            "entity_id": "Q42",
            "entity_type": "item",
            "labels": {"en": {"value": "Douglas Adams", "language": "en"}},
            "descriptions": {...},
            "aliases": {...},
            "claims_flat": {"P31": ["Q5"], "P21": ["Q6581097"]},
            "claims": {...},
            "lastrevid": 2441354823,
            "modified": "2025-12-12T17:50:31Z"
        }
    """
    entities = entity_json.get("entities", {})

    if not entities:
        logger.warning("No entities found in input JSON")
        return {}

    entity_id = list(entities.keys())[0]
    entity_data = entities[entity_id]

    result = {
        "entity_id": entity_id,
        "entity_type": entity_data.get("type"),
        "lastrevid": entity_data.get("lastrevid"),
        "modified": entity_data.get("modified"),
    }

    if entity_data.get("type") == "property":
        result["datatype"] = entity_data.get("datatype")

    result["labels"] = entity_data.get("labels", {})
    result["descriptions"] = entity_data.get("descriptions", {})
    result["aliases"] = entity_data.get("aliases", {})
    result["claims"] = entity_data.get("claims", {})

    result["claims_flat"] = _flatten_claims(entity_data.get("claims", {}))

    if entity_data.get("type") == "lexeme":
        result["lemmas"] = entity_data.get("lemmas", {})
        result["forms"] = entity_data.get("forms", [])
        result["senses"] = entity_data.get("senses", [])
        result["language"] = entity_data.get("language")
        result["lexicalCategory"] = entity_data.get("lexicalCategory")

    logger.debug(f"Transformed entity {entity_id} to ES format")
    return result


def _flatten_claims(claims: dict[str, Any]) -> dict[str, list[str]]:
    """Flatten claims to simple property -> values mapping.

    Args:
        claims: Original claims dict from Wikibase format

    Returns:
        Flattened dict: property_id -> list of value IDs/values

    Example:
        Input:  {"P31": [{"mainsnak": {"datavalue": {"value": {"id": "Q5"}}}}]}
        Output: {"P31": ["Q5"]}
    """
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
                if isinstance(value, dict):
                    if "id" in value:
                        values.append(value["id"])
                    elif "entity-type" in value and "id" in value:
                        values.append(value["id"])
                    elif "time" in value:
                        values.append(value["time"])
                    elif "amount" in value:
                        values.append(str(value["amount"]))
                    else:
                        values.append(str(value))
                else:
                    values.append(str(value))

        if values:
            flat[prop_id] = values

    return flat
