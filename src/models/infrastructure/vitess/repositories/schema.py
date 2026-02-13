"""Manager for Vitess database schema operations."""

import logging
from models.infrastructure.vitess.repository import Repository
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class SchemaRepository(Repository):
    """Manager for creating and managing Vitess database schema."""

    def create_tables(self) -> None:
        """Create all required database tables."""
        logger.debug("Creating database tables")
        logger.debug("Validating Vitess client and connection")
        if not self.vitess_client:
            raise_validation_error(message="Vitess not initialized")
        if not self.vitess_client.connection_manager:
            raise_validation_error(message="Connection manager not initialized")
        if not self.vitess_client.connection_manager.connection:
            raise_validation_error(
                message="Connection manager variable not initialized"
            )
        logger.debug("Database connection validated, creating cursor")
        logger.debug("Starting table creation")
        with self.vitess_client.cursor as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS entity_id_mapping (
                    entity_id VARCHAR(50) PRIMARY KEY,
                    internal_id BIGINT UNSIGNED NOT NULL UNIQUE
                )
            """
            )

            cursor.execute(
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
            )

            cursor.execute(
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
                CREATE TABLE IF NOT EXISTS user_daily_stats (
                    stat_date DATE PRIMARY KEY,
                    total_users BIGINT NOT NULL,
                    active_users BIGINT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            cursor.execute(
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
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS entity_terms (
                    hash BIGINT UNSIGNED PRIMARY KEY,
                    term TEXT NOT NULL,
                    term_type ENUM('label', 'alias', 'description', 'form_representation', 'sense_gloss') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
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
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    internal_entity_id BIGINT UNSIGNED NOT NULL,
                    watched_properties TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_watch (user_id, internal_entity_id, watched_properties(255)),
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

            cursor.execute(
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
            """
            )

            cursor.execute(
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
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS lexeme_terms (
                    entity_id VARCHAR(20) NOT NULL,
                    form_sense_id VARCHAR(20) NOT NULL,
                    term_type ENUM('form', 'sense') NOT NULL,
                    language VARCHAR(10) NOT NULL,
                    term_hash BIGINT UNSIGNED NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (entity_id, form_sense_id, term_type, language),
                    INDEX idx_entity (entity_id),
                    INDEX idx_hash (term_hash),
                    INDEX idx_language (language)
                )
            """
            )
