import json
import logging
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest
import requests

sys.path.insert(0, "src")

os.environ["STREAMING_ENABLED"] = "false"
os.environ.pop("KAFKA_BOOTSTRAP_SERVERS", None)

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

logger = logging.getLogger(__name__)


def get_entity_id_from_response(response: Any) -> str:
    """Extract entity_id from create item response with debug logging."""
    if response.status_code != 200:
        logger.error(
            f"Failed to create entity: {response.status_code} - {response.text}"
        )
        raise AssertionError(
            f"Expected 200, got {response.status_code}: {response.text}"
        )
    json_data = response.json()
    if "data" not in json_data:
        logger.error(f"Response missing 'data' field: {json_data}")
        raise AssertionError(f"Response missing 'data' field: {json_data}")
    if "entity_id" not in json_data["data"]:
        logger.error(f"Response data missing 'entity_id': {json_data['data']}")
        raise AssertionError(f"Response data missing 'entity_id': {json_data['data']}")
    return json_data["data"]["entity_id"]


@pytest.fixture(scope="session", autouse=True)
def validate_e2e_env_vars():
    """Validate required environment variables are set before running E2E tests.

    This fixture fails fast if required environment variables are missing,
    preventing long retry loops and confusing connection errors.
    """
    if DB_TYPE == "mysql":
        required_vars = {
            "MYSQL_HOST": "Sql database host",
            "MYSQL_PORT": "Sql database port",
            "MYSQL_DATABASE": "Sql database name",
            "MYSQL_USER": "Sql database user",
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
    if DB_TYPE == "sqlite":
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_e2e.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        yield conn
        if conn:
            conn.close()
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        import pymysql
        from models.config.settings import settings

        conn = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            connect_timeout=2,
        )
        yield conn
        if conn:
            conn.close()


@pytest.fixture(scope="class")
def db_cleanup(db_conn):
    """Clean up database tables after each test class (faster than per-test)."""
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
    if DB_TYPE == "sqlite":
        for table in tables:
            try:
                db_conn.execute(f"DELETE FROM {table}")
            except sqlite3.OperationalError:
                continue
        db_conn.commit()
    else:
        import pymysql
        with db_conn.cursor() as cursor:
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except pymysql.err.ProgrammingError:
                    continue
        db_conn.commit()


@pytest.fixture(scope="session", autouse=True)
def create_tables(db_client):
    """Create database tables before running E2E tests."""
    db_client.create_tables()
    logger.info(f"Database tables created for E2E tests (DB_TYPE={DB_TYPE})")


@pytest.fixture(scope="session")
def db_client():
    """Create a database client (SqliteClient or MysqlClient) connected to test database."""
    from models.config.settings import settings

    if DB_TYPE == "sqlite":
        from models.infrastructure.sqlite.client import SqliteClient

        sqlite_config = settings.get_db_config
        client = SqliteClient(config=sqlite_config)
        yield client
        client.disconnect()
    else:
        from models.infrastructure.mysql.client import MysqlClient
        from models.data.config.mysql import MysqlConfig

        mysql_config = MysqlConfig(
            host=settings.mysql_host,
            port=settings.mysql_port,
            database=settings.mysql_database,
            user=settings.mysql_user,
            password=settings.mysql_password,
            pool_size=20,
            max_overflow=20,
            pool_timeout=5,
        )
        client = MysqlClient(config=mysql_config)
        yield client
        client.disconnect()


@pytest.fixture(scope="session")
def mysql_client():
    """Create a real MysqlClient connected to test database (for backwards compatibility)."""
    if DB_TYPE != "mysql":
        pytest.skip("mysql_client fixture requires DB_TYPE=mysql")
    from models.infrastructure.mysql.client import MysqlClient
    from models.data.config.mysql import MysqlConfig
    from models.config.settings import settings

    mysql_config = MysqlConfig(
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.mysql_database,
        user=settings.mysql_user,
        password=settings.mysql_password,
        pool_size=20,
        max_overflow=20,
        pool_timeout=5,
    )
    client = MysqlClient(config=mysql_config)
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
    from minio import Minio
    from minio.error import S3Error
    from models.config.settings import settings

    required_buckets = [
        settings.s3_revisions_bucket,
    ]

    endpoint = s3_config.endpoint_url
    if endpoint.startswith("http://"):
        endpoint = endpoint[7:]
    elif endpoint.startswith("https://"):
        endpoint = endpoint[8:]

    s3 = Minio(
        endpoint,
        access_key=s3_config.access_key,
        secret_key=s3_config.secret_key,
        secure=False,
    )

    created_count = 0
    for bucket in required_buckets:
        try:
            if s3.bucket_exists(bucket):
                logger.debug(f"Bucket already exists: {bucket}")
            else:
                s3.make_bucket(bucket)
                logger.debug(f"Created bucket: {bucket}")
                created_count += 1
        except S3Error as e:
            logger.error(f"Error creating bucket {bucket}: {e}")
            raise

    print(
        f"S3 buckets ready: {len(required_buckets)} buckets ({created_count} created)"
    )


@pytest.fixture(scope="session")
def s3_client(s3_config, db_client):
    """Create real MyS3Client connected to S3."""
    from models.infrastructure.s3.client import MyS3Client

    client = MyS3Client(config=s3_config, mysql_client=db_client)
    yield client
    client.disconnect()
    logger.debug("S3Client disconnected in s3_client fixture")


@pytest.fixture(scope="session", autouse=True)
def initialized_app(db_client, s3_client, create_s3_buckets):
    """Initialize the FastAPI app with state_handler for E2E tests."""
    from models.rest_api.main import app
    from models.rest_api.entitybase.v1.handlers.state import StateHandler
    from models.config.settings import settings

    logger.debug("Creating StateHandler...")
    state_handler = StateHandler(settings=settings)

    # Inject pre-configured test clients instead of creating new ones
    state_handler.cached_mysql_client = db_client
    state_handler.cached_s3_client = s3_client
    logger.debug("Injected test Sql and S3 clients into StateHandler")

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


@pytest.fixture(scope="session", autouse=True)
def mock_auth(initialized_app):
    """Override auth dependency to use test user for all E2E tests.

    This allows E2E tests to run without real JWT token authentication.
    All authenticated endpoints will use a test user (user_id=0, role=default).
    """
    from models.rest_api.main import app
    from models.rest_api.auth.dependencies import verify_auth
    from models.rest_api.auth.models import AuthenticatedRequest, User
    from models.data.common.roles import UserRole

    test_user = User(user_id=0, username="test", role=UserRole.DEFAULT)
    test_auth_request = AuthenticatedRequest(
        user=test_user, edit_summary="E2E test", base_revision_id=0
    )

    async def override_verify_auth():
        return test_auth_request

    app.dependency_overrides[verify_auth] = override_verify_auth
    logger.debug("Auth dependency overridden with test user for E2E tests")

    yield

    app.dependency_overrides.clear()
    logger.debug("Auth dependency override cleared")


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
def sample_item_with_entity_reference() -> dict[str, Any]:
    """Sample item with statement referencing another entity for backlink testing."""
    return {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Referencing Item"}},
        "descriptions": {
            "en": {"language": "en", "value": "Item that references another entity"}
        },
        "statements": [
            {
                "id": "TESTREF123",
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
