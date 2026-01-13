"""Main REST API application module."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Header, Query, Response
from fastapi.responses import JSONResponse
from jsonschema import ValidationError

from models.config.settings import settings
from models.rest_api.clients import Clients
from models.rest_api.handlers.admin import AdminHandler
from models.rest_api.handlers.entity.delete import EntityDeleteHandler
from models.rest_api.handlers.entity.read import EntityReadHandler
from models.rest_api.handlers.export import ExportHandler
from models.rest_api.handlers.redirect import RedirectHandler
from models.rest_api.handlers.statement import StatementHandler
from models.rest_api.handlers.system import health_check
from models.rest_api.handlers.user import UserHandler
from models.rest_api.handlers.watchlist import WatchlistHandler
from models.rest_api.handlers.entity.revert import EntityRevertHandler
from models.rest_api.handlers.user_activity import UserActivityHandler
from models.rest_api.request.entity import (
    EntityDeleteRequest,
    EntityRedirectRequest,
    RedirectRevertRequest,
    EntityRevertRequest,
)
from models.rest_api.request.user import UserCreateRequest, WatchlistToggleRequest
from models.rest_api.response.entity import EntityRevertResponse
from models.rest_api.response.health import HealthCheckResponse
from models.rest_api.response.misc import (
    RawRevisionResponse,
    RevisionMetadataResponse,
    WatchCounts,
)
from models.rest_api.response.misc import TtlResponse
from models.rest_api.response.statement import (
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
)
from models.rest_api.response.user import (
    UserCreateResponse,
    WatchlistToggleResponse,
    MessageResponse,
)
from models.rest_api.response.user_activity import UserActivityResponse
from models.rest_api.response.user_preferences import UserPreferencesResponse
from models.rest_api.request.user_preferences import UserPreferencesRequest
from models.rest_api.handlers.user_preferences import UserPreferencesHandler
from models.user import User
from models.watchlist import (
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    WatchlistResponse,
    NotificationResponse,
    MarkCheckedRequest,
)
from models.rest_api.services.enumeration_service import EnumerationService
from models.validation.json_schema_validator import JsonSchemaValidator
from .entitybase.v1 import v1_router
from .response.entity.entitybase import (
    EntityResponse,
    EntityRedirectResponse,
    EntityDeleteResponse,
    EntityListResponse,
)
from .wikibase.v1 import wikibase_v1_router

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


@app.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response) -> HealthCheckResponse:
    """Health check endpoint for monitoring service status."""
    return health_check(response)


@app.get("/v1/health")
def health_redirect() -> EntityRedirectResponse:
    """Redirect legacy /v1/health endpoint to /health."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/health", status_code=302)


@app.post("/v1/users", response_model=UserCreateResponse)
def create_user(request: UserCreateRequest) -> UserCreateResponse:
    """Create/register a user with MediaWiki user ID."""
    clients = app.state.clients
    handler = UserHandler()
    return handler.create_user(request, clients.vitess)


@app.get("/v1/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    """Get user information by MediaWiki user ID."""
    clients = app.state.clients
    handler = UserHandler()
    return handler.get_user(user_id, clients.vitess)


@app.put("/v1/users/{user_id}/watchlist/toggle", response_model=WatchlistToggleResponse)
def toggle_watchlist(
    user_id: int, request: WatchlistToggleRequest
) -> WatchlistToggleResponse:
    """Enable or disable watchlist for user."""
    clients = app.state.clients
    handler = UserHandler()
    try:
        return handler.toggle_watchlist(user_id, request, clients.vitess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/watchlist", response_model=MessageResponse)
def add_watch(request: WatchlistAddRequest) -> MessageResponse:
    """Add a watchlist entry."""
    clients = app.state.clients
    handler = WatchlistHandler()
    try:
        return handler.add_watch(request, clients.vitess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/v1/watchlist", response_model=MessageResponse)
def remove_watch(request: WatchlistRemoveRequest) -> MessageResponse:
    """Remove a watchlist entry."""
    clients = app.state.clients
    handler = WatchlistHandler()
    return handler.remove_watch(request, clients.vitess)


@app.get("/v1/watchlist", response_model=WatchlistResponse)
def get_watchlist(
    user_id: int = Query(..., description="MediaWiki user ID"),
) -> WatchlistResponse:
    """Get user's watchlist."""
    clients = app.state.clients
    handler = WatchlistHandler()
    try:
        return handler.get_watches(user_id, clients.vitess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/watchlist/counts")
def get_watch_counts(
    user_id: int = Query(..., description="MediaWiki user ID"),
) -> WatchCounts:
    """Get user's watch counts."""
    clients = app.state.clients
    handler = WatchlistHandler()
    try:
        return handler.get_watch_counts(user_id, clients.vitess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/watchlist/notifications", response_model=NotificationResponse)
def get_notifications(
    user_id: int = Query(..., description="MediaWiki user ID"),
    hours: int = Query(24, ge=1, le=720, description="Time span in hours (1-720)"),
    limit: int = Query(50, description="Number of notifications (50, 100, 250, 500)"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
) -> NotificationResponse:
    """Get user's recent watchlist notifications within time span."""
    # Validate limit
    allowed_limits = [50, 100, 250, 500]
    if limit not in allowed_limits:
        raise HTTPException(
            status_code=400, detail=f"Limit must be one of {allowed_limits}"
        )

    clients = app.state.clients
    handler = WatchlistHandler()
    try:
        return handler.get_notifications(user_id, clients.vitess, hours, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/watchlist/notifications/check", response_model=MessageResponse)
def mark_notification_checked(
    request: MarkCheckedRequest,
    user_id: int = Query(..., description="MediaWiki user ID"),
) -> MessageResponse:
    """Mark a notification as checked."""
    clients = app.state.clients
    handler = WatchlistHandler()
    return handler.mark_checked(user_id, request, clients.vitess)


@app.get("/v1/users/{user_id}/activity", response_model=UserActivityResponse)
def get_user_activity(
    user_id: int,
    type: str | None = Query(None, description="Activity type filter"),
    hours: int = Query(24, ge=1, le=720, description="Time span in hours"),
    limit: int = Query(50, description="Number of activities (50, 100, 250, 500)"),
    offset: int = Query(0, ge=0, description="Number of activities to skip"),
) -> UserActivityResponse:
    """Get user's activity history."""
    logger.debug(f"Getting user activity for user {user_id} with type {type}")
    # Validate limit
    allowed_limits = [50, 100, 250, 500]
    if limit not in allowed_limits:
        raise HTTPException(
            status_code=400, detail=f"Limit must be one of {allowed_limits}"
        )

    clients = app.state.clients
    handler = UserActivityHandler()
    try:
        return handler.get_user_activities(
            user_id, clients.vitess, type, hours, limit, offset
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/v1/users/{user_id}/preferences", response_model=UserPreferencesResponse)
def get_user_preferences(user_id: int) -> UserPreferencesResponse:
    """Get user's notification preferences."""
    clients = app.state.clients
    handler = UserPreferencesHandler()
    try:
        return handler.get_preferences(user_id, clients.vitess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/v1/users/{user_id}/preferences", response_model=UserPreferencesResponse)
def update_user_preferences(
    user_id: int, request: UserPreferencesRequest
) -> UserPreferencesResponse:
    """Update user's notification preferences."""
    clients = app.state.clients
    handler = UserPreferencesHandler()
    try:
        return handler.update_preferences(user_id, request, clients.vitess)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/entitybase/v1/entities/{entity_id}/revert", response_model=EntityRevertResponse
)
def revert_entity(
    entity_id: str,
    request: EntityRevertRequest,
    user_id: int = Header(..., alias="X-User-ID"),
) -> EntityRevertResponse:
    """Revert an entity to a previous revision."""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Valid user ID required")

    clients = app.state.clients
    handler = EntityRevertHandler()
    return handler.revert_entity(entity_id, request, clients.vitess, user_id)


@v1_router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str) -> EntityResponse:
    """Retrieve a single entity by its ID."""
    clients = app.state.clients
    handler = EntityReadHandler()
    return handler.get_entity(entity_id, clients.vitess, clients.s3)


@v1_router.get(
    "/entities/{entity_id}/history", response_model=list[RevisionMetadataResponse]
)
def get_entity_history(
    entity_id: str,
    limit: int = Query(
        20, ge=1, le=100, description="Maximum number of revisions to return"
    ),
    offset: int = Query(0, ge=0, description="Number of revisions to skip"),
) -> list[Any]:
    """Get the revision history for an entity."""
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
    return cast(EntityRedirectResponse, await handler.create_entity_redirect(request))


@app.post("/entities/{entity_id}/revert-redirect")
async def revert_entity_redirect(
    entity_id: str, request: RedirectRevertRequest
) -> EntityRedirectResponse:
    clients = app.state.clients
    handler = RedirectHandler(clients.s3, clients.vitess, clients.stream_producer)
    return cast(EntityRedirectResponse, await handler.revert_entity_redirect(
        entity_id, request.revert_to_revision_id
    ))


@v1_router.delete("/entities/{entity_id}", response_model=EntityDeleteResponse)
async def delete_entity(
    entity_id: str, request: EntityDeleteRequest
) -> EntityDeleteResponse:
    clients = app.state.clients
    handler = EntityDeleteHandler()
    return cast(EntityDeleteResponse, await handler.delete_entity(
        entity_id, request, clients.vitess, clients.s3, clients.stream_producer
    ))


@v1_router.get(
    "/entities/{entity_id}/revisions/raw/{revision_id}",
    response_model=RawRevisionResponse,
)
def get_raw_revision(entity_id: str, revision_id: int) -> RawRevisionResponse:
    """Retrieve raw revision data from storage."""
    clients = app.state.clients
    handler = AdminHandler()
    return handler.get_raw_revision(entity_id, revision_id, clients.vitess, clients.s3)  # type: ignore


@app.get("/entities", response_model=EntityListResponse)
def list_entities(
    entity_type: str = Query(
        "",
        description="Entity type to filter by (item, property, lexeme, entityschema). Leave empty for all types",
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of entities to return"
    ),
    offset: int = Query(0, ge=0, description="Number of entities to skip"),
) -> EntityRedirectResponse:
    """List entities based on type, limit, and offset."""
    clients = app.state.clients
    handler = AdminHandler()
    return cast(EntityListResponse, handler.list_entities(
        vitess_client=clients.vitess,
        entity_type=entity_type,
        limit=limit,
        offset=offset,
    ))


@v1_router.get("/entities/{entity_id}/properties", response_model=PropertyListResponse)
def get_entity_properties(entity_id: str) -> PropertyListResponse:
    """Get list of properties used by an entity."""
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_properties(entity_id, clients.vitess, clients.s3)


@v1_router.get(
    "/entities/{entity_id}/properties/counts", response_model=PropertyCountsResponse
)
def get_entity_property_counts(entity_id: str) -> PropertyCountsResponse:
    """Get statement counts for each property in an entity."""
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
    """Get statement hashes for specified properties in an entity."""
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_property_hashes(
        entity_id, property_list, clients.vitess, clients.s3
    )


app.include_router(v1_router, prefix="/entitybase/v1")
app.include_router(wikibase_v1_router, prefix="/wikibase/v1")
