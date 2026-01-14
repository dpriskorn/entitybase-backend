"""Drop all tables worker for test database reset."""

import os
import pymysql
import logging

logger = logging.getLogger(__name__)


def drop_all_tables() -> None:
    """Drop all Wikibase tables to reset the database for tests."""
    host = os.getenv("VITESS_HOST", "localhost")
    port = int(os.getenv("VITESS_PORT", "15309"))
    database = os.getenv("VITESS_DATABASE", "page")
    user = os.getenv("VITESS_USER", "root")
    password = os.getenv("VITESS_PASSWORD", "")

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        cursor = conn.cursor()

        tables = [
            "id_ranges",
            "entity_id_mapping",
            "entity_revisions",
            "entity_head",
            "entity_backlinks",
        ]

        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            logger.info(f"Dropped table {table}")

        conn.commit()
        logger.info("All tables dropped successfully")

    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    drop_all_tables()
