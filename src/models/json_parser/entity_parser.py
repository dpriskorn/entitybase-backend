"""JSON entity parser."""

import logging

from typing import Any

from models.internal_representation.entity_data import EntityData
from models.internal_representation.statements import Statement
from models.rest_api.entitybase.response import (
    EntityAliasesResponse,
    EntityDescriptionsResponse,
    EntityLabelsResponse,
    EntityMetadataResponse,
)
from models.rest_api.entitybase.response import StatementHashResult
from models.rest_api.entitybase.response.entity import (
    AliasValue,
    DescriptionValue,
    LabelValue,
    EntityStatementsResponse,
    EntitySitelinksResponse,
)

from models.json_parser.statement_parser import parse_statement
from models.infrastructure.s3.enums import EntityType
from models.internal_representation.json_fields import JsonField


logger = logging.getLogger(__name__)


def parse_entity(raw_entity_data: dict[str, Any]) -> EntityMetadataResponse:
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
    metadata = EntityMetadataResponse(
        id=metadata_dict.get(JsonField.ID.value, ""),
        type=metadata_dict.get(JsonField.TYPE.value, EntityType.ITEM.value),
        labels=EntityLabelsResponse(
            data={lang: LabelValue(**val) for lang, val in labels_dict.items()}
        ),
        descriptions=EntityDescriptionsResponse(
            data={
                lang: DescriptionValue(**val) for lang, val in descriptions_dict.items()
            }
        ),
        aliases=EntityAliasesResponse(
            data={
                lang: [AliasValue(**alias) for alias in alias_list]
                for lang, alias_list in aliases_dict.items()
            }
        ),
        statements=EntityStatementsResponse(
            data=[stmt for prop in claims_json.values() for stmt in prop]
        ),
        sitelinks=EntitySitelinksResponse(data=sitelinks_json),
    )

    entity_type = EntityType(metadata.type)

    statements = [parse_statement(stmt) for stmt in metadata.statements.data]

    from models.internal_representation.entity import Entity

    return Entity(
        id=metadata.id,
        type=entity_type,
        labels=metadata.labels,
        descriptions=metadata.descriptions,
        aliases=metadata.aliases,
        statements=statements,
        sitelinks=metadata.sitelinks,
    )
