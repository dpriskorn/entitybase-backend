import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from jsonschema import ValidationError

from models.config.settings import settings
from models.validation.json_schema_validator import JsonSchemaValidator
from models.api_models import (
    CleanupOrphanedRequest,
    CleanupOrphanedResponse,
    EntityDeleteRequest,
    EntityDeleteResponse,
    EntityListResponse,
    EntityRedirectResponse,
    EntityResponse,
    EntityRedirectRequest,
    HealthCheckResponse,
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
    RedirectRevertRequest,
    RevisionMetadata,
    StatementBatchRequest,
    StatementBatchResponse,
    StatementResponse,
    TtlResponse,
)
from models.rest_api.clients import Clients
from models.rest_api.services.enumeration_service import EnumerationService
from models.rest_api.handlers.admin import AdminHandler
from models.rest_api.handlers.entity.read import EntityReadHandler
from models.rest_api.handlers.entity.delete import EntityDeleteHandler
from .v1 import v1_router
from models.rest_api.handlers.export import ExportHandler
from models.rest_api.handlers.redirect import RedirectHandler
from models.rest_api.handlers.statement import StatementHandler
from models.rest_api.handlers.system import health_check

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
            property_registry_path=property_registry_path,
        )

        if app_.state.clients.stream_producer:
            await app_.state.clients.stream_producer.start()
            logger.info("Stream producer started")

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


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ValidationError)
async def validation_error_handler(exc: ValidationError) -> JSONResponse:
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


@app.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response) -> HealthCheckResponse:
    return health_check(response)


@app.get("/v1/health")
def health_redirect() -> Any:
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/health", status_code=302)


@v1_router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str) -> EntityResponse:
    clients = app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity(entity_id, clients.vitess, clients.s3)


@v1_router.get("/entities/{entity_id}/history", response_model=list[RevisionMetadata])
def get_entity_history(entity_id: str, limit: int = 20, offset: int = 0) -> list[Any]:
    clients = app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity_history(  # type: ignore[no-any-return]
        entity_id, clients.vitess, clients.s3, limit, offset
    )


@v1_router.get("/entities/{entity_id}.ttl")
async def get_entity_data_turtle(entity_id: str) -> TtlResponse:
    clients = app.state.clients
    handler = ExportHandler()
    return handler.get_entity_data_turtle(
        entity_id, clients.vitess, clients.s3, clients.property_registry
    )


@app.post("/redirects")
async def create_entity_redirect(
    request: EntityRedirectRequest,
) -> EntityRedirectResponse:
    clients = app.state.clients
    handler = RedirectHandler(clients.s3, clients.vitess, clients.stream_producer)
    return await handler.create_entity_redirect(request)


@app.post("/entities/{entity_id}/revert-redirect")
async def revert_entity_redirect(
    entity_id: str, request: RedirectRevertRequest
) -> EntityResponse:
    clients = app.state.clients
    handler = RedirectHandler(clients.s3, clients.vitess, clients.stream_producer)
    return await handler.revert_entity_redirect(
        entity_id, request.revert_to_revision_id
    )


@v1_router.delete("/entities/{entity_id}", response_model=EntityDeleteResponse)
async def delete_entity(
    entity_id: str, request: EntityDeleteRequest
) -> EntityDeleteResponse:
    clients = app.state.clients
    handler = EntityDeleteHandler()
    return await handler.delete_entity(
        entity_id, request, clients.vitess, clients.s3, clients.stream_producer
    )


@v1_router.get("/entities/{entity_id}/revisions/raw/{revision_id}")
def get_raw_revision(entity_id: str, revision_id: int) -> Dict[str, Any]:
    clients = app.state.clients
    handler = AdminHandler()
    return handler.get_raw_revision(entity_id, revision_id, clients.vitess, clients.s3)  # type: ignore


@app.get("/entities", response_model=EntityListResponse)
def list_entities(
    status: Optional[str] = None, edit_type: Optional[str] = None, limit: int = 100
) -> EntityListResponse:
    clients = app.state.clients
    handler = AdminHandler()
    return handler.list_entities(clients.vitess, status, edit_type, limit)


@app.get("/statement/{content_hash}", response_model=StatementResponse)
def get_statement(content_hash: int) -> StatementResponse:
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_statement(content_hash, clients.s3)


@app.post("/statements/batch", response_model=StatementBatchResponse)
def get_statements_batch(request: StatementBatchRequest) -> StatementBatchResponse:
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_statements_batch(request, clients.s3)


@v1_router.get("/entities/{entity_id}/properties", response_model=PropertyListResponse)
def get_entity_properties(entity_id: str) -> PropertyListResponse:
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_properties(entity_id, clients.vitess, clients.s3)


@v1_router.get(
    "/entities/{entity_id}/properties/counts", response_model=PropertyCountsResponse
)
def get_entity_property_counts(entity_id: str) -> PropertyCountsResponse:
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_property_counts(entity_id, clients.vitess, clients.s3)


@app.get(
    "/entity/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
def get_entity_property_hashes(
    entity_id: str, property_list: str
) -> PropertyHashesResponse:
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_property_hashes(
        entity_id, property_list, clients.vitess, clients.s3
    )


@app.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(
    request: CleanupOrphanedRequest,
) -> CleanupOrphanedResponse:
    clients = app.state.clients
    handler = AdminHandler()
    return handler.cleanup_orphaned_statements(request, clients.vitess, clients.s3)


app.include_router(v1_router)
