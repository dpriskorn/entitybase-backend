"""Manager for Vitess database schema operations."""

"""Manager for Vitess database schema operations."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manager for creating and managing Vitess database schema."""

    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def create_tables(self) -> None:
        """Create all required database tables."""
        logger.debug("Creating database tables")
        conn = self.connection_manager.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_id_mapping (
                entity_id VARCHAR(50) PRIMARY KEY,
                internal_id BIGINT NOT NULL UNIQUE
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_head (
                internal_id BIGINT PRIMARY KEY,
                head_revision_id BIGINT NOT NULL,
                is_semi_protected BOOLEAN DEFAULT FALSE,
                is_locked BOOLEAN DEFAULT FALSE,
                is_archived BOOLEAN DEFAULT FALSE,
                is_dangling BOOLEAN DEFAULT FALSE,
                is_mass_edit_protected BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE,
                is_redirect BOOLEAN DEFAULT FALSE,
                redirects_to BIGINT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_redirects (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                redirect_from_id BIGINT NOT NULL,
                redirect_to_id BIGINT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(255) DEFAULT NULL,
                INDEX idx_redirect_from (redirect_from_id),
                INDEX idx_redirect_to (redirect_to_id),
                UNIQUE KEY unique_redirect (redirect_from_id, redirect_to_id)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS statement_content (
                content_hash BIGINT UNSIGNED PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ref_count INT DEFAULT 1,
                INDEX idx_ref_count (ref_count DESC)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_backlinks (
                referenced_internal_id BIGINT NOT NULL,
                referencing_internal_id BIGINT NOT NULL,
                statement_hash BIGINT UNSIGNED NOT NULL,
                property_id VARCHAR(32) NOT NULL,
                `rank` ENUM('preferred', 'normal', 'deprecated') NOT NULL,
                PRIMARY KEY (referenced_internal_id, referencing_internal_id, statement_hash),
                FOREIGN KEY (referenced_internal_id) REFERENCES entity_id_mapping(internal_id),
                FOREIGN KEY (referencing_internal_id) REFERENCES entity_id_mapping(internal_id),
                FOREIGN KEY (statement_hash) REFERENCES statement_content(content_hash),
                INDEX idx_backlinks_property (referencing_internal_id, property_id)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS backlink_statistics (
                date DATE PRIMARY KEY,
                total_backlinks BIGINT NOT NULL,
                unique_entities_with_backlinks BIGINT NOT NULL,
                top_entities_by_backlinks JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
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
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_revisions (
                internal_id BIGINT NOT NULL,
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
                PRIMARY KEY (internal_id, revision_id)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entity_terms (
                hash BIGINT PRIMARY KEY,
                term TEXT NOT NULL,
                term_type ENUM('label', 'alias') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS id_ranges (
                entity_type VARCHAR(1) PRIMARY KEY,
                current_range_start BIGINT NOT NULL DEFAULT 1,
                current_range_end BIGINT NOT NULL DEFAULT 1000000,
                range_size BIGINT DEFAULT 1000000,
                allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                worker_id VARCHAR(64),
                version BIGINT DEFAULT 0
            )
        """
        )

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

        cursor.execute(
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
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS watchlist (
                user_id BIGINT NOT NULL,
                internal_entity_id BIGINT NOT NULL,
                watched_properties TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, internal_entity_id, watched_properties(255)),
                FOREIGN KEY (internal_entity_id) REFERENCES entity_id_mapping(internal_id)
            )
        """
        )

        cursor.execute(
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
        """
        )

        cursor.execute(
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
        """
        )

        cursor.close()
