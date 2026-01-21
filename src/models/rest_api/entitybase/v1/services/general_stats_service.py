"""Service for computing general wiki statistics."""

import logging

from models.rest_api.entitybase.v1.response.misc import (
    GeneralStatsData,
    TermsByType,
    TermsPerLanguage,
)
from models.rest_api.entitybase.v1.service import Service

logger = logging.getLogger(__name__)


class GeneralStatsService(Service):
    """Service for computing general wiki statistics."""

    def compute_daily_stats(self) -> GeneralStatsData:
        """Compute comprehensive general wiki statistics for current date."""
        total_statements = self.get_total_statements()
        total_qualifiers = self.get_total_qualifiers()
        total_references = self.get_total_references()
        total_items = self.get_total_items()
        total_lexemes = self.get_total_lexemes()
        total_properties = self.get_total_properties()
        total_sitelinks = self.get_total_sitelinks()
        total_terms = self.get_total_terms()
        terms_per_language = self.get_terms_per_language()
        terms_by_type = self.get_terms_by_type()

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

    def get_total_statements(self) -> int:
        """Count total statements."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM statements")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_qualifiers(self) -> int:
        """Count total qualifiers."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM qualifiers")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_references(self) -> int:
        """Count total references."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM references")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_items(self) -> int:
        """Count total items."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM entity_revisions WHERE entity_type = 'item'")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_lexemes(self) -> int:
        """Count total lexemes."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM entity_revisions WHERE entity_type = 'lexeme'")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_properties(self) -> int:
        """Count total properties."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM entity_revisions WHERE entity_type = 'property'")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_lexemes(self) -> int:
        """Count total lexemes."""
        with self.state.vitess_client.connection_manager.get_connection() as _:
            with self.connection_manager.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM entities WHERE type = 'lexeme'")
                result = cursor.fetchone()
                return result[0] if result else 0

    def get_total_properties(self) -> int:
        """Count total properties."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM entities WHERE type = 'property'")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_sitelinks(self) -> int:
        """Count total sitelinks."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM sitelinks")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_terms(self) -> int:
        """Count total terms."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM terms")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_sitelinks(self) -> int:
        """Count total sitelinks."""
        cursor = self.state.vitess_client.cursor
        cursor.execute("SELECT COUNT(*) FROM sitelinks")
        result = cursor.fetchone()
        return result[0] if result else 0

    def get_total_terms(self) -> int:
        """Count total terms (labels + descriptions + aliases)."""
        cursor = self.state.vitess_client.cursor
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

    def get_terms_per_language(self) -> TermsPerLanguage:
        """Count terms per language."""
        terms_per_lang: dict[str, int] = {}
        cursor = self.state.vitess_client.cursor
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

    def get_terms_by_type(self) -> TermsByType:
        """Count terms by type (labels, descriptions, aliases)."""
        cursor = self.state.vitess_client.cursor
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
