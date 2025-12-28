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
                head_revision_id BIGINT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_revisions (
                entity_id BIGINT NOT NULL,
                revision_id BIGINT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                is_mass_edit BOOLEAN DEFAULT FALSE,
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
    
    def insert_revision(self, entity_id: int, revision_id: int, is_mass_edit: bool = False) -> None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entity_revisions (entity_id, revision_id, is_mass_edit) VALUES (%s, %s, %s)",
            (entity_id, revision_id, is_mass_edit)
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
