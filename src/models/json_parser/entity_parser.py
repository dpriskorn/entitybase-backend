import logging

from typing import Any

from models.rest_api.response.entity import (
    EntityAliases,
    EntityDescriptions,
    EntityLabels,
)
from models.json_parser.statement_parser import parse_statement
from models.internal_representation.entity import Entity
from models.internal_representation.entity_types import EntityKind
from models.internal_representation.json_fields import JsonField


logger = logging.getLogger(__name__)


def parse_entity(metadata: dict[str, Any]) -> Entity:
    # Handle nested structure {"entities": {"Q42": {...}}}
    if "entities" in metadata:
        entities = metadata["entities"]
        entity_ids = list(entities.keys())
        if entity_ids:
            metadata = entities[entity_ids[0]]

    entity_id = metadata.get(JsonField.ID.value, "")
    entity_type = EntityKind(metadata.get(JsonField.TYPE.value, EntityKind.ITEM.value))

    labels_json = metadata.get(JsonField.LABELS.value, {})
    descriptions_json = metadata.get(JsonField.DESCRIPTIONS.value, {})
    aliases_json = metadata.get(JsonField.ALIASES.value, {})
    claims_json = metadata.get(JsonField.CLAIMS.value, {})
    sitelinks_json = metadata.get(JsonField.SITELINKS.value, {})

    labels = _parse_labels(labels_json)
    descriptions = _parse_descriptions(descriptions_json)
    aliases = _parse_aliases(aliases_json)
    statements = _parse_statements(claims_json)

    return Entity(
        id=entity_id,
        type=entity_type,
        labels=labels,
        descriptions=descriptions,
        aliases=aliases,
        statements=statements,
        sitelinks=sitelinks_json if sitelinks_json else None,
    )


def _parse_labels(labels_json: dict[str, dict[str, str]]) -> EntityLabels:
    labels = {
        lang: label_data.get("value", "") for lang, label_data in labels_json.items()
    }
    return EntityLabels(labels=labels)


def _parse_descriptions(
    descriptions_json: dict[str, dict[str, str]],
) -> EntityDescriptions:
    descriptions = {
        lang: desc_data.get("value", "")
        for lang, desc_data in descriptions_json.items()
    }
    return EntityDescriptions(descriptions=descriptions)


def _parse_aliases(
    aliases_json: dict[str, list[dict[str, str]]],
) -> EntityAliases:
    aliases = {
        lang: [alias_data.get("value", "") for alias_data in alias_list]
        for lang, alias_list in aliases_json.items()
    }
    return EntityAliases(aliases=aliases)


def _parse_statements(claims_json: dict[str, list[dict[str, Any]]]) -> list:
    statements = []
    for property_id, claim_list in claims_json.items():
        for claim_json in claim_list:
            try:
                statement = parse_statement(claim_json)
                statements.append(statement)
            except ValueError as e:
                logger.warning(
                    f"Failed to parse statement for property {property_id}: {e}"
                )
                continue

    return statements
