"""JSON entity parser."""

import logging

from typing import Any

from models.rest_api.response.entity import (
    AliasValue,
    DescriptionValue,
    EntityAliases,
    EntityDescriptions,
    EntityLabels,
    EntityMetadata,
    EntitySitelinks,
    EntityStatements,
    LabelValue,
)
from models.json_parser.statement_parser import parse_statement
from models.internal_representation.entity import Entity
from models.internal_representation.entity_types import EntityKind
from models.internal_representation.json_fields import JsonField


logger = logging.getLogger(__name__)


def parse_entity(raw_entity_data: dict[str, Any]) -> Entity:
    """Parse entity from Wikidata JSON format."""
    # Handle nested structure {"entities": {"Q42": {...}}}
    metadata_dict = raw_entity_data
    if "entities" in metadata_dict:
        entities = metadata_dict["entities"]
        entity_ids = list(entities.keys())
        if entity_ids:
            metadata_dict = entities[entity_ids[0]]

    # Extract raw data
    labels_dict = metadata_dict.get(JsonField.LABELS.value, {})
    descriptions_dict = metadata_dict.get(JsonField.DESCRIPTIONS.value, {})
    aliases_dict = metadata_dict.get(JsonField.ALIASES.value, {})
    claims_json = metadata_dict.get(JsonField.CLAIMS.value, {})
    sitelinks_json = metadata_dict.get(JsonField.SITELINKS.value, {})

    # Create EntityMetadata instance with structured data
    metadata = EntityMetadata(
        id=metadata_dict.get(JsonField.ID.value, ""),
        type=metadata_dict.get(JsonField.TYPE.value, EntityKind.ITEM.value),
        labels=EntityLabels(
            data={lang: LabelValue(**val) for lang, val in labels_dict.items()}
        ),
        descriptions=EntityDescriptions(
            data={
                lang: DescriptionValue(**val) for lang, val in descriptions_dict.items()
            }
        ),
        aliases=EntityAliases(
            data={
                lang: [AliasValue(**alias) for alias in alias_list]
                for lang, alias_list in aliases_dict.items()
            }
        ),
        statements=EntityStatements(data=claims_json),
        sitelinks=EntitySitelinks(data=sitelinks_json),
    )

    entity_type = EntityKind(metadata.type)

    labels = metadata.labels.data
    descriptions = metadata.descriptions.data
    aliases = metadata.aliases.data
    statements = metadata.statements.data
    sitelinks = metadata.sitelinks.data

    return Entity(
        id=metadata.id,
        type=entity_type,
        labels=labels,
        descriptions=descriptions,
        aliases=aliases,
        statements=statements,
        sitelinks=sitelinks if sitelinks else None,
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
