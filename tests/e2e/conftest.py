import json
import logging
import os
import sys
from typing import Any

import pymysql
import pytest
import requests

sys.path.insert(0, "src")

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def validate_e2e_env_vars():
    """Validate required environment variables are set before running E2E tests.

    This fixture fails fast if required environment variables are missing,
    preventing long retry loops and confusing connection errors.
    """
    required_vars = {
        "VITESS_HOST": "Vitess database host",
        "VITESS_PORT": "Vitess database port",
        "VITESS_DATABASE": "Vitess database name",
        "VITESS_USER": "Vitess database user",
    }

    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == "":
            missing_vars.append(f"  {var}: {description}")

    if missing_vars:
        error_msg = (
            "Required environment variables are not set:\n"
            + "\n".join(missing_vars)
            + "\n\nPlease set these environment variables before running E2E tests."
        )
        pytest.fail(error_msg)


@pytest.fixture(scope="session")
def db_conn():
    """Database connection for cleanup."""
    from models.config.settings import settings

    conn = pymysql.connect(
        host=settings.vitess_host,
        port=settings.vitess_port,
        user=settings.vitess_user,
        password=settings.vitess_password,
        database=settings.vitess_database,
        connect_timeout=2,
    )
    yield conn
    if conn:
        conn.close()


@pytest.fixture(autouse=True)
def db_cleanup(db_conn):
    """Clean up database tables after each E2E test."""
    yield
    tables = [
        "entity_id_mapping",
        "entity_revisions",
        "entity_head",
        "metadata_content",
        "entity_backlinks",
        "backlink_statistics",
        "statement_content",
        "entity_terms",
        "user_activity",
        "user_notifications",
        "user_thanks",
        "user_statement_endorsements",
        "watchlist",
        "entity_redirects",
        "users",
        "user_daily_stats",
        "general_daily_stats",
    ]
    with db_conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table}")
            except pymysql.err.ProgrammingError as e:
                if "doesn't exist" in str(e):
                    continue
                else:
                    raise
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db_conn.commit()


@pytest.fixture(scope="session", autouse=True)
def create_tables(vitess_client):
    """Create database tables before running E2E tests."""
    from models.infrastructure.vitess.repositories.schema import SchemaRepository

    schema_repository = SchemaRepository(vitess_client=vitess_client)
    schema_repository.create_tables()
    logger.info("Database tables created for E2E tests")


@pytest.fixture(scope="session")
def vitess_client():
    """Create a real VitessClient connected to test database."""
    from models.infrastructure.vitess.client import VitessClient
    from models.data.config.vitess import VitessConfig
    from models.config.settings import settings

    vitess_config = VitessConfig(
        host=settings.vitess_host,
        port=settings.vitess_port,
        database=settings.vitess_database,
        user=settings.vitess_user,
        password=settings.vitess_password,
        pool_size=20,
        max_overflow=20,
        pool_timeout=5,
    )
    client = VitessClient(config=vitess_config)
    yield client
    client.disconnect()


@pytest.fixture(scope="session")
def s3_config():
    """Create real S3Config from settings."""
    from models.config.settings import settings

    return settings.get_s3_config


@pytest.fixture(scope="session", autouse=True)
def create_s3_buckets(s3_config):
    """Create S3 buckets before running E2E tests."""
    import boto3
    from botocore.exceptions import ClientError
    from models.config.settings import settings

    required_buckets = [
        settings.s3_terms_bucket,
        settings.s3_statements_bucket,
        settings.s3_references_bucket,
        settings.s3_qualifiers_bucket,
        settings.s3_revisions_bucket,
        settings.s3_sitelinks_bucket,
        settings.s3_snaks_bucket,
    ]

    s3 = boto3.client(
        "s3",
        endpoint_url=s3_config.endpoint_url,
        aws_access_key_id=s3_config.access_key,
        aws_secret_access_key=s3_config.secret_key,
    )

    created_count = 0
    for bucket in required_buckets:
        try:
            s3.head_bucket(Bucket=bucket)
            logger.debug(f"Bucket already exists: {bucket}")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchBucket"}:
                try:
                    s3.create_bucket(Bucket=bucket)
                    logger.debug(f"Created bucket: {bucket}")
                    created_count += 1
                except Exception as create_error:
                    logger.error(f"Failed to create bucket {bucket}: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket {bucket}: {error_code}")
                raise

    print(
        f"S3 buckets ready: {len(required_buckets)} buckets ({created_count} created)"
    )


@pytest.fixture(scope="session")
def s3_client(s3_config, vitess_client):
    """Create real MyS3Client connected to S3."""
    from models.infrastructure.s3.client import MyS3Client

    client = MyS3Client(config=s3_config, vitess_client=vitess_client)
    yield client
    client.disconnect()
    logger.debug("S3Client disconnected in s3_client fixture")


@pytest.fixture(scope="session", autouse=True)
def initialized_app(vitess_client, s3_client, create_s3_buckets):
    """Initialize the FastAPI app with state_handler for E2E tests."""
    from models.rest_api.main import app
    from models.rest_api.entitybase.v1.handlers.state import StateHandler
    from models.config.settings import settings

    logger.debug("Creating StateHandler...")
    state_handler = StateHandler(settings=settings)

    # Inject pre-configured test clients instead of creating new ones
    state_handler.cached_vitess_client = vitess_client
    state_handler.cached_s3_client = s3_client
    logger.debug("Injected test Vitess and S3 clients into StateHandler")

    logger.debug("StateHandler created, calling start()...")
    state_handler.start()
    logger.debug("StateHandler started")

    app.state.state_handler = state_handler
    logger.debug(
        f"app.state.state_handler set: {type(app.state.state_handler).__name__}"
    )

    yield

    logger.debug("Disconnecting StateHandler...")
    if state_handler:
        state_handler.disconnect()
        logger.debug("StateHandler disconnected in initialized_app fixture")


@pytest.fixture
def sample_item_data() -> dict[str, Any]:
    """Sample item entity data for testing - simple item without fixed ID."""
    return {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Item"}},
        "descriptions": {
            "en": {"language": "en", "value": "A test item for E2E testing"}
        },
    }


@pytest.fixture
def sample_item_with_statements() -> dict[str, Any]:
    """Sample item with statements for testing."""
    return {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Item with Statements"}},
        "descriptions": {
            "en": {"language": "en", "value": "Test item with statements"}
        },
        "statements": [
            {
                "id": "TESTCLAIM123",
                "mainsnak": {
                    "snaktype": "value",
                    "property": "P31",
                    "datavalue": {"value": {"id": "Q5"}, "type": "wikibase-item"},
                },
                "type": "statement",
                "rank": "normal",
            }
        ],
    }


@pytest.fixture
def sample_property_data() -> dict[str, Any]:
    """Sample property entity data for testing."""
    return {
        "type": "property",
        "datatype": "wikibase-item",
        "labels": {"en": {"language": "en", "value": "Test Property"}},
        "descriptions": {
            "en": {"language": "en", "value": "A test property for E2E testing"}
        },
    }


@pytest.fixture
def sample_lexeme_data() -> dict[str, Any]:
    """Sample lexeme entity data for testing."""
    return {
        "type": "lexeme",
        "language": "Q1860",
        "lexicalCategory": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "labels": {"en": {"language": "en", "value": "test lexeme"}},
        "forms": [
            {
                "id": "L1-F1",
                "representations": {"en": {"language": "en", "value": "tests"}},
                "grammaticalFeatures": ["Q110786"],
            }
        ],
        "senses": [
            {
                "id": "L1-S1",
                "glosses": {"en": {"language": "en", "value": "A test sense"}},
            }
        ],
    }


@pytest.fixture
def test_user_ids() -> list[int]:
    """Test user IDs for testing."""
    return [90001, 90002, 90003]


@pytest.fixture
def sample_sitelink() -> dict[str, Any]:
    """Sample sitelink data for testing."""
    return {"site": "enwiki", "title": "Test Article", "badges": []}


@pytest.fixture
def sample_edit_headers() -> dict[str, str]:
    """Sample edit headers for testing."""
    return {"X-Edit-Summary": "E2E test", "X-User-ID": "0"}
