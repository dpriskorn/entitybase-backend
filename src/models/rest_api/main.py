"""Main REST API application module."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from jsonschema import ValidationError  # type: ignore[import-untyped]

from models.config.settings import settings
from models.rest_api.entitybase.v1.endpoints import v1_router
from models.rest_api.entitybase.v1.handlers.state import StateHandler
from models.rest_api.entitybase.v1.routes import include_routes

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

for logger_name in aws_loggers:
    logging.getLogger(logger_name).setLevel(logging.INFO)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown tasks."""
    try:
        logger.debug("Initializing clients...")
        s3_config = settings.to_s3_config()
        vitess_config = settings.to_vitess_config()
        kafka_brokers = settings.kafka_brokers
        kafka_entity_change_topic = settings.kafka_entitychange_json_topic
        logger.debug(f"S3 config: {s3_config}")
        logger.debug(f"Vitess config: {vitess_config}")
        logger.debug(
            f"Kafka config: brokers={kafka_brokers}, topic={kafka_entity_change_topic}"
        )

        property_registry_path = (
            Path("test_data/properties")
            if Path("test_data/properties").exists()
            else None
        )
        logger.debug(f"Property registry path: {property_registry_path}")

        app_.state.state_handler = StateHandler(
            s3_config=s3_config,
            vitess_config=vitess_config,
            streaming_enabled=settings.streaming_enabled,
            kafka_brokers=settings.kafka_brokers,
            kafka_entitychange_topic=settings.kafka_entitychange_json_topic,
            kafka_entitydiff_topic=settings.kafka_entity_diff_topic,
            property_registry_path=property_registry_path,
            entity_change_stream_config=settings.get_entity_change_stream_config(),
            entity_diff_stream_config=settings.get_entity_diff_stream_config(),
        )
        app_.state.clients = app_.state.state_handler

        # Create database tables on startup (only if vitess is available)
        try:
            logger.debug("Creating database tables...")
            from models.infrastructure.vitess.repositories.schema import SchemaRepository
            schema_repository = SchemaRepository(vitess_client=app_.state.clients.vitess_client)
            schema_repository.create_tables()
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.warning(f"Could not create database tables on startup: {e}")
            logger.info("Tables will be created when first accessed or in tests")

        logger.info("Streaming clients initialized (lazy startup)")

        logger.debug(
            "Clients, validator, and enumeration service initialized successfully"
        )
        yield
    except Exception as e:
        logger.error(
            f"Failed to initialize clients: {type(e).__name__}: {e}", exc_info=True
        )
        raise
    finally:
        # assert isinstance(app_.state.clients, State)
        if (
            settings.streaming_enabled
            and app_.state.clients.entity_change_stream_producer
        ):
            await app_.state.clients.entity_change_stream_producer.stop()
            logger.info("entitychange_stream_producer stopped")

        if settings.streaming_enabled and app_.state.clients.entitydiff_stream_producer:
            await app_.state.clients.entitydiff_stream_producer.stop()
            logger.info("entitydiff_stream_producer stopped")


app = FastAPI(
    title="EntityBase", version="1.0.0", openapi_version="3.1", lifespan=lifespan
)


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
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with proper JSON formatting."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError from validation errors in dev mode."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": str(exc),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all exceptions and return formatted JSON response."""
    is_prod = os.getenv("ENVIRONMENT", "dev").lower() == "prod"
    
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)
    
    if is_prod:
        message = "An internal error occurred"
        detail = None
    else:
        message = str(exc)
        detail = f"{type(exc).__name__}: {exc}"
    
    content = {
        "error": "internal_error",
        "message": message,
    }
    
    if detail:
        content["detail"] = detail
    
    return JSONResponse(
        status_code=500,
        content=content,
    )


include_routes(app)

app.include_router(v1_router, prefix="/entitybase/v1")
# app.include_router(wikibase_v1_router, prefix="/wikibase/v1")


@app.get("/v1/openapi.json")
async def get_openapi() -> dict:
    """Retrieve the OpenAPI document."""
    openapi = app.openapi()
    assert isinstance(openapi, dict)
    return app.openapi()  # type: ignore


@app.get("/")
async def redirect_to_docs():
    """Redirect to the OpenAPI docs."""
    return RedirectResponse(url="/docs")

