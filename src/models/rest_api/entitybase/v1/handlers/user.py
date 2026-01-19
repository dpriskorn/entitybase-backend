"""Handler for user operations."""

import json
import logging

logger = logging.getLogger(__name__)

from models.infrastructure.vitess.vitess_client import VitessClient
from models.rest_api.entitybase.v1.response.misc import (
    GeneralStatsResponse,
    TermsByType,
    TermsPerLanguage,
    UserStatsResponse,
)
from models.rest_api.entitybase.v1.response.user import (
    WatchlistToggleResponse,
    UserCreateResponse,
)
from models.rest_api.utils import raise_validation_error
from models.rest_api.entitybase.v1.request.user import (
    UserCreateRequest,
    WatchlistToggleRequest,
)
from models.rest_api.entitybase.v1.response.user import UserResponse


class UserHandler:
    """Handler for user-related operations."""

    def create_user(
        self, request: UserCreateRequest, vitess_client: VitessClient
    ) -> UserCreateResponse:
        """Create/register a user."""
        # Check if user already exists
        exists = vitess_client.user_repository.user_exists(request.user_id)
        if not exists:
            result = vitess_client.user_repository.create_user(request.user_id)
            if not result.success:
                raise_validation_error(
                    result.error or "Failed to create user", status_code=500
                )
            created = True
        else:
            created = False
        return UserCreateResponse(user_id=request.user_id, created=created)

    def get_user(self, user_id: int, vitess_client: VitessClient) -> UserResponse:
        """Get user by ID."""
        user = vitess_client.user_repository.get_user(user_id)
        if user is None:
            raise_validation_error("User not found", status_code=404)
        assert isinstance(user, UserResponse)
        return user

    def toggle_watchlist(
        self, user_id: int, request: WatchlistToggleRequest, vitess_client: VitessClient
    ) -> WatchlistToggleResponse:
        """Enable or disable watchlist for user."""
        # Check if user exists
        if not vitess_client.user_repository.user_exists(user_id):
            raise_validation_error("User not registered", status_code=400)

        result = vitess_client.user_repository.set_watchlist_enabled(
            user_id, request.enabled
        )
        if not result.success:
            raise_validation_error(
                result.error or "Failed to set watchlist", status_code=500
            )
        return WatchlistToggleResponse(user_id=user_id, enabled=request.enabled)

    def get_user_stats(self, vitess_client: VitessClient) -> UserStatsResponse:
        """Get user statistics from the daily stats table."""
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT stat_date, total_users, active_users FROM user_daily_stats ORDER BY stat_date DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    # Handle both datetime objects and string dates
                    date_str = (
                        row[0].isoformat()
                        if hasattr(row[0], "isoformat")
                        else str(row[0])
                    )
                    return UserStatsResponse(
                        date=date_str,
                        total=row[1],
                        active=row[2],
                    )
                else:
                    # Fallback to live computation if no data
                    from models.rest_api.entitybase.v1.services.user_stats_service import (
                        UserStatsService,
                    )

                    service = UserStatsService()
                    stats = service.compute_daily_stats(vitess_client)
                    return UserStatsResponse(
                        date="live",
                        total=stats.total_users,
                        active=stats.active_users,
                    )

    def get_general_stats(self, vitess_client: VitessClient) -> GeneralStatsResponse:
        """Get general wiki statistics from the daily stats table."""
        logger.debug("Fetching general stats from database")
        with vitess_client.connection_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT stat_date, total_statements, total_qualifiers, total_references, total_items, total_lexemes, total_properties, total_sitelinks, total_terms, terms_per_language, terms_by_type FROM general_daily_stats ORDER BY stat_date DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    return GeneralStatsResponse(
                        date=row[0].isoformat(),
                        total_statements=row[1],
                        total_qualifiers=row[2],
                        total_references=row[3],
                        total_items=row[4],
                        total_lexemes=row[5],
                        total_properties=row[6],
                        total_sitelinks=row[7],
                        total_terms=row[8],
                        terms_per_language=TermsPerLanguage(
                            terms=json.loads(row[9]) if row[9] else {}
                        ),
                        terms_by_type=TermsByType(
                            counts=json.loads(row[10]) if row[10] else {}
                        ),
                    )
                else:
                    # Fallback to live computation if no data
                    from models.rest_api.entitybase.v1.services.general_stats_service import (
                        GeneralStatsService,
                    )

                    service = GeneralStatsService()
                    stats = service.compute_daily_stats(vitess_client)
                    return GeneralStatsResponse(
                        date="live",
                        total_statements=stats.total_statements,
                        total_qualifiers=stats.total_qualifiers,
                        total_references=stats.total_references,
                        total_items=stats.total_items,
                        total_lexemes=stats.total_lexemes,
                        total_properties=stats.total_properties,
                        total_sitelinks=stats.total_sitelinks,
                        total_terms=stats.total_terms,
                        terms_per_language=TermsPerLanguage(
                            terms=stats.terms_per_language.terms
                            if hasattr(stats.terms_per_language, "terms")
                            else stats.terms_per_language
                        ),
                        terms_by_type=TermsByType(
                            counts=stats.terms_by_type.counts
                            if hasattr(stats.terms_by_type, "counts")
                            else stats.terms_by_type
                        ),
                    )
