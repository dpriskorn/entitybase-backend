from typing import Any, Optional
import pymysql
from pydantic import BaseModel, Field

from services.shared.models.vitess_models import (
    VitessConfig,
    RegisterEntityRequest,
    RegisterEntityResponse,
    GetHeadRequest,
    GetHeadResponse,
    CASUpdateHeadRequest,
    InsertRevisionRequest,
    GetHistoryRequest,
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
                PRIMARY KEY (entity_id, revision_id)
            )
        """)
        
        cursor.close()
    
    def register_entity(self, request: RegisterEntityRequest) -> RegisterEntityResponse:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entity_id_mapping (external_id, internal_id) VALUES (%s, %s)",
            (request.external_id, request.internal_id)
        )
        cursor.close()
        return RegisterEntityResponse(success=True)
    
    def resolve_id(self, request: GetHeadRequest) -> GetHeadResponse:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT internal_id FROM entity_id_mapping WHERE external_id = %s",
            (request.entity_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return GetHeadResponse(head_revision_id=result[0] if result else None)
    
    def get_head(self, request: GetHeadRequest) -> GetHeadResponse:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT head_revision_id FROM entity_head WHERE entity_id = %s",
            (request.entity_id,)
        )
        result = cursor.fetchone()
        cursor.close()
        return GetHeadResponse(head_revision_id=result[0] if result else None)
    
    def cas_update_head(self, request: CASUpdateHeadRequest) -> bool:
        conn = self.connect()
        cursor = conn.cursor()
        if request.old_revision_id is None:
            cursor.execute(
                "INSERT INTO entity_head (entity_id, head_revision_id) VALUES (%s, %s)",
                (request.entity_id, request.new_revision_id)
            )
        else:
            cursor.execute(
                "UPDATE entity_head SET head_revision_id = %s WHERE entity_id = %s AND head_revision_id = %s",
                (request.new_revision_id, request.entity_id, request.old_revision_id)
            )
        success = cursor.rowcount > 0
        cursor.close()
        return success
    
    def insert_revision(self, request: InsertRevisionRequest) -> None:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entity_revisions (entity_id, revision_id) VALUES (%s, %s)",
            (request.entity_id, request.revision_id)
        )
        cursor.close()
    
    def get_history(self, request: GetHistoryRequest) -> list[HistoryRecord]:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT revision_id, created_at FROM entity_revisions WHERE entity_id = %s ORDER BY revision_id",
            (request.entity_id,)
        )
        result = [HistoryRecord(revision_id=row[0], created_at=str(row[1])) for row in cursor.fetchall()]
        cursor.close()
        return result
