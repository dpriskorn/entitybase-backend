from typing import Any, Optional
import pymysql
from pydantic import BaseModel, Field

from services.shared.models.vitess_models import (
    VitessConfig,
    HistoryRecord
)


class VitessClient(BaseModel):
    config: VitessConfig
    connection: Optional[Any] = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, config: VitessConfig, **kwargs):
        super().__init__(config=config, **kwargs)
        self.connection = None
        self._create_tables()
    
    def connect(self):
        if not self.connection:
            self.connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                passwd=self.config.password,
                database=self.config.database,
                autocommit=True
            )
        return self.connection
    
    def _create_tables(self):
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_id_mapping (
                external_id VARCHAR(255) PRIMARY KEY,
                internal_id BIGINT NOT NULL UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_head (
                entity_id BIGINT PRIMARY KEY,
                head_revision_id BIGINT NOT NULL,
                is_semi_protected BOOLEAN DEFAULT FALSE,
                is_locked BOOLEAN DEFAULT FALSE,
                is_archived BOOLEAN DEFAULT FALSE,
                is_dangling BOOLEAN DEFAULT FALSE,
                is_mass_edit_protected BOOLEAN DEFAULT FALSE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_revisions (
                entity_id BIGINT NOT NULL,
                revision_id BIGINT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_mass_edit BOOLEAN DEFAULT FALSE,
                edit_type VARCHAR(100) DEFAULT '',
                PRIMARY KEY (entity_id, revision_id)
            )
        """)
        
        cursor.close()
    
    def register_entity(self, external_id: str, internal_id: int) -> None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entity_id_mapping (external_id, internal_id) VALUES (%s, %s)",
            (external_id, internal_id)
        )
        cursor.close()
    
    def resolve_id(self, external_id: str) -> int | None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT internal_id FROM entity_id_mapping WHERE external_id = %s",
            (external_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def get_head(self, entity_id: int) -> int | None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT head_revision_id FROM entity_head WHERE entity_id = %s",
            (entity_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def cas_update_head(self, entity_id: int, old_revision_id: int | None, new_revision_id: int) -> bool:
        conn = self.connect()
        cursor = conn.cursor()
        if old_revision_id is None:
            cursor.execute(
                "INSERT INTO entity_head (entity_id, head_revision_id) VALUES (%s, %s)",
                (entity_id, new_revision_id)
            )
        else:
            cursor.execute(
                "UPDATE entity_head SET head_revision_id = %s WHERE entity_id = %s AND head_revision_id = %s",
                (new_revision_id, entity_id, old_revision_id)
            )
        success = cursor.rowcount > 0
        cursor.close()
        return success
    
    def insert_revision(self, entity_id: int, revision_id: int, is_mass_edit: bool = False, edit_type: str = "") -> None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entity_revisions (entity_id, revision_id, is_mass_edit, edit_type) VALUES (%s, %s, %s, %s)",
            (entity_id, revision_id, is_mass_edit, edit_type)
        )
        cursor.close()
    
    def get_history(self, entity_id: int) -> list[HistoryRecord]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT revision_id, created_at, is_mass_edit FROM entity_revisions WHERE entity_id = %s ORDER BY revision_id",
            (entity_id,)
        )
        result = [HistoryRecord(revision_id=row[0], created_at=str(row[1]), is_mass_edit=row[2]) for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def cas_update_head_with_status(
        self,
        entity_id: int,
        old_revision_id: int | None,
        new_revision_id: int,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool
    ) -> bool:
        """Atomic CAS update including status flags"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if old_revision_id is None:
            cursor.execute(
                """INSERT INTO entity_head
                   (entity_id, head_revision_id, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (entity_id, new_revision_id, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected)
            )
        else:
            cursor.execute(
                """UPDATE entity_head
                   SET head_revision_id = %s,
                       is_semi_protected = %s,
                       is_locked = %s,
                       is_archived = %s,
                       is_dangling = %s,
                       is_mass_edit_protected = %s
                   WHERE entity_id = %s AND head_revision_id = %s""",
                (new_revision_id, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected,
                 entity_id, old_revision_id)
            )
        
        success = cursor.rowcount > 0
        cursor.close()
        return success
    
    def list_locked_entities(self, limit: int) -> list[str]:
        """List all locked items"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.external_id
               FROM entity_head h
               JOIN entity_id_mapping m ON h.entity_id = m.internal_id
               WHERE h.is_locked = TRUE
               LIMIT %s""",
            (limit,)
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def list_semi_protected_entities(self, limit: int) -> list[str]:
        """List all semi-protected items"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.external_id
               FROM entity_head h
               JOIN entity_id_mapping m ON h.entity_id = m.internal_id
               WHERE h.is_semi_protected = TRUE
               LIMIT %s""",
            (limit,)
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def list_archived_entities(self, limit: int) -> list[str]:
        """List all archived items"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.external_id
               FROM entity_head h
               JOIN entity_id_mapping m ON h.entity_id = m.internal_id
               WHERE h.is_archived = TRUE
               LIMIT %s""",
            (limit,)
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def list_dangling_entities(self, limit: int) -> list[str]:
        """List all dangling items"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.external_id
               FROM entity_head h
               JOIN entity_id_mapping m ON h.entity_id = m.internal_id
               WHERE h.is_dangling = TRUE
               LIMIT %s""",
            (limit,)
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
    
    def list_by_edit_type(self, edit_type: str, limit: int) -> list[str]:
        """List entities by edit_type of latest revision"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT m.external_id
               FROM entity_head h
               JOIN entity_id_mapping m ON h.entity_id = m.internal_id
               JOIN entity_revisions r ON h.entity_id = r.entity_id AND h.head_revision_id = r.revision_id
               WHERE r.edit_type = %s
               LIMIT %s""",
            (edit_type, limit)
        )
        result = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return result
