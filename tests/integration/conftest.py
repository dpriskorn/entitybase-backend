import logging
import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

import pytest
import requests
from minio.error import S3Error

sys.path.insert(0, "src")

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# In CI, always disable streaming regardless of what test.env loaded
if os.getenv("CI"):
    os.environ["STREAMING_ENABLED"] = "false"

if "STREAMING_ENABLED" not in os.environ:
    # Default to disabled - only enable if Kafka is available and not in CI
    streaming_enabled = "false"
    kafka_host = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
    # Only enable streaming if Kafka is configured and not in CI
    if kafka_host and not os.getenv("CI"):
        streaming_enabled = "true"
    os.environ["STREAMING_ENABLED"] = streaming_enabled

# Only set default Kafka host if NOT in CI (CI doesn't have Kafka)
if "KAFKA_BOOTSTRAP_SERVERS" not in os.environ and not os.getenv("CI"):
    os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "redpanda:9092"
if "KAFKA_ENTITYCHANGE_JSON_TOPIC" not in os.environ:
    os.environ["KAFKA_ENTITYCHANGE_JSON_TOPIC"] = "entitybase.entity_change"

# noinspection PyPep8
from models.config.settings import settings

minio_loggers = [
    "urllib3",
]

for logger_name in minio_loggers:
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
        "S3_ENDPOINT": "S3 storage endpoint URL",
        "S3_ACCESS_KEY": "S3 access key",
        "S3_SECRET_KEY": "S3 secret key",
    }

    if DB_TYPE == "mysql":
        required_vars["MYSQL_HOST"] = "Sql database host"
        required_vars["MYSQL_PORT"] = "Sql database port"
        required_vars["MYSQL_DATABASE"] = "Sql database name"
        required_vars["MYSQL_USER"] = "Sql database user"

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

    if DB_TYPE == "sqlite":
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_integration.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        logger.debug(
            f"=== db_conn fixture SUCCESS (SQLite) in {(time_module.time() - start_time):.2f}s ==="
        )
        yield conn
        if conn:
            conn.close()
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        logger.debug(
            f"Attempting to connect to: host='{settings.mysql_host}', port={settings.mysql_port}, user='{settings.mysql_user}', database='{settings.mysql_database}'"
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
                    host=settings.mysql_host,
                    port=settings.mysql_port,
                    user=settings.mysql_user,
                    password=settings.mysql_password,
                    database=settings.mysql_database,
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
def create_tables(db_client):
    """Create database tables before running integration tests."""
    import time as time_module

    start_time = time_module.time()
    logger.debug("=== create_tables fixture START ===")
    db_client.create_tables()
    logger.debug(
        f"=== create_tables fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )
    print(f"Database tables created for integration tests (DB_TYPE={DB_TYPE})")


@pytest.fixture(scope="session")
def db_client():
    """Create a database client (SqliteClient or MysqlClient) connected to test database."""
    import time as time_module

    start_time = time_module.time()
    logger.debug("=== db_client fixture START ===")

    if DB_TYPE == "sqlite":
        from models.infrastructure.sqlite.client import SqliteClient

        sqlite_config = settings.get_db_config
        logger.debug(
            f"pytest:db_client: SQLite datadir='{sqlite_config.datadir}'"
        )
        client = SqliteClient(config=sqlite_config)
        logger.debug(
            f"=== db_client fixture SUCCESS (SQLite) in {(time_module.time() - start_time):.2f}s ==="
        )
        yield client
        client.disconnect()
    else:
        logger.debug(f"pytest:db_client: Running")
        from models.infrastructure.mysql.client import MysqlClient
        from models.data.config.mysql import MysqlConfig

        # Create a test-specific config with smaller pool for faster tests
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
        logger.debug(
            f"Sql config: host='{mysql_config.host}', port={mysql_config.port}, database='{mysql_config.database}'"
        )

        client_start = time_module.time()
        client = MysqlClient(config=mysql_config)
        logger.debug(f"MysqlClient created in {(time_module.time() - client_start):.2f}s")

        logger.debug(
            f"=== db_client fixture END total time: {(time_module.time() - start_time):.2f}s ==="
        )
        yield client

        client.disconnect()


@pytest.fixture(scope="session")
def mysql_client():
    """Create a real MysqlClient connected to test database (for backwards compatibility)."""
    if DB_TYPE != "mysql":
        pytest.skip("mysql_client fixture requires DB_TYPE=mysql")
    import time as time_module

    start_time = time_module.time()
    logger.debug("=== mysql_client fixture START ===")
    logger.debug(f"pytest:mysql_client: Running")
    from models.infrastructure.mysql.client import MysqlClient
    from models.data.config.mysql import MysqlConfig

    # Create a test-specific config with smaller pool for faster tests
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
    logger.debug(
        f"Sql config: host='{mysql_config.host}', port={mysql_config.port}, database='{mysql_config.database}'"
    )

    client_start = time_module.time()
    client = MysqlClient(config=mysql_config)
    logger.debug(f"MysqlClient created in {(time_module.time() - client_start):.2f}s")

    logger.debug(
        f"=== mysql_client fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )
    yield client

    client.disconnect()


@pytest.fixture(scope="function")
def connection_manager():
    """Create a SqlConnectionManager for testing connection pool behavior."""
    from models.infrastructure.mysql.connection import SqlConnectionManager
    from models.data.config.mysql import MysqlConfig

    # Use settings config but with smaller timeouts for faster tests
    test_config = MysqlConfig(
        host=settings.mysql_host,
        port=settings.mysql_port,
        database=settings.mysql_database,
        user=settings.mysql_user,
        password=settings.mysql_password,
        pool_size=20,
        max_overflow=20,
        pool_timeout=5,
    )
    manager = SqlConnectionManager(config=test_config)
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
    from minio import Minio

    start_time = time_module.time()
    logger.debug("=== create_s3_buckets fixture START ===")

    from models.config.settings import settings

    required_buckets = [
        settings.s3_revisions_bucket,
    ]

    s3 = Minio(
        s3_config.endpoint_url,
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

    logger.debug(
        f"=== create_s3_buckets fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )
    print(
        f"S3 buckets ready: {len(required_buckets)} buckets ({created_count} created)"
    )


@pytest.fixture(scope="session")
def s3_client(s3_config, db_client):
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
            client = MyS3Client(config=s3_config, mysql_client=db_client)
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
async def initialized_app(db_client, s3_client, create_s3_buckets):
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
    state_handler.cached_mysql_client = db_client
    logger.debug("StateHandler created, calling start()...")
    state_handler.start()
    logger.debug("StateHandler started")

    app.state.state_handler = state_handler
    logger.debug(
        f"app.state.state_handler set: {type(app.state.state_handler).__name__}"
    )
    logger.debug(
        f"initialized_app fixture ready in {(time_module.time() - start_time):.2f}s"
    )

    yield

    logger.debug("Disconnecting StateHandler...")
    if state_handler:
        await state_handler.async_shutdown()
        state_handler.disconnect()
        logger.debug("StateHandler disconnected in initialized_app fixture")
    logger.debug(
        f"=== initialized_app fixture END total time: {(time_module.time() - start_time):.2f}s ==="
    )
