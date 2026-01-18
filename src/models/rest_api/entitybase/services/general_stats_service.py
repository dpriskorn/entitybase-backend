"""Service for computing general wiki statistics."""

import logging
from typing import Dict

from pydantic import BaseModel

from models.infrastructure.vitess_client import VitessClient
from models.rest_api.entitybase.response.misc import (
    GeneralStatsData,
    TermsByType,
    TermsPerLanguage,
)

logger = logging.getLogger(__name__)


class GeneralStatsService(BaseModel):
    """Service for computing general wiki statistics."""

    def compute_daily_stats(self, vitess_client: VitessClient) -> GeneralStatsData:
        """Compute comprehensive general wiki statistics for current date."""
        total_statements = self.get_total_statements(vitess_client)
        total_qualifiers = self.get_total_qualifiers(vitess_client)
        total_references = self.get_total_references(vitess_client)
        total_items = self.get_total_items(vitess_client)
        total_lexemes = self.get_total_lexemes(vitess_client)
        total_properties = self.get_total_properties(vitess_client)
        total_sitelinks = self.get_total_sitelinks(vitess_client)
        total_terms = self.get_total_terms(vitess_client)
        terms_per_language = self.get_terms_per_language(vitess_client)
        terms_by_type = self.get_terms_by_type(vitess_client)

        return GeneralStatsData(
            total_statements=total_statements,
            total_qualifiers=total_qualifiers,
            total_references=total_references,
            total_items=total_items,
            total_lexemes=total_lexemes,
            total_properties=total_properties,
            total_sitelinks=total_sitelinks,
            total_terms=total_terms,
            terms_per_language=TermsPerLanguage(terms=terms_per_language),
            terms_by_type=TermsByType(counts=terms_by_type),
        )

    def get_total_statements(self, vitess_client: VitessClient) -> int:
        """Count total statements."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM statements")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_qualifiers(self, vitess_client: VitessClient) -> int:
        """Count total qualifiers."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM qualifiers")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_references(self, vitess_client: VitessClient) -> int:
        """Count total references."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM references")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_items(self, vitess_client: VitessClient) -> int:
        """Count total items."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM entities WHERE type = 'item'")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_lexemes(self, vitess_client: VitessClient) -> int:
        """Count total lexemes."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM entities WHERE type = 'lexeme'")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_properties(self, vitess_client: VitessClient) -> int:
        """Count total properties."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM entities WHERE type = 'property'")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_sitelinks(self, vitess_client: VitessClient) -> int:
        """Count total sitelinks."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM sitelinks")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_terms(self, vitess_client: VitessClient) -> int:
        """Count total terms (labels + descriptions + aliases)."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        (SELECT COUNT(*) FROM labels) +
                        (SELECT COUNT(*) FROM descriptions) +
                        (SELECT COUNT(*) FROM aliases) AS total_terms
                    """
                )
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_terms_per_language(self, vitess_client: VitessClient) -> TermsPerLanguage:
        """Count terms per language."""
        terms_per_lang: dict[str, int] = {}
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                # Labels per language
                cursor.execute(
                    "SELECT language_code, COUNT(*) FROM labels GROUP BY language_code"
                )
                for row in cursor.fetchall():
                    lang, count = row
                    terms_per_lang[lang] = terms_per_lang.get(lang, 0) + count

                # Descriptions per language
                cursor.execute(
                    "SELECT language_code, COUNT(*) FROM descriptions GROUP BY language_code"
                )
                for row in cursor.fetchall():
                    lang, count = row
                    terms_per_lang[lang] = terms_per_lang.get(lang, 0) + count

                # Aliases per language
                cursor.execute(
                    "SELECT language_code, COUNT(*) FROM aliases GROUP BY language_code"
                )
                for row in cursor.fetchall():
                    lang, count = row
                    terms_per_lang[lang] = terms_per_lang.get(lang, 0) + count

        return TermsPerLanguage(terms=terms_per_lang)

    def get_terms_by_type(self, vitess_client: VitessClient) -> TermsByType:
        """Count terms by type (labels, descriptions, aliases)."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 'labels' AS type, COUNT(*) FROM labels
                    UNION ALL
                    SELECT 'descriptions' AS type, COUNT(*) FROM descriptions
                    UNION ALL
                    SELECT 'aliases' AS type, COUNT(*) FROM aliases
                    """
                )
                results = cursor.fetchall()
                data = {row[0]: row[1] for row in results}
                return TermsByType(counts=data)
