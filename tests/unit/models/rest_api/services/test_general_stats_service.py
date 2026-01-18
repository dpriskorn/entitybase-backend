"""Unit tests for GeneralStatsService."""

import pytest
from unittest.mock import Mock

from models.rest_api.entitybase.services.general_stats_service import GeneralStatsService


class TestGeneralStatsService:
    """Test cases for GeneralStatsService."""

    def test_compute_daily_stats(self):
        """Test computing daily general stats."""
        # Mock vitess client
        vitess_client = Mock()

        # Mock connection and cursor
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(return_value=conn)
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(return_value=None)
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        # Mock query results
        cursor.fetchone.side_effect = [
            (1000,),  # total_statements
            (500,),   # total_qualifiers
            (200,),   # total_references
            (800,),   # total_items
            (50,),    # total_lexemes
            (100,),   # total_properties
            (1500,),  # total_sitelinks
            (3000,),  # total_terms
        ]
        # Mock aggregations for terms_per_language and terms_by_type
        cursor.fetchall.side_effect = [
            [("en", 1000), ("de", 500)],  # terms_per_language (labels)
            [("en", 800), ("fr", 300)],   # terms_per_language (descriptions)
            [("en", 200), ("es", 100)],   # terms_per_language (aliases)
            [("labels", 1500), ("descriptions", 1000), ("aliases", 500)],  # terms_by_type
        ]

        service = GeneralStatsService()
        stats = service.compute_daily_stats(vitess_client)

        assert stats.total_statements == 1000
        assert stats.total_qualifiers == 500
        assert stats.total_references == 200
        assert stats.total_items == 800
        assert stats.total_lexemes == 50
        assert stats.total_properties == 100
        assert stats.total_sitelinks == 1500
        assert stats.total_terms == 3000
        assert stats.terms_per_language == {"en": 2000, "de": 500, "fr": 300, "es": 100}
        assert stats.terms_by_type == {"labels": 1500, "descriptions": 1000, "aliases": 500}

    def test_get_total_statements_zero(self):
        """Test getting total statements when none exist."""
        vitess_client = Mock()
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(return_value=conn)
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(return_value=None)
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        cursor.fetchone.return_value = (0,)

        service = GeneralStatsService()
        total = service.get_total_statements(vitess_client)

        assert total == 0

    def test_get_terms_per_language_empty(self):
        """Test terms per language when no data."""
        vitess_client = Mock()
        conn = Mock()
        cursor = Mock()
        vitess_client.connection_manager.get_connection.return_value.__enter__ = Mock(return_value=conn)
        vitess_client.connection_manager.get_connection.return_value.__exit__ = Mock(return_value=None)
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=None)

        cursor.fetchall.return_value = []

        service = GeneralStatsService()
        terms_per_lang = service.get_terms_per_language(vitess_client)

        assert terms_per_lang == {}