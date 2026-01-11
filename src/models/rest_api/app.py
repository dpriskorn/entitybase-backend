"""FastAPI application setup and configuration."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from models.config.settings import settings
from models.rest_api.clients import Clients

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.debug("Initializing clients...")
        from pathlib import Path

        clients = Clients(
            s3=settings.to_s3_config(),
            vitess=settings.to_vitess_config(),
            property_registry_path=Path(settings.property_registry_path)
            if settings.property_registry_path
            else None,
        )
        app_.state.clients = clients

        if clients.s3 and clients.s3.healthy_connection:
            logger.debug("S3 client connected successfully")
        else:
            logger.warning("S3 client connection failed")

        if clients.vitess and clients.vitess.healthy_connection:
            logger.debug("Vitess client connected successfully")
        else:
            logger.warning("Vitess client connection failed")

        logger.debug("Clients initialized successfully")

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
