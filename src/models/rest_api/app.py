"""FastAPI application setup and configuration."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from models.config.settings import settings
from models.rest_api.entitybase.v1.handlers.state import StateHandler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.debug("Initializing clients...")
        from pathlib import Path

        state_handler = StateHandler(
            s3_config=settings.to_s3_config(),
            vitess_config=settings.to_vitess_config(),
            entity_change_stream_config=settings.get_entity_change_stream_config(),
            entity_diff_stream_config=settings.get_entity_diff_stream_config(),
            property_registry_path=Path(settings.property_registry_path)
            if settings.property_registry_path
            else None,
        )
        state_handler.start()
        app_.state.state_handler = state_handler
        yield

    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        raise
    finally:
        logger.debug("Shutting down...")


app = FastAPI(
    title="Wikibase Backend API",
    description="Backend API for Wikibase entity management",
    version="1.0.0",
    lifespan=lifespan,
)
