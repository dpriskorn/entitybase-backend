"""Statement storage operations."""

import logging
from datetime import timezone, datetime

from models.data.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.statement import S3Statement
from models.infrastructure.s3.base_storage import BaseS3Storage
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.data.rest_api.v1.entitybase.response import StatementResponse

logger = logging.getLogger(__name__)


class StatementStorage(BaseS3Storage):
    """Storage operations for statements."""

    bucket: str = settings.s3_statements_bucket

    def store_statement(
        self,
        content_hash: int,
        statement_data: dict,
        schema_version: str,
    ) -> OperationResult[None]:
        """Write statement snapshot to S3."""
        key = str(content_hash)
        stored = S3Statement(
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
            data = self.load(key).data
            stored_statement = S3Statement.model_validate(data)

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
