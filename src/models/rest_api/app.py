"""FastAPI application setup and configuration."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from models.config.settings import settings
from models.rest_api.entitybase.v1.handlers.state import StateHandler

log_level = settings.get_log_level()

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info("Setting loglevel: {}".format(log_level))


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.debug("Initializing clients...")
        from pathlib import Path

        state_handler = StateHandler(
            settings=settings,
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
