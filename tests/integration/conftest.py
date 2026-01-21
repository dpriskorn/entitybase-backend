import sys
import time

import pymysql
import pytest
import requests

sys.path.insert(0, "src")
# noinspection PyPep8
from models.config.settings import settings


@pytest.fixture(scope="session")
def db_conn():
    """Database connection for cleanup"""
    # Wait for DB to be ready
    max_retries = 30
    conn = None
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(
                host=settings.vitess_host,
                port=settings.vitess_port,
                user=settings.vitess_user,
                password=settings.vitess_password,
                database=settings.vitess_database,
            )
            # Test connection with a simple query
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            break
        except pymysql.Error as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def db_cleanup(db_conn):
    yield
    # Truncate relevant tables after each test (only if they exist)
    tables = [
        "entity_revisions",
        "entity_head",
        "metadata_content",
        "entity_backlinks",
        "backlink_statistics",
    ]
    with db_conn.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table}")
            except pymysql.err.ProgrammingError as e:
                if "doesn't exist" in str(e):
                    # Table doesn't exist, skip
                    continue
                else:
                    raise
    db_conn.commit()


@pytest.fixture(scope="session", autouse=True)
def create_tables(db_conn):
    """Create database tables before running integration tests."""
    try:
        from models.infrastructure.vitess.repositories.schema import SchemaRepository
        from models.infrastructure.vitess.client import VitessClient
        from models.config.settings import settings

        # Create Vitess config and schema repository
        vitess_config = settings.to_vitess_config()
        vitess_client = VitessClient(config=vitess_config)
        schema_repository = SchemaRepository(vitess_client=vitess_client)
        schema_repository.create_tables()
        print("Database tables created for integration tests")
    except Exception as e:
        print(f"Failed to create tables: {e}")
        # Try to create tables using raw SQL as fallback
        try:
            with db_conn.cursor() as cursor:
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
            db_conn.commit()
            print("Created minimal tables using raw SQL")
        except Exception as sql_e:
            print(f"Failed to create tables with SQL: {sql_e}")
            raise


@pytest.fixture(scope="session")
def api_client():
    """API client for E2E tests - connects to running application."""
    # base_url = "http://api:8000"  # Adjust for Docker container URL

    # # Wait for API to be ready
    # @retry(
    #     stop=stop_after_attempt(30), wait=wait_exponential(multiplier=1, min=1, max=10)
    # )
    # def wait_for_api():
    #     try:
    #         response = requests.get(f"{base_url}/health", timeout=5)
    #         response.raise_for_status()
    #         assert response.json().get("status") == "ok"
    #     except requests.RequestException:
    #         raise Exception("E2E API not ready")

    # wait_for_api()
    return requests.Session()


@pytest.fixture(scope="session")
def base_url():
    """Base URL for E2E API."""
    return "http://api:8000"
