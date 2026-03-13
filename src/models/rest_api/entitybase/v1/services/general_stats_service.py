"""Service for computing general wiki statistics."""

import logging

from models.data.rest_api.v1.entitybase.response.stats import (
    DeduplicationDatabaseStatsResponse,
    DeduplicationStatsByType,
    GeneralStatsData,
)
from models.data.rest_api.v1.entitybase.response.terms import (
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
            terms_per_language=terms_per_language,
            terms_by_type=terms_by_type,
        )

    def get_total_statements(self) -> int:
        """Count total statements."""
        try:
            with self.state.vitess_client.cursor as cursor:
                cursor.execute("SELECT COUNT(*) FROM statements")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            logger.debug("statements table does not exist, returning 0")
            return 0

    def get_total_qualifiers(self) -> int:
        """Count total qualifiers."""
        try:
            with self.state.vitess_client.cursor as cursor:
                cursor.execute("SELECT COUNT(*) FROM qualifiers")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            logger.debug("qualifiers table does not exist, returning 0")
            return 0

    def get_total_references(self) -> int:
        """Count total references."""
        try:
            with self.state.vitess_client.cursor as cursor:
                cursor.execute("SELECT COUNT(*) FROM references")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            logger.debug("references table does not exist, returning 0")
            return 0

    def get_total_items(self) -> int:
        """Count total items."""
        with self.state.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT COUNT(*) FROM entity_revisions r
                   JOIN entity_id_mapping m ON r.internal_id = m.internal_id
                   WHERE m.entity_id LIKE 'Q%'"""
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_total_lexemes(self) -> int:
        """Count total lexemes."""
        with self.state.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT COUNT(*) FROM entity_revisions r
                   JOIN entity_id_mapping m ON r.internal_id = m.internal_id
                   WHERE m.entity_id LIKE 'L%'"""
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_total_properties(self) -> int:
        """Count total properties."""
        with self.state.vitess_client.cursor as cursor:
            cursor.execute(
                """SELECT COUNT(*) FROM entity_revisions r
                   JOIN entity_id_mapping m ON r.internal_id = m.internal_id
                   WHERE m.entity_id LIKE 'P%'"""
            )
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_total_sitelinks(self) -> int:
        """Count total sitelinks."""
        try:
            with self.state.vitess_client.cursor as cursor:
                cursor.execute("SELECT COUNT(*) FROM sitelinks")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            logger.debug("sitelinks table does not exist, returning 0")
            return 0

    def get_total_terms(self) -> int:
        """Count total terms."""
        try:
            with self.state.vitess_client.cursor as cursor:
                cursor.execute("SELECT COUNT(*) FROM terms")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            logger.debug("terms table does not exist, returning 0")
            return 0

    def get_terms_per_language(self) -> TermsPerLanguage:
        """Count terms per language."""
        terms_per_lang: dict[str, int] = {}
        try:
            with self.state.vitess_client.cursor as cursor:
                try:
                    cursor.execute(
                        "SELECT language_code, COUNT(*) FROM labels GROUP BY language_code"
                    )
                    for row in cursor.fetchall():
                        lang, count = row
                        terms_per_lang[lang] = terms_per_lang.get(lang, 0) + count
                except Exception:
                    logger.debug("labels table does not exist, skipping")

                try:
                    cursor.execute(
                        "SELECT language_code, COUNT(*) FROM descriptions GROUP BY language_code"
                    )
                    for row in cursor.fetchall():
                        lang, count = row
                        terms_per_lang[lang] = terms_per_lang.get(lang, 0) + count
                except Exception:
                    logger.debug("descriptions table does not exist, skipping")

                try:
                    cursor.execute(
                        "SELECT language_code, COUNT(*) FROM aliases GROUP BY language_code"
                    )
                    for row in cursor.fetchall():
                        lang, count = row
                        terms_per_lang[lang] = terms_per_lang.get(lang, 0) + count
                except Exception:
                    logger.debug("aliases table does not exist, skipping")
        except Exception as e:
            logger.debug(f"Error getting terms per language: {e}")
        return TermsPerLanguage(terms=terms_per_lang)

    def get_terms_by_type(self) -> TermsByType:
        """Count terms by type (labels, descriptions, aliases)."""
        data = {}
        try:
            with self.state.vitess_client.cursor as cursor:
                try:
                    cursor.execute("SELECT 'labels' AS type, COUNT(*) FROM labels")
                    result = cursor.fetchone()
                    if result:
                        data[result[0]] = result[1]
                except Exception:
                    logger.debug("labels table does not exist, skipping")

                try:
                    cursor.execute(
                        "SELECT 'descriptions' AS type, COUNT(*) FROM descriptions"
                    )
                    result = cursor.fetchone()
                    if result:
                        data[result[0]] = result[1]
                except Exception:
                    logger.debug("descriptions table does not exist, skipping")

                try:
                    cursor.execute("SELECT 'aliases' AS type, COUNT(*) FROM aliases")
                    result = cursor.fetchone()
                    if result:
                        data[result[0]] = result[1]
                except Exception:
                    logger.debug("aliases table does not exist, skipping")
        except Exception as e:
            logger.debug(f"Error getting terms by type: {e}")
        return TermsByType(counts=data)

    def compute_deduplication_stats(self) -> DeduplicationDatabaseStatsResponse:
        """Compute deduplication statistics for all data types."""
        statements = self._get_table_deduplication_stats("statements")
        qualifiers = self._get_table_deduplication_stats("qualifiers")
        references = self._get_table_deduplication_stats("refs")
        snaks = self._get_table_deduplication_stats("snaks")
        sitelinks = self._get_table_deduplication_stats("sitelinks")
        terms = self._get_terms_deduplication_stats()

        return DeduplicationDatabaseStatsResponse(
            statements=statements,
            qualifiers=qualifiers,
            references=references,
            snaks=snaks,
            sitelinks=sitelinks,
            terms=terms,
        )

    def _get_table_deduplication_stats(
        self, table_name: str
    ) -> DeduplicationStatsByType:
        """Get deduplication stats for a specific table."""
        try:
            with self.state.vitess_client.cursor as cursor:
                cursor.execute(
                    f"SELECT COUNT(*), COALESCE(SUM(ref_count), 0) FROM {table_name}"
                )
                result = cursor.fetchone()
                if result and result[0] > 0:
                    unique_hashes = result[0]
                    total_ref_count = result[1]
                    space_saved = total_ref_count - unique_hashes
                    deduplication_factor = (
                        (space_saved / total_ref_count * 100)
                        if total_ref_count > 0
                        else 0.0
                    )
                    return DeduplicationStatsByType(
                        unique_hashes=unique_hashes,
                        total_ref_count=total_ref_count,
                        deduplication_factor=round(deduplication_factor, 2),
                        space_saved=space_saved,
                    )
        except Exception as e:
            logger.debug(f"Error getting deduplication stats for {table_name}: {e}")

        return DeduplicationStatsByType(
            unique_hashes=0,
            total_ref_count=0,
            deduplication_factor=0.0,
            space_saved=0,
        )

    def _get_terms_deduplication_stats(self) -> DeduplicationStatsByType:
        """Get deduplication stats for terms (labels, descriptions, aliases tables)."""
        try:
            with self.state.vitess_client.cursor as cursor:
                total_unique = 0
                total_ref_count = 0

                for table in ["labels", "descriptions", "aliases"]:
                    try:
                        cursor.execute(
                            f"SELECT COUNT(*), COALESCE(SUM(ref_count), 0) FROM {table}"
                        )
                        result = cursor.fetchone()
                        if result:
                            total_unique += result[0]
                            total_ref_count += result[1]
                    except Exception:
                        logger.debug(f"{table} table does not exist, skipping")

                if total_unique > 0:
                    space_saved = total_ref_count - total_unique
                    deduplication_factor = (
                        (space_saved / total_ref_count * 100)
                        if total_ref_count > 0
                        else 0.0
                    )
                    return DeduplicationStatsByType(
                        unique_hashes=total_unique,
                        total_ref_count=total_ref_count,
                        deduplication_factor=round(deduplication_factor, 2),
                        space_saved=space_saved,
                    )
        except Exception as e:
            logger.debug(f"Error getting terms deduplication stats: {e}")

        return DeduplicationStatsByType(
            unique_hashes=0,
            total_ref_count=0,
            deduplication_factor=0.0,
            space_saved=0,
        )
