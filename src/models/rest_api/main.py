"""Main REST API application module."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from jsonschema import ValidationError  # type: ignore[import-untyped]

from models.config.settings import settings
from models.rest_api.clients import Clients
from models.validation.json_schema_validator import JsonSchemaValidator
from .entitybase.services.enumeration_service import EnumerationService
from models.rest_api.entitybase.versions.v1 import v1_router

log_level = settings.get_log_level()

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

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
        kafka_topic = settings.kafka_topic
        logger.debug(f"S3 config: {s3_config}")
        logger.debug(f"Vitess config: {vitess_config}")
        logger.debug(f"Kafka config: brokers={kafka_brokers}, topic={kafka_topic}")

        property_registry_path = (
            Path("test_data/properties")
            if Path("test_data/properties").exists()
            else None
        )
        logger.debug(f"Property registry path: {property_registry_path}")

        app_.state.clients = Clients(
            s3=s3_config,
            vitess=vitess_config,
            enable_streaming=settings.enable_streaming,
            kafka_brokers=kafka_brokers,
            kafka_topic=kafka_topic,
            kafka_rdf_topic=settings.kafka_rdf_topic,
            property_registry_path=property_registry_path,
        )

        if app_.state.clients.stream_producer:
            await app_.state.clients.stream_producer.start()
            logger.info("Stream producer started")

        if app_.state.clients.rdf_stream_producer:
            await app_.state.clients.rdf_stream_producer.start()
            logger.info("RDF stream producer started")

        app_.state.validator = JsonSchemaValidator(
            s3_revision_version=settings.s3_revision_version,
            s3_statement_version=settings.s3_statement_version,
            wmf_recentchange_version=settings.wmf_recentchange_version,
        )

        app_.state.enumeration_service = EnumerationService(
            app_.state.clients.vitess, worker_id="rest-api"
        )
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
        if app_.state.clients.stream_producer:
            await app_.state.clients.stream_producer.stop()
            logger.info("Stream producer stopped")

        if app_.state.clients.rdf_stream_producer:
            await app_.state.clients.rdf_stream_producer.stop()
            logger.info("RDF stream producer stopped")


app = FastAPI(lifespan=lifespan)


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


from models.rest_api.entitybase.routes import include_routes

include_routes(app)

app.include_router(v1_router, prefix="/entitybase/v1")
# app.include_router(wikibase_v1_router, prefix="/wikibase/v1")
