"""General statistics routes."""

import logging

from fastapi import APIRouter, Request

from models.rest_api.entitybase.v1.handlers.user import UserHandler
from models.data.rest_api.v1.entitybase.response import GeneralStatsResponse

logger = logging.getLogger(__name__)

stats_router = APIRouter(tags=["statistics"])


@stats_router.get("/stats", response_model=GeneralStatsResponse)
def get_general_stats(req: Request) -> GeneralStatsResponse:
    """Get general wiki statistics."""
    state = req.app.state.state_handler
    handler = UserHandler(state=state)
    try:
        stats = handler.get_general_stats()
        return stats
    except ValueError as e:
        logger.warning(f"ValueError in get_general_stats (returning empty stats): {e}")
        from datetime import date
        from models.data.rest_api.v1.entitybase.response import (
            TermsPerLanguage,
            TermsByType,
        )

        return GeneralStatsResponse(
            date=str(date.today()),
            total_statements=0,
            total_qualifiers=0,
            total_references=0,
            total_items=0,
            total_lexemes=0,
            total_properties=0,
            total_sitelinks=0,
            total_terms=0,
            terms_per_language=TermsPerLanguage(terms={}),
            terms_by_type=TermsByType(counts={}),
        )
