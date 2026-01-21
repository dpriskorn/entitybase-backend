#!/usr/bin/env python3
"""Script to create database tables for testing."""

import sys
from pathlib import Path

# Add src to path (we're already in src/models/workers/dev/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def create_tables():
    """Create database tables."""
    try:
        from models.infrastructure.vitess.repositories.schema import SchemaRepository
        from models.config.settings import settings

        print("Creating database tables...")
        vitess_config = settings.to_vitess_config()
        schema_repository = SchemaRepository(config=vitess_config)
        schema_repository.create_tables()
        print("Database tables created successfully")

    except Exception as e:
        print(f"Failed to create tables: {e}")
        # Try fallback with raw SQL
        try:
            import pymysql
            from models.config.settings import settings

            config = settings.to_vitess_config()
            conn = pymysql.connect(
                host=config.host,
                port=config.port,
                user=config.user,
                password=config.password,
                database=config.database,
            )

            with conn.cursor() as cursor:
                # Create essential tables
                tables_sql = [
                    """
                    CREATE TABLE IF NOT EXISTS entity_id_mapping (
                        entity_id VARCHAR(50) PRIMARY KEY,
                        internal_id BIGINT UNSIGNED NOT NULL UNIQUE
                    )
                    """,
                    """
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
                    """,
                    """
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
                    """
                ]

                for sql in tables_sql:
                    cursor.execute(sql)

            conn.commit()
            conn.close()
            print("Created tables using raw SQL fallback")

        except Exception as sql_e:
            print(f"Raw SQL creation also failed: {sql_e}")
            raise

if __name__ == "__main__":
    create_tables()