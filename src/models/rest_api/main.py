"""Main REST API application module."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from jsonschema import ValidationError  # type: ignore[import-untyped]
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
# from starlette.exceptions import StarletteHTTPException

from models.config.settings import settings
from models.rest_api.entitybase.v1.endpoints import v1_router
from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.routes import include_routes
from models.rest_api.utils import raise_validation_error

aws_loggers = [
    "botocore",
    "boto3",
    "urllib3",
    "s3transfer",
    "botocore.hooks",
    "botocore.retryhandler",
    "botocore.utils",
    "botocore.parsers",
    "botocore.endpoint",
    "botocore.auth",
]

aiokafka_loggers = [
    "aiokafka.conn",
    "aiokafka.consumer.group_coordinator",
    "aiokafka.consumer.fetcher",
    "aiokafka.consumer.subscription_state",
    "aiokafka.coordinator.assignor",
    "aiokafka.coordinator.heartbeat",
]

for logger_name in aws_loggers:
    logging.getLogger(logger_name).setLevel(logging.INFO)

for logger_name in aiokafka_loggers:
    logging.getLogger(logger_name).setLevel(logging.INFO)

logger = logging.getLogger(__name__)


class StartupMiddleware(BaseHTTPMiddleware):
    """Middleware to protect endpoints during application startup.

    Returns 503 for non-essential endpoints while state_handler is initializing.
    Always allows /health, /docs, and /openapi.json through.
    """

    async def dispatch(
        self, request: StarletteRequest, call_next: Any
    ) -> StarletteResponse:
        allowed_paths = {"/health", "/docs", "/openapi.json", "/redoc"}
        request_path = request.url.path

        if request_path not in allowed_paths:
            state_handler = getattr(request.app.state, "state_handler", None)
            if state_handler is None:
                logger.debug(
                    f"Rejecting request to {request_path} during initialization"
                )
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": "Service Unavailable",
                        "message": "Application is initializing. Please try again shortly.",
                    },
                )

        return await call_next(request)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown tasks."""
    try:
        state_handler = await _initialize_state_handler()
        await _create_database_tables(state_handler)
        await _initialize_app_state(app_, state_handler)
        yield
    except Exception as e:
        logger.error(
            f"Failed to initialize clients: {type(e).__name__}: {e}", exc_info=True
        )
        raise
    finally:
        await _cleanup_app_state(app_)


async def _initialize_state_handler() -> StateHandler:
    """Initialize the state handler."""
    state_handler = StateHandler(settings=settings)
    state_handler.start()
    return state_handler


async def _create_database_tables(state_handler: StateHandler) -> None:
    """Create database tables on startup."""
    try:
        logger.debug("Creating database tables...")
        from models.infrastructure.vitess.repositories.schema import SchemaRepository

        schema_repository = SchemaRepository(vitess_client=state_handler.vitess_client)
        schema_repository.create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.warning(f"Could not create database tables on startup: {e}")
        logger.info("Tables will be created when first accessed or in tests")


async def _initialize_app_state(app_: FastAPI, state_handler: StateHandler) -> None:
    """Initialize app state and log success."""
    logger.info("Clients, validator, and enumeration service initialized successfully")
    app_.state.state_handler = state_handler


async def _cleanup_app_state(app_: FastAPI) -> None:
    """Cleanup app state on shutdown."""
    if hasattr(app_.state, "state_handler") and app_.state.state_handler:
        app_.state.state_handler.disconnect()
        logger.info("All clients disconnected")

    await _stop_stream_producer(
        app_, "entitychange_stream_producer", "entitychange_stream_producer stopped"
    )
    await _stop_stream_producer(
        app_, "entitydiff_stream_producer", "entitydiff_stream_producer stopped"
    )


async def _stop_stream_producer(
    app_: FastAPI, producer_attr: str, log_message: str
) -> None:
    """Stop a stream producer if it exists."""
    if (
        hasattr(app_.state, "state_handler")
        and app_.state.state_handler
        and settings.streaming_enabled
        and getattr(app_.state.state_handler, producer_attr, None)
    ):
        producer = getattr(app_.state.state_handler, producer_attr)
        await producer.stop()
        logger.info(log_message)


app = FastAPI(
    title="EntityBase",
    version="1.0.0",
    openapi_version="3.1",
    lifespan=lifespan,
    response_model_by_alias=True,
)
app.add_middleware(StartupMiddleware)


@app.exception_handler(ValidationError)
async def validation_error_handler(exc: ValidationError) -> JSONResponse:
    """Handle JSON schema validation errors and return formatted response."""
    error_field = f"{'/' + '/'.join(str(p) for p in exc.path) if exc.path else '/'}"
    error_message = exc.message
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": "JSON schema validation failed",
            "details": [
                {
                    "field": error_field,
                    "message": error_message,
                    "path": list(exc.path),
                }
            ],
        },
    )


@app.exception_handler(HTTPException)
async def starlette_http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Handle StarletteHTTPException with proper JSON formatting."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail if exc.detail else "Not Found",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all exceptions and return formatted JSON response."""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)

    content = {
        "error": "internal_error",
        "message": str(exc),
        "detail": f"{type(exc).__name__}: {exc}",
    }

    return JSONResponse(
        status_code=500,
        content=content,
    )


include_routes(app)

app.include_router(v1_router, prefix=settings.api_prefix)
# app.include_router(wikibase_v1_router, prefix="/wikibase/v1")


@app.get("/v1/openapi.json")
async def get_openapi() -> dict:
    """Retrieve the OpenAPI document."""
    openapi = app.openapi()
    if not isinstance(openapi, dict):
        raise_validation_error("OpenAPI schema generation failed", status_code=500)
    return openapi


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    """Redirect to the OpenAPI docs."""
    return RedirectResponse(url="/docs")
