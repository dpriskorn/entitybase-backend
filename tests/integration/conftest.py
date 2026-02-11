import logging
import sys
import time

import boto3
import pymysql
import pytest
import requests
from botocore.exceptions import ClientError

sys.path.insert(0, "src")
# noinspection PyPep8
from models.config.settings import settings

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


@pytest.fixture(scope="session", autouse=True)
def validate_env_vars():
    """Validate required environment variables are set before running integration tests.

    This fixture fails fast if required environment variables are missing,
    preventing long retry loops in connection fixtures.
    """
    import os

    required_vars = {
        "VITESS_HOST": "Vitess database host",
        "VITESS_PORT": "Vitess database port",
        "VITESS_DATABASE": "Vitess database name",
        "VITESS_USER": "Vitess database user",
        "S3_ENDPOINT": "S3 storage endpoint URL",
        "S3_ACCESS_KEY": "S3 access key",
        "S3_SECRET_KEY": "S3 secret key",
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
            + "\n\nPlease set these environment variables before running integration tests."
        )
        logger.error(error_msg)
        pytest.fail(error_msg)

    logger.debug("All required environment variables are validated")


# @pytest.fixture(autouse=True)
# def configure_aws_logging():
#     """Configure AWS loggers to WARNING level for integration tests."""
#     for logger_name in AWS_LOGGERS:
#         logging.getLogger(logger_name).setLevel(logging.WARNING)
#     yield


@pytest.fixture(scope="session")
def db_conn():
    """Database connection for cleanup"""
    import time as time_module

    start_time = time_module.time()
    logger.debug("=== db_conn fixture START ===")
    logger.debug(
        f"Attempting to connect to: host='{settings.vitess_host}', port={settings.vitess_port}, user='{settings.vitess_user}', database='{settings.vitess_database}'"
    )

    # Wait for DB to be ready - optimized retry logic
    max_retries = 5
    conn = None
    for attempt in range(max_retries):
        attempt_start = time_module.time()
        try:
            logger.debug(
                f"Attempt {attempt + 1}/{max_retries}: Connecting to database..."
            )
            conn = pymysql.connect(
                host=settings.vitess_host,
                port=settings.vitess_port,
                user=settings.vitess_user,
                password=settings.vitess_password,
                database=settings.vitess_database,
                connect_timeout=2,
            )
            logger.debug(
                f"Attempt {attempt + 1}/{max_retries}: Connection established in {(time_module.time() - attempt_start):.2f}s"
            )

            # Test connection with a simple query
            with conn.cursor() as cursor:
                query_start = time_module.time()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                logger.debug(
                    f"Attempt {attempt + 1}/{max_retries}: Query executed in {(time_module.time() - query_start):.2f}s"
                )

            logger.debug(
                f"=== db_conn fixture SUCCESS in {(time_module.time() - start_time):.2f}s ==="
            )
            break
        except pymysql.Error as e:
            attempt_time = time_module.time() - attempt_start
            logger.debug(
                f"Attempt {attempt + 1}/{max_retries} FAILED after {attempt_time:.2f}s: {e}"
            )
            if attempt == max_retries - 1:
                logger.error(
                    f"=== db_conn fixture FAILED after {(time_module.time() - start_time):.2f}s ==="
                )
                raise e
            logger.debug(f"Waiting 1s before retry...")
            time.sleep(1)

    yield conn
    if conn:
        conn.close()
    logger.debug(
        f"=== db_conn fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )


@pytest.fixture(autouse=True)
def db_cleanup(db_conn):
    yield
    # Truncate relevant tables after each test (only if they exist)
    # Note: id_ranges is NOT truncated because it's required for ID generation across test runs
    # user_daily_stats, general_daily_stats are historical stats that shouldn't be reset
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
    ]
    with db_conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table}")
            except pymysql.err.ProgrammingError as e:
                if "doesn't exist" in str(e):
                    # Table doesn't exist, skip
                    continue
                else:
                    raise
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    db_conn.commit()


@pytest.fixture(scope="session", autouse=True)
def create_tables(vitess_client):
    """Create database tables before running integration tests."""
    import time as time_module

    start_time = time_module.time()
    logger.debug("=== create_tables fixture START ===")
    try:
        from models.infrastructure.vitess.repositories.schema import SchemaRepository

        schema_start = time_module.time()
        schema_repository = SchemaRepository(vitess_client=vitess_client)
        schema_repository.create_tables()
        logger.debug(
            f"Schema tables created in {(time_module.time() - schema_start):.2f}s"
        )

        print("Database tables created for integration tests")
    except Exception as e:
        logger.debug(f"Failed to create tables: {e}")
        # Try to create tables using raw SQL as fallback using db_conn
        try:
            import pymysql
            from models.config.settings import settings
            import time as time_module

            fallback_start = time_module.time()
            conn = pymysql.connect(
                host=settings.vitess_host,
                port=settings.vitess_port,
                user=settings.vitess_user,
                password=settings.vitess_password,
                database=settings.vitess_database,
                connect_timeout=2,
            )
            with conn.cursor() as cursor:
                # Create minimal tables needed for tests
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entity_id_mapping (
                        entity_id VARCHAR(50) PRIMARY KEY,
                        internal_id BIGINT UNSIGNED NOT NULL UNIQUE
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entity_revisions (
                        internal_id BIGINT UNSIGNED NOT NULL,
                        revision_id BIGINT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        is_mass_edit BOOLEAN DEFAULT FALSE,
                        edit_type VARCHAR(100) DEFAULT '',
                        statements JSON NOT NULL,
                        properties JSON NOT NULL,
                        property_counts JSON NOT NULL,
                        labels_hashes JSON,
                        descriptions_hashes JSON,
                        aliases_hashes JSON,
                        sitelinks_hashes JSON,
                        user_id BIGINT UNSIGNED,
                        edit_summary TEXT,
                        content_hash BIGINT UNSIGNED NOT NULL,
                        PRIMARY KEY (internal_id, revision_id)
                    )
                """)
                # Add other essential tables as needed
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entity_head (
                        internal_id BIGINT UNSIGNED PRIMARY KEY,
                        head_revision_id BIGINT NOT NULL,
                        is_semi_protected BOOLEAN DEFAULT FALSE,
                        is_locked BOOLEAN DEFAULT FALSE,
                        is_archived BOOLEAN DEFAULT FALSE,
                        is_dangling BOOLEAN DEFAULT FALSE,
                        is_mass_edit_protected BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        is_redirect BOOLEAN DEFAULT FALSE,
                        redirects_to BIGINT UNSIGNED NULL
                    )
                """)
            conn.commit()
            conn.close()
            logger.debug(
                f"Fallback SQL tables created in {(time_module.time() - fallback_start):.2f}s"
            )
            print("Created minimal tables using raw SQL")
        except Exception as sql_e:
            logger.debug(f"Failed to create tables with SQL: {sql_e}")
            raise

    logger.debug(
        f"=== create_tables fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )


@pytest.fixture(scope="session")
def vitess_client():
    """Create a real VitessClient connected to test database."""
    import time as time_module

    start_time = time_module.time()
    logger.debug("=== vitess_client fixture START ===")
    logger.debug(f"pytest:vitess_client: Running")
    from models.infrastructure.vitess.client import VitessClient
    from models.data.config.vitess import VitessConfig

    # Create a test-specific config with smaller pool for faster tests
    vitess_config = VitessConfig(
        host=settings.vitess_host,
        port=settings.vitess_port,
        database=settings.vitess_database,
        user=settings.vitess_user,
        password=settings.vitess_password,
        pool_size=5,
        max_overflow=5,
        pool_timeout=2,
    )
    logger.debug(
        f"Vitess config: host='{vitess_config.host}', port={vitess_config.port}, database='{vitess_config.database}'"
    )

    client_start = time_module.time()
    client = VitessClient(config=vitess_config)
    logger.debug(f"VitessClient created in {(time_module.time() - client_start):.2f}s")

    logger.debug(
        f"=== vitess_client fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )
    yield client

    client.disconnect()


@pytest.fixture(scope="function")
def connection_manager():
    """Create a VitessConnectionManager for testing connection pool behavior."""
    from models.infrastructure.vitess.connection import VitessConnectionManager
    from models.data.config.vitess import VitessConfig

    # Use settings config but with smaller timeouts for faster tests
    test_config = VitessConfig(
        host=settings.vitess_host,
        port=settings.vitess_port,
        database=settings.vitess_database,
        user=settings.vitess_user,
        password=settings.vitess_password,
        pool_size=2,
        max_overflow=1,
        pool_timeout=1,
    )
    manager = VitessConnectionManager(config=test_config)
    yield manager
    manager.disconnect()


@pytest.fixture(scope="session")
def s3_config():
    """Create real S3Config from settings."""
    from models.config.settings import settings

    return settings.get_s3_config


@pytest.fixture(scope="session", autouse=True)
def create_s3_buckets(s3_config):
    """Create S3 buckets before running integration tests.

    This fixture ensures all required S3 buckets exist before tests run,
    preventing NoSuchBucket errors when storing data.
    """
    import time as time_module

    start_time = time_module.time()
    logger.debug("=== create_s3_buckets fixture START ===")

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

    logger.debug(
        f"=== create_s3_buckets fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )
    print(f"S3 buckets ready: {len(required_buckets)} buckets ({created_count} created)")


@pytest.fixture(scope="session")
def s3_client(s3_config):
    """Create real MyS3Client connected to Minio."""
    import time as time_module
    from models.infrastructure.s3.client import MyS3Client

    start_time = time_module.time()
    logger.debug("=== s3_client fixture START ===")
    logger.debug(f"pytest:s3_client: Running, S3 endpoint: {s3_config.endpoint_url}")

    max_retries = 5
    for attempt in range(max_retries):
        attempt_start = time_module.time()
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries}: Connecting to S3...")
            client = MyS3Client(config=s3_config)
            logger.debug(
                f"pytest:s3_client: Connected to S3 at attempt {attempt + 1} in {(time_module.time() - attempt_start):.2f}s"
            )
            logger.debug(
                f"=== s3_client fixture SUCCESS in {(time_module.time() - start_time):.2f}s ==="
            )
            yield client
            return
        except Exception as e:
            attempt_time = time_module.time() - attempt_start
            logger.debug(
                f"Attempt {attempt + 1}/{max_retries} FAILED after {attempt_time:.2f}s: {e}"
            )
            if attempt == max_retries - 1:
                logger.error(
                    f"=== s3_client fixture FAILED after {(time_module.time() - start_time):.2f}s ==="
                )
                raise
            logger.debug(f"Waiting 1s before retry...")
            time_module.sleep(1)


@pytest.fixture(scope="session", autouse=True)
def initialized_app(vitess_client, s3_client, create_s3_buckets):
    """Initialize the FastAPI app with state_handler for integration tests.

    This fixture ensures that app.state.state_handler is properly initialized
    before tests run, preventing 503 errors from StartupMiddleware.

    Session-scoped to avoid redundant health checks for each test.
    """
    import time as time_module
    start_time = time_module.time()
    logger.info("=== initialized_app fixture START ===")
    from models.rest_api.main import app
    from models.rest_api.entitybase.v1.handlers.state import StateHandler

    logger.debug("Creating StateHandler...")
    state_handler = StateHandler(settings=settings)
    logger.debug("StateHandler created, calling start()...")
    state_handler.start()
    logger.debug("StateHandler started")

    app.state.state_handler = state_handler
    logger.debug(f"app.state.state_handler set: {type(app.state.state_handler).__name__}")
    logger.debug(f"initialized_app fixture ready in {(time_module.time() - start_time):.2f}s")

    yield

    logger.debug("Disconnecting StateHandler...")
    if state_handler:
        state_handler.disconnect()
        logger.debug("StateHandler disconnected in initialized_app fixture")
    logger.debug(
        f"=== initialized_app fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )
