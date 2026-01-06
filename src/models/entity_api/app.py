import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from models.config.settings import settings
from models.entity_api.clients import Clients

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Wikibase Backend API",
    description="Backend API for Wikibase entity management",
    version="1.0.0",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.debug("Initializing clients...")
        clients = Clients(
            s3=settings.s3,
            vitess=settings.vitess,
            property_registry_path=settings.property_registry_path,
        )
        app.state.clients = clients

        if clients.s3 and clients.s3.check_connection():
            logger.debug("S3 client connected successfully")
        else:
            logger.warning("S3 client connection failed")

        if clients.vitess and clients.vitess.check_connection():
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


app.router.lifespan_context = lifespan
