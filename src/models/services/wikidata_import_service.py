"""Wikidata import service."""

import logging
import os
from typing import Any, Dict

import requests
from pydantic import BaseModel

from models.rest_api.entitybase.response.misc import RawEntityData
from models.rest_api.misc import EditType
from models.rest_api.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = os.getenv("WIKIDATA_USER_AGENT", "Entitybase/1.0 User:So9q")


class WikidataImportService(BaseModel):
    """Service for importing entities from Wikidata."""

    @staticmethod
    def fetch_entity_data(entity_id: str) -> RawEntityData:
        """Fetch entity data from Wikidata API.

        Args:
            entity_id: Wikidata entity ID (Q42, P31, etc.)

        Returns:
            Raw entity data from Wikidata API

        Raises:
            ValueError: If entity not found or API error
        """
        params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "format": "json",
        }

        headers = {"User-Agent": USER_AGENT}

        try:
            response = requests.get(
                WIKIDATA_API_URL,
                params=params,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            data: Dict[str, Any] = response.json()

            # Check for API errors
            if "error" in data:
                raise ValueError(f"Wikidata API error: {data['error']}")

            # Check if entity exists
            entities = data.get("entities", {})
            if entity_id not in entities:
                raise ValueError(f"Entity {entity_id} not found in Wikidata")

            entity_data = entities[entity_id]

            # Handle missing entities (deleted or invalid)
            if "missing" in entity_data:
                raise ValueError(f"Entity {entity_id} is missing/deleted on Wikidata")

            # Handle redirects
            if "redirects" in data:
                redirect_info = data["redirects"].get(entity_id)
                if redirect_info:
                    redirected_to = redirect_info.get("to")
                    logger.info(f"Entity {entity_id} redirects to {redirected_to}")
                    # For now, just proceed with the data (API returns the target entity)

            return RawEntityData(data=entity_data)

        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch {entity_id} from Wikidata: {e}")

    @staticmethod
    def transform_to_create_request(
        wikidata_data: Dict[str, Any],
    ) -> EntityCreateRequest:
        """Transform Wikidata entity data to EntityCreateRequest format.

        Args:
            wikidata_data: Raw entity data from Wikidata API

        Returns:
            EntityCreateRequest: Formatted request for entity creation
        """
        logger.info(f"Transforming Wikidata data for entity {wikidata_data.get('id')}")
        entity_id = wikidata_data["id"]
        entity_type = wikidata_data["type"]  # "item", "property", "lexeme"

        # Map Wikidata type to our type
        if entity_type == "item":
            our_type = "item"
        elif entity_type == "property":
            our_type = "property"
        elif entity_type == "lexeme":
            our_type = "lexeme"
        else:
            our_type = entity_type  # fallback

        # Extract labels, descriptions, aliases (format is compatible)
        labels = wikidata_data.get("labels", {})
        descriptions = wikidata_data.get("descriptions", {})
        aliases = wikidata_data.get("aliases", {})

        # Claims are compatible
        claims = wikidata_data.get("claims", {})

        # Sitelinks
        sitelinks = wikidata_data.get("sitelinks", {})

        return EntityCreateRequest(
            id=entity_id,
            type=our_type,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            claims=claims,
            sitelinks=sitelinks,
            edit_type=EditType.BOT_IMPORT,
            edit_summary="Imported from Wikidata",
        )

    @classmethod
    def import_entity(cls, entity_id: str) -> EntityCreateRequest:
        """Fetch and transform a single entity from Wikidata.

        Args:
            entity_id: Wikidata entity ID

        Returns:
            EntityCreateRequest for the entity

        Raises:
            ValueError: If fetch or transformation fails
        """
        logger.info(f"Importing entity {entity_id} from Wikidata")
        raw_data = cls.fetch_entity_data(entity_id)
        create_request = cls.transform_to_create_request(raw_data.data)
        return create_request
