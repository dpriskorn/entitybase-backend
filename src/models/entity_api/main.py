import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Response

from models.config.settings import settings
from models.entity import (
    CleanupOrphanedRequest,
    CleanupOrphanedResponse,
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityDeleteResponse,
    EntityRedirectResponse,
    EntityResponse,
    EntityRedirectRequest,
    HealthCheckResponse,
    MostUsedStatementsResponse,
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
from models.entity_api.clients import Clients
from models.entity_api.handlers.admin_handler import AdminHandler
from models.entity_api.handlers.entity_handler import EntityHandler
from models.entity_api.handlers.export_handler import ExportHandler
from models.entity_api.handlers.redirect_handler import RedirectHandler
from models.entity_api.handlers.statement_handler import StatementHandler
from models.entity_api.handlers.system_handler import health_check

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
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.debug("Initializing clients...")
        s3_config = settings.to_s3_config()
        vitess_config = settings.to_vitess_config()
        logger.debug(f"S3 config: {s3_config}")
        logger.debug(f"Vitess config: {vitess_config}")

        property_registry_path = (
            Path("test_data/properties")
            if Path("test_data/properties").exists()
            else None
        )
        logger.debug(f"Property registry path: {property_registry_path}")

        app.state.clients = Clients(
            s3=s3_config,
            vitess=vitess_config,
            property_registry_path=property_registry_path,
        )
        logger.debug("Clients initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


app = FastAPI(lifespan=lifespan)


@app.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response) -> HealthCheckResponse:
    return health_check(response)


@app.post("/entity", response_model=EntityResponse)
def create_entity(request: EntityCreateRequest) -> EntityResponse:
    clients = app.state.clients
    handler = EntityHandler()
    return handler.create_entity(request, clients.vitess, clients.s3)


@app.get("/entity/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str) -> EntityResponse:
    clients = app.state.clients
    handler = EntityHandler()
    return handler.get_entity(entity_id, clients.vitess, clients.s3)


@app.get("/entity/{entity_id}/history", response_model=list[RevisionMetadata])
def get_entity_history(
    entity_id: str, limit: int = 20, offset: int = 0
) -> list[RevisionMetadata]:
    clients = app.state.clients
    handler = EntityHandler()
    return handler.get_entity_history(entity_id, clients.vitess, limit, offset)  # type: ignore


@app.get("/entity/{entity_id}.ttl")
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
    handler = RedirectHandler(clients.s3, clients.vitess)
    return handler.create_entity_redirect(request)


@app.post("/entities/{entity_id}/revert-redirect")
async def revert_entity_redirect(
    entity_id: str, request: RedirectRevertRequest
) -> EntityResponse:
    clients = app.state.clients
    handler = RedirectHandler(clients.s3, clients.vitess)
    return handler.revert_entity_redirect(entity_id, request.revert_to_revision_id)


@app.get("/entity/{entity_id}/revision/{revision_id}", response_model=Dict[str, Any])
def get_entity_revision(entity_id: str, revision_id: int) -> Dict[str, Any]:
    clients = app.state.clients
    handler = EntityHandler()
    return handler.get_entity_revision(entity_id, revision_id, clients.s3)  # type: ignore


@app.delete("/entity/{entity_id}", response_model=EntityDeleteResponse)
def delete_entity(entity_id: str, request: EntityDeleteRequest) -> EntityDeleteResponse:
    clients = app.state.clients
    handler = EntityHandler()
    return handler.delete_entity(entity_id, request, clients.vitess, clients.s3)  # type: ignore


@app.get("/raw/{entity_id}/{revision_id}")
def get_raw_revision(entity_id: str, revision_id: int) -> Dict[str, Any]:
    clients = app.state.clients
    handler = AdminHandler()
    return handler.get_raw_revision(entity_id, revision_id, clients.vitess, clients.s3)  # type: ignore


# @app.get("/entities", response_model=EntityListResponse)
# def list_entities(
#     status: Optional[str] = None, edit_type: Optional[str] = None, limit: int = 100
# ) -> EntityListResponse:
#     clients = app.state.clients
#     handler = AdminHandler()
#     return handler.list_entities(clients.vitess, status, edit_type, limit)


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


@app.get("/entity/{entity_id}/properties", response_model=PropertyListResponse)
def get_entity_properties(entity_id: str) -> PropertyListResponse:
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_properties(entity_id, clients.vitess, clients.s3)


@app.get("/entity/{entity_id}/properties/counts", response_model=PropertyCountsResponse)
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


@app.get("/statement/most_used", response_model=MostUsedStatementsResponse)
def get_most_used_statements(
    limit: int = 100, min_ref_count: int = 1
) -> MostUsedStatementsResponse:
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_most_used_statements(clients.vitess, limit, min_ref_count)


@app.post("/statements/cleanup-orphaned", response_model=CleanupOrphanedResponse)
def cleanup_orphaned_statements(
    request: CleanupOrphanedRequest,
) -> CleanupOrphanedResponse:
    clients = app.state.clients
    handler = AdminHandler()
    return handler.cleanup_orphaned_statements(request, clients.vitess, clients.s3)
