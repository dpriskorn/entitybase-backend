#!/usr/bin/env python3
"""Development worker for database table creation and management."""

import logging
import os
import sys
from typing import Any, Dict, List

import pymysql
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, src_path)

# noinspection PyPep8
from models.config.settings import settings


class CreateTables(BaseModel):
    """Development worker for database table creation and management."""

    # Essential tables required for the application
    required_tables: List[str] = [
        "entity_id_mapping",
        "entity_revisions",
        "entity_head",
        "entity_redirects",
        "statement_content",
        "entity_backlinks",
        "backlink_statistics",
        "metadata_content",
        "user_daily_stats",
        "general_daily_stats",
        "users",
        "watchlist",
        "user_notifications",
        "user_activity",
        "user_thanks",
        "user_statement_endorsements",
        "entity_terms",
        "id_ranges",
    ]



    @property
    def vitess_config(self) -> Any:
        """Get Vitess configuration."""
        return settings.to_vitess_config()

    async def ensure_tables_exist(self) -> Dict[str, str]:
        """Ensure all required tables exist using SchemaRepository."""
        results = {}

        try:
            from models.infrastructure.vitess.repositories.schema import SchemaRepository
            from models.infrastructure.vitess.client import VitessClient

            logger.info("Creating database tables using SchemaRepository...")
            vitess_client = VitessClient(config=self.vitess_config)
            schema_repository = SchemaRepository(vitess_client=vitess_client)
            schema_repository.create_tables()

            # Assume all tables were created successfully
            for table in self.required_tables:
                results[table] = "created"

            logger.info("Database tables created successfully")
            return results

        except Exception as e:
            logger.warning(f"SchemaRepository approach failed: {e}")
            # Fall back to raw SQL approach
            return await self.ensure_tables_exist_fallback()

    async def ensure_tables_exist_fallback(self) -> Dict[str, str]:
        """Ensure all required tables exist using raw SQL."""
        results = {}

        try:
            logger.info("Creating database tables using raw SQL fallback...")

            conn = pymysql.connect(
                host=self.vitess_config.host,
                port=self.vitess_config.port,
                user=self.vitess_config.user,
                password=self.vitess_config.password,
                database=self.vitess_config.database,
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
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS entity_redirects (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        redirect_from_id BIGINT UNSIGNED NOT NULL,
                        redirect_to_id BIGINT UNSIGNED NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(255) DEFAULT NULL,
                        INDEX idx_redirect_from (redirect_from_id),
                        INDEX idx_redirect_to (redirect_to_id),
                        UNIQUE KEY unique_redirect (redirect_from_id, redirect_to_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS statement_content (
                        content_hash BIGINT UNSIGNED PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ref_count INT DEFAULT 1,
                        INDEX idx_ref_count (ref_count DESC)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS entity_backlinks (
                        referenced_internal_id BIGINT UNSIGNED NOT NULL,
                        referencing_internal_id BIGINT UNSIGNED NOT NULL,
                        statement_hash BIGINT UNSIGNED NOT NULL,
                        property_id VARCHAR(32) NOT NULL,
                        `rank` ENUM('preferred', 'normal', 'deprecated') NOT NULL,
                        PRIMARY KEY (referenced_internal_id, referencing_internal_id, statement_hash),
                        FOREIGN KEY (referenced_internal_id) REFERENCES entity_id_mapping(internal_id),
                        FOREIGN KEY (referencing_internal_id) REFERENCES entity_id_mapping(internal_id),
                        FOREIGN KEY (statement_hash) REFERENCES statement_content(content_hash),
                        INDEX idx_backlinks_property (referencing_internal_id, property_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS backlink_statistics (
                        date DATE PRIMARY KEY,
                        total_backlinks BIGINT NOT NULL,
                        unique_entities_with_backlinks BIGINT NOT NULL,
                        top_entities_by_backlinks JSON NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS metadata_content (
                        content_hash BIGINT UNSIGNED NOT NULL,
                        content_type ENUM('labels', 'descriptions', 'aliases') NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ref_count INT DEFAULT 1,
                        PRIMARY KEY (content_hash, content_type),
                        INDEX idx_type_hash (content_type, content_hash),
                        INDEX idx_ref_count (ref_count DESC)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS user_daily_stats (
                        stat_date DATE PRIMARY KEY,
                        total_users BIGINT NOT NULL,
                        active_users BIGINT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS general_daily_stats (
                        stat_date DATE PRIMARY KEY,
                        total_statements BIGINT NOT NULL,
                        total_qualifiers BIGINT NOT NULL,
                        total_references BIGINT NOT NULL,
                        total_items BIGINT NOT NULL,
                        total_lexemes BIGINT NOT NULL,
                        total_properties BIGINT NOT NULL,
                        total_sitelinks BIGINT NOT NULL,
                        total_terms BIGINT NOT NULL,
                        terms_per_language JSON NOT NULL,
                        terms_by_type JSON NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        preferences JSON DEFAULT NULL,
                        watchlist_enabled BOOLEAN DEFAULT TRUE,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notification_limit INT DEFAULT 50,
                        retention_hours INT DEFAULT 24
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS watchlist (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        internal_entity_id BIGINT UNSIGNED NOT NULL,
                        watched_properties TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_watch (user_id, internal_entity_id, watched_properties(255)),
                        FOREIGN KEY (internal_entity_id) REFERENCES entity_id_mapping(internal_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS user_notifications (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        user_id BIGINT NOT NULL,
                        entity_id VARCHAR(50) NOT NULL,
                        revision_id BIGINT NOT NULL,
                        change_type VARCHAR(50) NOT NULL,
                        changed_properties JSON DEFAULT NULL,
                        event_timestamp TIMESTAMP NOT NULL,
                        is_checked BOOLEAN DEFAULT FALSE,
                        checked_at TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_user_timestamp (user_id, event_timestamp),
                        INDEX idx_entity (entity_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS user_activity (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        user_id BIGINT NOT NULL,
                        activity_type VARCHAR(50) NOT NULL,
                        entity_id VARCHAR(50),
                        revision_id BIGINT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_user_type_time (user_id, activity_type, created_at),
                        INDEX idx_entity (entity_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS user_thanks (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        from_user_id BIGINT NOT NULL,
                        to_user_id BIGINT NOT NULL,
                        internal_entity_id BIGINT UNSIGNED NOT NULL,
                        revision_id BIGINT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_from_user (from_user_id, created_at),
                        INDEX idx_to_user (to_user_id, created_at),
                        INDEX idx_revision (internal_entity_id, revision_id),
                        UNIQUE KEY unique_thank (from_user_id, internal_entity_id, revision_id),
                        FOREIGN KEY (internal_entity_id) REFERENCES entity_id_mapping(internal_id)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS user_statement_endorsements (
                        id BIGINT PRIMARY KEY AUTO_INCREMENT,
                        user_id BIGINT NOT NULL,
                        statement_hash BIGINT UNSIGNED NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        removed_at TIMESTAMP NULL,
                        INDEX idx_user (user_id, created_at),
                        INDEX idx_statement (statement_hash, created_at),
                        INDEX idx_removed (removed_at),
                        UNIQUE KEY unique_endorsement (user_id, statement_hash),
                        FOREIGN KEY (statement_hash) REFERENCES statement_content(content_hash)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS entity_terms (
                        hash BIGINT PRIMARY KEY,
                        term TEXT NOT NULL,
                        term_type ENUM('label', 'alias') NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS id_ranges (
                        entity_type VARCHAR(1) PRIMARY KEY,
                        current_range_start BIGINT UNSIGNED NOT NULL DEFAULT 1,
                        current_range_end BIGINT UNSIGNED NOT NULL DEFAULT 1000000,
                        range_size BIGINT UNSIGNED DEFAULT 1000000,
                        allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        worker_id VARCHAR(64),
                        version BIGINT DEFAULT 0
                    )
                    """,
                ]

                for sql in tables_sql:
                    cursor.execute(sql)

                # Initialize ID ranges for each entity type
                cursor.execute(
                    """
                    INSERT IGNORE INTO id_ranges (entity_type, current_range_start, current_range_end, range_size) VALUES
                    ('Q', 1, 1000000, 1000000),
                    ('P', 1, 1000000, 1000000),
                    ('L', 1, 1000000, 1000000),
                    ('E', 1, 1000000, 1000000)
                    """
                )

            conn.commit()
            conn.close()

            # Mark all tables as created
            for table in self.required_tables:
                results[table] = "created"

            logger.info("Created tables using raw SQL fallback")
            return results

        except Exception as e:
            logger.error(f"Raw SQL table creation failed: {e}")
            # Mark all tables as failed
            for table in self.required_tables:
                results[table] = f"failed: {e}"
            return results

    async def table_health_check(self) -> Dict[str, Any]:
        """Check if all required tables exist and are accessible."""
        issues = []
        healthy_tables = 0

        try:
            conn = pymysql.connect(
                host=self.vitess_config.host,
                port=self.vitess_config.port,
                user=self.vitess_config.user,
                password=self.vitess_config.password,
                database=self.vitess_config.database,
            )

            with conn.cursor() as cursor:
                # Check each required table
                for table in self.required_tables:
                    try:
                        cursor.execute(f"SHOW TABLES LIKE '{table}'")
                        if not cursor.fetchone():
                            issues.append(f"Table '{table}' does not exist")
                        else:
                            healthy_tables += 1
                    except Exception as e:
                        issues.append(f"Error checking table '{table}': {e}")

            conn.close()

        except Exception as e:
            issues.append(f"Database connection failed: {e}")

        overall_status = "healthy" if len(issues) == 0 else "unhealthy"

        return {
            "overall_status": overall_status,
            "healthy_tables": healthy_tables,
            "total_tables": len(self.required_tables),
            "issues": issues,
        }

    async def run_setup(self) -> Dict[str, Any]:
        """Run complete table setup process for development environment."""
        logger.info("Starting database table setup")

        # Ensure tables exist
        table_results = await self.ensure_tables_exist()

        # Perform health check
        health_status = await self.table_health_check()

        setup_results = {
            "tables_created": table_results,
            "health_check": health_status,
            "setup_status": "completed"
            if health_status["overall_status"] == "healthy"
            else "failed",
        }

        logger.info(
            f"Database table setup completed with status: {setup_results['setup_status']}"
        )
        return setup_results
