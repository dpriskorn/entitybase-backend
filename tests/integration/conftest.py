import pytest
import pymysql


@pytest.fixture(scope="session")
def db_conn():
    """Database connection for cleanup"""
    conn = pymysql.connect(
        host="vitess",
        port=15309,
        user="root",
        password="",
        database="page"
    )
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
        "backlink_statistics"
    ]
    with db_conn.cursor() as cursor:
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
    db_conn.commit()