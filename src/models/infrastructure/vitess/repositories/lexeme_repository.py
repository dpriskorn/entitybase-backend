"""Lexeme repository for database operations."""

import logging
from typing import Any, Dict, Optional

from models.data.infrastructure.vitess.records.lexeme_terms import (
    FormTermHashes,
    LexemeTerms,
    SenseTermHashes,
    TermHashes,
)
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class LexemeRepository(Repository):
    """Database operations for lexeme metadata and term mappings."""

    def store_lexeme_terms(self, entity_id: str, term_hashes: Optional[Dict[str, Any]]) -> None:
        """Store lexeme term hash mappings for an entity.

        Args:
            entity_id: The lexeme entity ID (e.g., "L42")
            term_hashes: Dictionary containing form and sense hash mappings
        """
        logger.debug(f"Storing lexeme terms for {entity_id}")

        if not term_hashes:
            logger.debug("No term hashes to store")
            return

        with self.vitess_client.cursor as cursor:
            # Clear existing terms for this entity
            cursor.execute(
                "DELETE FROM lexeme_terms WHERE entity_id = %s",
                (entity_id,)
            )

            # Insert form terms
            if "forms" in term_hashes:
                for form_id, representations in term_hashes["forms"].items():
                    for lang, term_hash in representations.items():
                        cursor.execute(
                            """
                            INSERT INTO lexeme_terms
                            (entity_id, form_sense_id, term_type, language, term_hash)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (entity_id, form_id, "form", lang, term_hash)
                        )

            # Insert sense terms
            if "senses" in term_hashes:
                for sense_id, glosses in term_hashes["senses"].items():
                    for lang, term_hash in glosses.items():
                        cursor.execute(
                            """
                            INSERT INTO lexeme_terms
                            (entity_id, form_sense_id, term_type, language, term_hash)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (entity_id, sense_id, "sense", lang, term_hash)
                        )

        logger.info(f"Stored lexeme terms for {entity_id}")

    def get_lexeme_terms(self, entity_id: str) -> LexemeTerms:
        """Retrieve lexeme term hash mappings for an entity.

        Args:
            entity_id: The lexeme entity ID (e.g., "L42")

        Returns:
            LexemeTerms object containing form and sense hash mappings
        """
        logger.debug(f"Retrieving lexeme terms for {entity_id}")

        forms = {}
        senses = {}

        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """
                SELECT form_sense_id, term_type, language, term_hash
                FROM lexeme_terms
                WHERE entity_id = %s
                """,
                (entity_id,)
            )

            for row in cursor.fetchall():
                form_sense_id, term_type, language, term_hash = row
                if term_type == "form":
                    if form_sense_id not in forms:
                        forms[form_sense_id] = {}
                    forms[form_sense_id][language] = term_hash
                elif term_type == "sense":
                    if form_sense_id not in senses:
                        senses[form_sense_id] = {}
                    senses[form_sense_id][language] = term_hash

        return LexemeTerms(
            forms=FormTermHashes(
                {
                    form_id: TermHashes(representations)
                    for form_id, representations in forms.items()
                }
            ),
            senses=SenseTermHashes(
                {
                    sense_id: TermHashes(glosses)
                    for sense_id, glosses in senses.items()
                }
            )
        )