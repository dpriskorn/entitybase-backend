import time

import pymysql
import pytest
import requests

from models.config.settings import settings


@pytest.fixture(scope="session")
def db_conn():
    """Database connection for cleanup"""
    # Wait for DB to be ready
    max_retries = 30
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
    # Truncate relevant tables after each test
    tables = [
        "entity_revisions",
        "entity_head",
        "metadata_content",
        "entity_backlinks",
        "backlink_statistics",
    ]
    with db_conn.cursor() as cursor:
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
    db_conn.commit()


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
