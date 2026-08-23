"""SQLite database schema creation with SQLite-compatible DDL."""

import logging
from typing import Any

from models.infrastructure.db.repository import Repository
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class SqliteSchemaRepository(Repository):
    """Creates and manages the SQLite database schema.

    Converts MySQL-specific DDL to SQLite-compatible syntax:
    - BIGINT UNSIGNED -> INTEGER
    - AUTO_INCREMENT -> AUTOINCREMENT
    - ENUM -> TEXT CHECK(...)
    - TIMESTAMP -> TEXT DEFAULT (datetime('now'))
    - JSON -> TEXT
    - BOOLEAN -> INTEGER
    """

    def create_tables(self) -> None:  # noqa: PLR0915
        """Create all required database tables using SQLite-compatible DDL."""
        logger.debug("Creating SQLite database tables")
        if not self.db_client:
            raise_validation_error(message="Database client not initialized")
        if not self.db_client.connection_manager:
            raise_validation_error(message="Connection manager not initialized")

        with self.db_client.cursor as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_id_mapping (
                    entity_id TEXT PRIMARY KEY,
                    internal_id INTEGER NOT NULL UNIQUE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_head (
                    internal_id INTEGER PRIMARY KEY,
                    head_revision_id INTEGER NOT NULL,
                    is_semi_protected INTEGER DEFAULT 0,
                    is_locked INTEGER DEFAULT 0,
                    is_archived INTEGER DEFAULT 0,
                    is_dangling INTEGER DEFAULT 0,
                    is_mass_edit_protected INTEGER DEFAULT 0,
                    is_deleted INTEGER DEFAULT 0,
                    is_redirect INTEGER DEFAULT 0,
                    redirects_to INTEGER
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_redirects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    redirect_from_id INTEGER NOT NULL,
                    redirect_to_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    created_by TEXT DEFAULT NULL,
                    UNIQUE (redirect_from_id, redirect_to_id)
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_redirect_from ON entity_redirects(redirect_from_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_redirect_to ON entity_redirects(redirect_to_id)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statement_content (
                    content_hash INTEGER PRIMARY KEY,
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_stmt_ref_count ON statement_content(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statements (
                    content_hash INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_stmts_ref_count ON statements(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qualifiers (
                    content_hash INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_qual_ref_count ON qualifiers(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS refs (
                    content_hash INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_refs_ref_count ON refs(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snaks (
                    content_hash INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_snaks_ref_count ON snaks(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_backlinks (
                    referenced_internal_id INTEGER NOT NULL,
                    referencing_internal_id INTEGER NOT NULL,
                    statement_hash INTEGER NOT NULL,
                    property_id TEXT NOT NULL,
                    rank TEXT NOT NULL CHECK(rank IN ('preferred', 'normal', 'deprecated')),
                    PRIMARY KEY (referenced_internal_id, referencing_internal_id, statement_hash),
                    FOREIGN KEY (referenced_internal_id) REFERENCES entity_id_mapping(internal_id),
                    FOREIGN KEY (referencing_internal_id) REFERENCES entity_id_mapping(internal_id),
                    FOREIGN KEY (statement_hash) REFERENCES statement_content(content_hash)
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_backlinks_property ON entity_backlinks(referencing_internal_id, property_id)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backlink_statistics (
                    date TEXT PRIMARY KEY,
                    total_backlinks INTEGER NOT NULL,
                    unique_entities_with_backlinks INTEGER NOT NULL,
                    top_entities_by_backlinks TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_daily_stats (
                    stat_date TEXT PRIMARY KEY,
                    total_users INTEGER NOT NULL,
                    active_users INTEGER NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS general_daily_stats (
                    stat_date TEXT PRIMARY KEY,
                    total_statements INTEGER NOT NULL,
                    total_qualifiers INTEGER NOT NULL,
                    total_references INTEGER NOT NULL,
                    total_items INTEGER NOT NULL,
                    total_lexemes INTEGER NOT NULL,
                    total_properties INTEGER NOT NULL,
                    total_sitelinks INTEGER NOT NULL,
                    total_terms INTEGER NOT NULL,
                    terms_per_language TEXT NOT NULL,
                    terms_by_type TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata_content (
                    content_hash INTEGER NOT NULL,
                    content_type TEXT NOT NULL CHECK(content_type IN ('labels', 'descriptions', 'aliases')),
                    data TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1,
                    PRIMARY KEY (content_hash, content_type)
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_meta_type_hash ON metadata_content(content_type, content_hash)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_meta_ref_count ON metadata_content(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sitelinks (
                    content_hash INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_sl_ref_count ON sitelinks(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_revisions (
                    internal_id INTEGER NOT NULL,
                    revision_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    is_mass_edit INTEGER DEFAULT 0,
                    edit_type TEXT DEFAULT '',
                    statements TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    property_counts TEXT NOT NULL,
                    labels_hashes TEXT,
                    descriptions_hashes TEXT,
                    aliases_hashes TEXT,
                    sitelinks_hashes TEXT,
                    user_id INTEGER,
                    edit_summary TEXT,
                    content_hash INTEGER NOT NULL,
                    PRIMARY KEY (internal_id, revision_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_terms (
                    hash INTEGER PRIMARY KEY,
                    term TEXT NOT NULL,
                    term_type TEXT NOT NULL CHECK(term_type IN ('label', 'alias', 'description', 'form_representation', 'sense_gloss')),
                    created_at TEXT DEFAULT (datetime('now')),
                    ref_count INTEGER DEFAULT 1
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_terms_ref_count ON entity_terms(ref_count DESC)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS id_ranges (
                    entity_type TEXT PRIMARY KEY,
                    current_range_start INTEGER NOT NULL DEFAULT 1,
                    current_range_end INTEGER NOT NULL DEFAULT 1000000,
                    range_size INTEGER DEFAULT 1000000,
                    allocated_at TEXT DEFAULT (datetime('now')),
                    worker_id TEXT,
                    version INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                INSERT OR IGNORE INTO id_ranges (entity_type, current_range_start, current_range_end, range_size)
                VALUES ('Q', 1, 1000000, 1000000),
                       ('P', 1, 1000000, 1000000),
                       ('L', 1, 1000000, 1000000),
                       ('E', 1, 1000000, 1000000)
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    created_at TEXT DEFAULT (datetime('now')),
                    preferences TEXT,
                    watchlist_enabled INTEGER DEFAULT 1,
                    last_activity TEXT DEFAULT (datetime('now')),
                    notification_limit INTEGER DEFAULT 50,
                    retention_hours INTEGER DEFAULT 24
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    internal_entity_id INTEGER NOT NULL,
                    watched_properties TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    UNIQUE (user_id, internal_entity_id, watched_properties),
                    FOREIGN KEY (internal_entity_id) REFERENCES entity_id_mapping(internal_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    entity_id TEXT NOT NULL,
                    revision_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL,
                    changed_properties TEXT,
                    event_timestamp TEXT NOT NULL,
                    is_checked INTEGER DEFAULT 0,
                    checked_at TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notif_user_time ON user_notifications(user_id, event_timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notif_entity ON user_notifications(entity_id)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    activity_type TEXT NOT NULL,
                    entity_id TEXT,
                    revision_id INTEGER,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_activity_user ON user_activity(user_id, activity_type, created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_activity_entity ON user_activity(entity_id)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_thanks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER NOT NULL,
                    to_user_id INTEGER NOT NULL,
                    internal_entity_id INTEGER NOT NULL,
                    revision_id INTEGER NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    UNIQUE (from_user_id, internal_entity_id, revision_id),
                    FOREIGN KEY (internal_entity_id) REFERENCES entity_id_mapping(internal_id)
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_thanks_from ON user_thanks(from_user_id, created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_thanks_to ON user_thanks(to_user_id, created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_thanks_revision ON user_thanks(internal_entity_id, revision_id)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_statement_endorsements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    statement_hash INTEGER NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    removed_at TEXT,
                    UNIQUE (user_id, statement_hash),
                    FOREIGN KEY (statement_hash) REFERENCES statement_content(content_hash)
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_endorse_user ON user_statement_endorsements(user_id, created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_endorse_stmt ON user_statement_endorsements(statement_hash, created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_endorse_removed ON user_statement_endorsements(removed_at)"
            )

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lexeme_terms (
                    entity_id TEXT NOT NULL,
                    form_sense_id TEXT NOT NULL,
                    term_type TEXT NOT NULL CHECK(term_type IN ('form', 'sense')),
                    language TEXT NOT NULL,
                    term_hash INTEGER NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    PRIMARY KEY (entity_id, form_sense_id, term_type, language)
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_lex_entity ON lexeme_terms(entity_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_lex_hash ON lexeme_terms(term_hash)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_lex_lang ON lexeme_terms(language)"
            )
