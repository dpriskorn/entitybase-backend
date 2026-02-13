"""JSON entity parser."""

import logging
from typing import Any

from models.data.infrastructure.s3.enums import EntityType
from models.internal_representation.entity_data import EntityData
from models.internal_representation.json_fields import JsonField
from models.internal_representation.lexeme import LexemeForm, LexemeSense
from models.json_parser.statement_parser import parse_statement
from models.data.rest_api.v1.entitybase.response import (
    EntityAliasesResponse,
    EntityDescriptionsResponse,
    EntityLabelsResponse,
    EntityMetadataResponse,
)
from models.data.rest_api.v1.entitybase.response import (
    AliasValue,
    DescriptionValue,
    LabelValue,
    EntityStatementsResponse,
    EntitySitelinksResponse,
)

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
            data=[
                {**stmt, "property": prop}
                for prop, stmts in claims_json.items()
                for stmt in stmts
            ]
        ),
        sitelinks=EntitySitelinksResponse(data=sitelinks_json),
    )

    return metadata


def parse_entity_data(raw_entity_data: dict[str, Any]) -> EntityData:
    """Parse entity from Wikidata JSON format into internal EntityData."""
    logger.debug("Parsing entity data from raw data")
    logger.debug(f"Raw data keys: {list(raw_entity_data.keys())}")
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

    entity_type = metadata_dict.get(JsonField.TYPE.value, EntityType.ITEM.value)
    logger.debug(
        f"Entity type: {entity_type}, ID: {metadata_dict.get(JsonField.ID.value)}"
    )

    statements = []
    logger.debug("Parsing statements")
    for prop_claims in claims_json.values():
        for stmt in prop_claims:
            statements.append(parse_statement(stmt))

    # Lexeme-specific fields
    lemmas = metadata_dict.get("lemmas")
    lexical_category = metadata_dict.get("lexicalCategory") or ""
    language = metadata_dict.get("language") or ""

    # Parse forms and senses if they exist
    forms = None
    senses = None

    if "forms" in metadata_dict:
        forms = []
        for form_data in metadata_dict["forms"]:
            form = LexemeForm(
                id=form_data["id"],
                representations=form_data.get("representations", {}),
                grammaticalFeatures=form_data.get("grammaticalFeatures", []),
                claims=form_data.get("claims", {}),
            )
            forms.append(form)

    if "senses" in metadata_dict:
        senses = []
        for sense_data in metadata_dict["senses"]:
            sense = LexemeSense(
                id=sense_data["id"],
                glosses=sense_data.get("glosses", {}),
                claims=sense_data.get("claims", {}),
            )
            senses.append(sense)

    return EntityData(
        id=metadata_dict.get(JsonField.ID.value, ""),
        type=entity_type,
        labels=labels_dict,
        descriptions=descriptions_dict,
        aliases=aliases_dict,
        statements=statements,
        sitelinks=sitelinks_json,
        lemmas=lemmas,
        lexicalCategory=lexical_category,
        language=language,
        forms=forms,
        senses=senses,
    )
