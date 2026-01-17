"""Main REST API application module."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Header, Query, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from jsonschema import ValidationError

from models.config.settings import settings
from models.rest_api.clients import Clients
from models.rest_api.entitybase.handlers import ExportHandler
from models.rest_api.entitybase.handlers import StatementHandler
from models.rest_api.entitybase.handlers import health_check
from models.rest_api.entitybase.handlers.admin import AdminHandler
from models.rest_api.entitybase.handlers.entity import EntityDeleteHandler
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.handlers.entity.revert import EntityRevertHandler
from models.rest_api.entitybase.handlers.redirect import RedirectHandler
from models.rest_api.entitybase.handlers.watchlist import WatchlistHandler
from models.rest_api.entitybase.request.entity import (
    EntityDeleteRequest,
    EntityRedirectRequest,
    RedirectRevertRequest,
    EntityRevertRequest,
)
from models.rest_api.entitybase.request.user import (
    UserCreateRequest,
    WatchlistToggleRequest,
)
from models.rest_api.entitybase.request.user_preferences import UserPreferencesRequest
from models.rest_api.entitybase.response import (
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
)
from models.rest_api.entitybase.response import (
    TtlResponse,
    RevisionMetadataResponse,
    HealthCheckResponse,
)
from models.rest_api.entitybase.response.entity.entitybase import (
    EntityResponse,
    EntityRedirectResponse,
    EntityDeleteResponse,
    EntityListResponse,
)
from models.user import User
from models.validation.json_schema_validator import JsonSchemaValidator
from models.validation.utils import raise_validation_error
from models.watchlist import (
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    WatchlistResponse,
    NotificationResponse,
    MarkCheckedRequest,
)
from .entitybase.handlers.user import UserHandler
from .entitybase.handlers.user_activity import UserActivityHandler
from .entitybase.handlers.user_preferences import UserPreferencesHandler
from .entitybase.handlers.thanks import ThanksHandler
from .entitybase.handlers.endorsements import EndorsementHandler
from .entitybase.response.entity import EntityRevertResponse
from .entitybase.response.misc import RawRevisionResponse, WatchCounts
from .entitybase.response.user import (
    MessageResponse,
    WatchlistToggleResponse,
    UserCreateResponse,
)
from .entitybase.response.user_activity import UserActivityResponse
from .entitybase.response.user_preferences import UserPreferencesResponse
from .entitybase.response.thanks import ThankResponse, ThanksListResponse
from .entitybase.request.thanks import ThanksListRequest
from .entitybase.response.endorsements import (
    BatchEndorsementStatsResponse,
    EndorsementResponse,
    EndorsementListResponse,
    EndorsementStatsResponse,
    SingleEndorsementStatsResponse,
)
from .entitybase.request.endorsements import EndorsementListRequest
from .entitybase.services.enumeration_service import EnumerationService
from .entitybase.v1 import v1_router

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


@app.get("/health", response_model=HealthCheckResponse)
def health_check_endpoint(response: Response) -> HealthCheckResponse:
    """Health check endpoint for monitoring service status."""
    return health_check(response)


@app.get("/v1/health")
def health_redirect() -> RedirectResponse:
    """Redirect legacy /v1/health endpoint to /health."""
    return RedirectResponse(url="/health", status_code=302)


@app.post("/v1/users", response_model=UserCreateResponse)
def create_user(request: UserCreateRequest) -> UserCreateResponse:
    """Create a new user."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = UserHandler()
    result = handler.create_user(request, clients.vitess)
    if not isinstance(result, UserCreateResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, UserCreateResponse)
    return result


@app.get("/v1/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    """Get user information by MediaWiki user ID."""
    clients = app.state.clients
    handler = UserHandler()
    result = handler.get_user(user_id, clients.vitess)
    if not isinstance(result, User):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@app.put("/v1/users/{user_id}/watchlist/toggle", response_model=WatchlistToggleResponse)
def toggle_watchlist(
    user_id: int, request: WatchlistToggleRequest
) -> WatchlistToggleResponse:
    """Enable or disable watchlist for user."""
    clients = app.state.clients
    handler = UserHandler()
    try:
        result = handler.toggle_watchlist(user_id, request, clients.vitess)
        if not isinstance(result, WatchlistToggleResponse):
            raise_validation_error("Invalid response type", status_code=500)
        assert isinstance(result, WatchlistToggleResponse)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thank",
    response_model=ThankResponse,
)
def send_thank_endpoint(
    entity_id: str, revision_id: int, user_id: int = Header(..., alias="X-User-ID")
) -> ThankResponse:
    """Send a thank for a specific revision."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    result = handler.send_thank(entity_id, revision_id, user_id, clients.vitess)
    if not isinstance(result, ThankResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThankResponse)
    return result


@app.get(
    "/entitybase/v1/users/{user_id}/thanks/received", response_model=ThanksListResponse
)
def get_thanks_received_endpoint(
    user_id: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of thanks to return"
    ),
    offset: int = Query(0, ge=0, description="Number of thanks to skip"),
    hours: int = Query(24, ge=1, le=720, description="Time span in hours"),
) -> ThanksListResponse:
    """Get thanks received by user."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    request = ThanksListRequest(limit=limit, offset=offset, hours=hours)
    result = handler.get_thanks_received(user_id, request, clients.vitess)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThanksListResponse)
    return result


@app.get(
    "/entitybase/v1/users/{user_id}/thanks/sent", response_model=ThanksListResponse
)
def get_thanks_sent_endpoint(
    user_id: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of thanks to return"
    ),
    offset: int = Query(0, ge=0, description="Number of thanks to skip"),
    hours: int = Query(24, ge=1, le=720, description="Time span in hours"),
) -> ThanksListResponse:
    """Get thanks sent by user."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    request = ThanksListRequest(limit=limit, offset=offset, hours=hours)
    result = handler.get_thanks_sent(user_id, request, clients.vitess)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThanksListResponse)
    return result


@app.get(
    "/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thanks",
    response_model=ThanksListResponse,
)
def get_revision_thanks_endpoint(entity_id: str, revision_id: int) -> ThanksListResponse:
    """Get all thanks for a specific revision."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = ThanksHandler()
    result = handler.get_revision_thanks(entity_id, revision_id, clients.vitess)
    if not isinstance(result, ThanksListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, ThanksListResponse)
    return result


@app.post(
    "/entitybase/v1/statements/{statement_hash}/endorse",
    response_model=EndorsementResponse,
)
def endorse_statement_endpoint(
    statement_hash: int, user_id: int = Header(..., alias="X-User-ID")
) -> EndorsementResponse:
    """Endorse a statement to signal trust."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    result = handler.endorse_statement(statement_hash, user_id, clients.vitess)
    if not isinstance(result, EndorsementResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementResponse)
    return result


@app.delete(
    "/entitybase/v1/statements/{statement_hash}/endorse",
    response_model=EndorsementResponse,
)
def withdraw_endorsement_endpoint(
    statement_hash: int, user_id: int = Header(..., alias="X-User-ID")
) -> EndorsementResponse:
    """Withdraw endorsement from a statement."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    result = handler.withdraw_endorsement(statement_hash, user_id, clients.vitess)
    if not isinstance(result, EndorsementResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementResponse)
    return result


@app.get(
    "/entitybase/v1/statements/{statement_hash}/endorsements",
    response_model=EndorsementListResponse,
)
def get_statement_endorsements_endpoint(
    statement_hash: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of endorsements to return"
    ),
    offset: int = Query(0, ge=0, description="Number of endorsements to skip"),
    include_removed: bool = Query(False, description="Include withdrawn endorsements"),
) -> EndorsementListResponse:
    """Get endorsements for a statement."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    request = EndorsementListRequest(
        limit=limit, offset=offset, include_removed=include_removed
    )
    result = handler.get_statement_endorsements(statement_hash, request, clients.vitess)
    if not isinstance(result, EndorsementListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementListResponse)
    return result


@app.get(
    "/entitybase/v1/users/{user_id}/endorsements",
    response_model=EndorsementListResponse,
)
def get_user_endorsements_endpoint(
    user_id: int,
    limit: int = Query(
        50, ge=1, le=500, description="Maximum number of endorsements to return"
    ),
    offset: int = Query(0, ge=0, description="Number of endorsements to skip"),
    include_removed: bool = Query(False, description="Include withdrawn endorsements"),
) -> EndorsementListResponse:
    """Get endorsements given by a user."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    request = EndorsementListRequest(
        limit=limit, offset=offset, include_removed=include_removed
    )
    result = handler.get_user_endorsements(user_id, request, clients.vitess)
    if not isinstance(result, EndorsementListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementListResponse)
    return result


@app.get(
    "/entitybase/v1/users/{user_id}/endorsements/stats",
    response_model=EndorsementStatsResponse,
)
def get_user_endorsement_stats_endpoint(user_id: int) -> EndorsementStatsResponse:
    """Get endorsement statistics for a user."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EndorsementHandler()
    result = handler.get_user_endorsement_stats(user_id, clients.vitess)
    if not isinstance(result, EndorsementStatsResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EndorsementStatsResponse)
    return result


@app.get(
    "/entitybase/v1/statements/{statement_hash}/endorsements/stats",
    response_model=SingleEndorsementStatsResponse,
)
def get_statement_endorsement_stats(
    statement_hash: int,
) -> SingleEndorsementStatsResponse:
    """Get endorsement statistics for a statement."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)

    # Get stats for single statement
    handler = EndorsementHandler()
    result = handler.get_batch_statement_endorsement_stats(
        [statement_hash], clients.vitess
    )
    if not isinstance(result, BatchEndorsementStatsResponse):
        raise_validation_error("Invalid response type", status_code=500)

    if not result.stats:
        raise_validation_error("Statement not found", status_code=404)

    # Convert batch response to single response
    stat = result.stats[0]
    return SingleEndorsementStatsResponse(
        total=stat.total, active=stat.active, withdrawn=stat.withdrawn
    )


@app.post(
    "/entitybase/v1/entities/{entity_id}/revert", response_model=EntityRevertResponse
)
def revert_entity(
    entity_id: str,
    request: EntityRevertRequest,
    user_id: int = Header(..., alias="X-User-ID"),
) -> EntityRevertResponse:
    """Revert entity to a previous revision."""
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityRevertHandler()
    result = handler.revert_entity(entity_id, request, clients.vitess, user_id)
    if not isinstance(result, EntityRevertResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, EntityRevertResponse)
    return result


@v1_router.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str, req: Request) -> EntityResponse:
    """Retrieve a single entity by its ID."""
    # noinspection PyUnresolvedReferences
    clients = req.app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = EntityReadHandler()
    result = handler.get_entity(entity_id, clients.vitess, clients.s3)
    if not isinstance(result, EntityResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


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
    result = handler.get_entity_data_turtle(
        entity_id, clients.vitess, clients.s3, clients.property_registry
    )
    if not isinstance(result, TtlResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@app.post("/redirects")
async def create_entity_redirect(
    request: EntityRedirectRequest,
) -> EntityRedirectResponse:
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(clients.s3, clients.vitess, clients.stream_producer)
    result = await handler.create_entity_redirect(request)
    if not isinstance(result, EntityRedirectResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@app.post("/entities/{entity_id}/revert-redirect")
async def revert_entity_redirect(  # type: ignore[no-any-return]
    entity_id: str, request: RedirectRevertRequest
) -> EntityResponse:
    clients = app.state.clients
    if not isinstance(clients, Clients):
        raise_validation_error("Invalid clients type", status_code=500)
    handler = RedirectHandler(clients.s3, clients.vitess, clients.stream_producer)
    result = await handler.revert_entity_redirect(
        entity_id, request.revert_to_revision_id
    )
    if not isinstance(result, EntityResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@v1_router.delete("/entities/{entity_id}", response_model=EntityDeleteResponse)
async def delete_entity(  # type: ignore[no-any-return]
    entity_id: str, request: EntityDeleteRequest
) -> EntityDeleteResponse:
    clients = app.state.clients
    handler = EntityDeleteHandler()
    result = await handler.delete_entity(
        entity_id, request, clients.vitess, clients.s3, clients.stream_producer
    )
    if not isinstance(result, EntityDeleteResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@v1_router.get(
    "/entities/{entity_id}/revisions/raw/{revision_id}",
    response_model=RawRevisionResponse,
)
def get_raw_revision(entity_id: str, revision_id: int) -> RawRevisionResponse:
    """Retrieve raw revision data from storage."""
    clients = app.state.clients
    handler = AdminHandler()
    result = handler.get_raw_revision(
        entity_id, revision_id, clients.vitess, clients.s3
    )  # type: ignore
    if not isinstance(result, RawRevisionResponse):
        raise_validation_error("Invalid response type", status_code=500)
    assert isinstance(result, RawRevisionResponse)
    return result


@app.get("/entities", response_model=EntityListResponse)
def list_entities(  # type: ignore[no-any-return]
    entity_type: str = Query(
        "",
        description="Entity type to filter by (item, property, lexeme, entityschema). Leave empty for all types",
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of entities to return"
    ),
    offset: int = Query(0, ge=0, description="Number of entities to skip"),
) -> EntityListResponse:
    """List entities based on type, limit, and offset."""
    clients = app.state.clients
    handler = AdminHandler()
    result = handler.list_entities(
        vitess_client=clients.vitess,
        entity_type=entity_type,
        limit=limit,
        offset=offset,
    )
    if not isinstance(result, EntityListResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@v1_router.get("/entities/{entity_id}/properties", response_model=PropertyListResponse)
async def get_entity_properties(entity_id: str, req: Request) -> PropertyListResponse:
    """Get properties for an entity."""
    clients = req.app.state.clients
    handler = StatementHandler()
    return handler.get_entity_properties(entity_id, clients.vitess, clients.s3)


@v1_router.get(
    "/entities/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
async def get_entity_property_hashes(
    entity_id: str, property_list: str
) -> PropertyHashesResponse:
    """Get statement hashes for specified properties in an entity."""
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_property_hashes(
        entity_id, property_list, clients.vitess, clients.s3
    )


@v1_router.get("/sitelinks/{hashes}")
async def get_batch_sitelinks(hashes: str, req: Request) -> dict[str, str]:
    """Get batch sitelink titles by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            title = clients.s3.load_sitelink_metadata(hash_value)
            if title:
                result[h] = title
        except ValueError:
            pass  # Skip invalid hashes
    return result


@v1_router.get("/labels/{hashes}")
async def get_batch_labels(hashes: str, req: Request) -> dict[str, str]:
    """Get batch labels by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            label = clients.s3.load_metadata("labels", hash_value)
            if label:
                result[h] = label
        except ValueError:
            pass
    return result


@v1_router.get("/descriptions/{hashes}")
async def get_batch_descriptions(hashes: str, req: Request) -> dict[str, str]:
    """Get batch descriptions by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            desc = clients.s3.load_metadata("descriptions", hash_value)
            if desc:
                result[h] = desc
        except ValueError:
            pass
    return result


@v1_router.get("/aliases/{hashes}")
async def get_batch_aliases(hashes: str, req: Request) -> dict[str, list[str]]:
    """Get batch aliases by hashes."""
    clients = req.app.state.clients
    hash_list = hashes.split(",")
    if len(hash_list) > 20:
        raise HTTPException(status_code=400, detail="Too many hashes (max 20)")
    result = {}
    for h in hash_list:
        try:
            hash_value = int(h.strip())
            aliases = clients.s3.load_metadata("aliases", hash_value)
            if aliases:
                result[h] = aliases
        except ValueError:
            pass
    return result


@v1_router.get("/statements/batch")
async def get_batch_statements(
    req: Request, entity_ids: str, property_ids: str | None = None
) -> dict[str, dict[str, list]]:
    """Get batch statements for entities and properties."""
    if req is None:
        raise HTTPException(status_code=500, detail="Request not provided")
    clients = req.app.state.clients
    entity_list = entity_ids.split(",")
    property_list = property_ids.split(",") if property_ids else None
    if len(entity_list) > 20:
        raise HTTPException(status_code=400, detail="Too many entities (max 20)")
    result = {}
    for entity_id in entity_list:
        entity_id = entity_id.strip()
        try:
            # Get entity revision
            handler = EntityReadHandler()
            entity_response = handler.get_entity(entity_id, clients.vitess, clients.s3)
            statements = entity_response.entity_data.get("statements", {})
            if property_list:
                filtered = {p: statements.get(p, []) for p in property_list}
                result[entity_id] = filtered
            else:
                result[entity_id] = statements
        except Exception:
            result[entity_id] = {}
    return result


def get_entity_property_counts(entity_id: str) -> PropertyCountsResponse:
    """Get statement counts for each property in an entity."""
    clients = app.state.clients
    handler = StatementHandler()
    result = handler.get_entity_property_counts(entity_id, clients.vitess, clients.s3)
    if not isinstance(result, PropertyCountsResponse):
        raise_validation_error("Invalid response type", status_code=500)
    return result


@app.get(
    "/entity/{entity_id}/properties/{property_list}",
    response_model=PropertyHashesResponse,
)
def get_entity_property_hashes_sync(
    entity_id: str, property_list: str
) -> PropertyHashesResponse:
    """Get statement hashes for specified properties in an entity."""
    clients = app.state.clients
    handler = StatementHandler()
    return handler.get_entity_property_hashes(
        entity_id, property_list, clients.vitess, clients.s3
    )


app.include_router(v1_router, prefix="/entitybase/v1")
# app.include_router(wikibase_v1_router, prefix="/wikibase/v1")
