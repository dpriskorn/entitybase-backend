from typing import Any


class SchemaManager:
    def __init__(self, connection_manager: Any) -> None:
        self.connection_manager = connection_manager

    def create_tables(self) -> None:
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
            CREATE TABLE IF NOT EXISTS entity_revisions (
                internal_id BIGINT NOT NULL,
                revision_id BIGINT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_mass_edit BOOLEAN DEFAULT FALSE,
                edit_type VARCHAR(100) DEFAULT '',
                statements JSON NOT NULL,
                properties JSON NOT NULL,
                property_counts JSON NOT NULL,
                PRIMARY KEY (internal_id, revision_id)
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

        cursor.close()
