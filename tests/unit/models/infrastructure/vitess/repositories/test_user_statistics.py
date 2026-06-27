"""Unit tests for UserRepository - statistics operations."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.user import UserRepository


class TestUserRepositoryStatistics:
    """Unit tests for UserRepository statistics operations."""

    def test_insert_general_statistics_success(self):
        """Test inserting general statistics successfully."""
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            GeneralStatisticsContext,
        )

        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        ctx = GeneralStatisticsContext(
            date="2023-01-01",
            total_statements=1000,
            total_qualifiers=500,
            total_references=300,
            total_items=100,
            total_lexemes=50,
            total_properties=20,
            total_sitelinks=200,
            total_terms=5000,
            terms_per_language={"en": 3000},
            terms_by_type={"label": 2000},
        )

        repo.insert_general_statistics(ctx)

        mock_cursor.execute.assert_called_once()

    def test_insert_general_statistics_invalid_date_format(self):
        """Test inserting statistics with invalid date format."""
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            GeneralStatisticsContext,
        )
        from fastapi import HTTPException

        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        ctx = GeneralStatisticsContext(
            date="2023-1-01",
            total_statements=1000,
            total_qualifiers=500,
            total_references=300,
            total_items=100,
            total_lexemes=50,
            total_properties=20,
            total_sitelinks=200,
            total_terms=5000,
        )

        with pytest.raises(HTTPException) as exc_info:
            repo.insert_general_statistics(ctx)

        assert exc_info.value.status_code == 400
        assert "Invalid date format" in exc_info.value.detail

    def test_insert_general_statistics_negative_statements(self):
        """Test inserting statistics with negative statements."""
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            GeneralStatisticsContext,
        )
        from fastapi import HTTPException

        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        ctx = GeneralStatisticsContext(
            date="2023-01-01",
            total_statements=-1,
            total_qualifiers=500,
            total_references=300,
            total_items=100,
            total_lexemes=50,
            total_properties=20,
            total_sitelinks=200,
            total_terms=5000,
        )

        with pytest.raises(HTTPException) as exc_info:
            repo.insert_general_statistics(ctx)

        assert exc_info.value.status_code == 400
        assert "total_statements must be non-negative" in exc_info.value.detail

    def test_insert_general_statistics_database_error(self):
        """Test inserting statistics with database error."""
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            GeneralStatisticsContext,
        )

        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        ctx = GeneralStatisticsContext(
            date="2023-01-01",
            total_statements=1000,
            total_qualifiers=500,
            total_references=300,
            total_items=100,
            total_lexemes=50,
            total_properties=20,
            total_sitelinks=200,
            total_terms=5000,
        )

        with pytest.raises(Exception) as exc_info:
            repo.insert_general_statistics(ctx)

        assert "DB error" in str(exc_info.value)

    def test_insert_user_statistics_success(self):
        """Test inserting user statistics successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        repo.insert_user_statistics("2023-01-01", 100, 50)

        mock_cursor.execute.assert_called_once()

    def test_insert_user_statistics_invalid_date_format(self):
        """Test inserting user statistics with invalid date format."""
        from fastapi import HTTPException

        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(HTTPException) as exc_info:
            repo.insert_user_statistics("2023-1-01", 100, 50)

        assert exc_info.value.status_code == 400
        assert "Invalid date format" in exc_info.value.detail

    def test_insert_user_statistics_negative_total_users(self):
        """Test inserting statistics with negative total users."""
        from fastapi import HTTPException

        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(HTTPException) as exc_info:
            repo.insert_user_statistics("2023-01-01", -1, 50)

        assert exc_info.value.status_code == 400
        assert "total_users must be non-negative" in exc_info.value.detail

    def test_insert_user_statistics_negative_active_users(self):
        """Test inserting statistics with negative active users."""
        from fastapi import HTTPException

        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(HTTPException) as exc_info:
            repo.insert_user_statistics("2023-01-01", 100, -1)

        assert exc_info.value.status_code == 400
        assert "active_users must be non-negative" in exc_info.value.detail

    def test_insert_user_statistics_database_error(self):
        """Test inserting user statistics with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception) as exc_info:
            repo.insert_user_statistics("2023-01-01", 100, 50)

        assert "DB error" in str(exc_info.value)
