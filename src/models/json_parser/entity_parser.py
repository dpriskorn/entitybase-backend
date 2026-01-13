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
    logger.debug("Parsing entity from raw data")
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
        statements=EntityStatements(
            data=[stmt for prop in claims_json.values() for stmt in prop]
        ),
        sitelinks=EntitySitelinks(data=sitelinks_json),
    )

    entity_type = EntityKind(metadata.type)

    sitelinks = metadata.sitelinks.data
    statements = [parse_statement(stmt) for stmt in metadata.statements.data]

    return Entity(
        id=metadata.id,
        type=entity_type,
        labels=metadata.labels,
        descriptions=metadata.descriptions,
        aliases=metadata.aliases,
        statements=statements,
        sitelinks=sitelinks if sitelinks else None,
    )
