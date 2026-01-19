"""Statement storage operations."""

import logging
from datetime import timezone, datetime
from typing import TYPE_CHECKING

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.connection import S3ConnectionManager
from models.infrastructure.s3.revision.stored_statement import StoredStatement
from models.rest_api.entitybase.v1.response import StatementResponse

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class StatementStorage(BaseS3Storage):
    """Storage operations for statements."""

    def __init__(self, connection_manager: S3ConnectionManager) -> None:
        super().__init__(connection_manager, settings.s3_statements_bucket)

    def store_statement(
        self,
        content_hash: int,
        statement_data: dict,
        schema_version: str,
    ) -> OperationResult[None]:
        """Write statement snapshot to S3."""
        key = str(content_hash)
        stored = StoredStatement(
            hash=content_hash,
            statement=statement_data["statement"],
            schema=schema_version,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        metadata = {"schema_version": schema_version}
        return self.store(key, stored, metadata=metadata)

    def load_statement(self, content_hash: int) -> StatementResponse:
        """Read statement snapshot from S3."""
        key = str(content_hash)

        try:
            data = self.load(key)
            stored_statement = StoredStatement.model_validate(data)

            return StatementResponse(
                schema=stored_statement.schema_version,
                hash=stored_statement.content_hash,
                statement=stored_statement.statement,
                created_at=stored_statement.created_at,
            )
        except S3NotFoundError:
            raise  # Re-raise as is

    def delete_statement(self, content_hash: int) -> OperationResult[None]:
        """Delete statement from S3."""
        key = str(content_hash)
        return self.delete(key)
