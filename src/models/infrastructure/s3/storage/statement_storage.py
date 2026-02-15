"""Statement storage operations."""

import json
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
        logger.debug(
            f"[STATEMENT_STORE] Preparing to store: bucket={self.bucket}, key={key}, "
            f"schema_version={schema_version}"
        )
        logger.debug(
            f"[STATEMENT_STORE] Statement data keys: {list(statement_data.keys())}"
        )

        stored = S3Statement(
            hash=content_hash,
            statement=statement_data["statement"],
            schema=schema_version,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        metadata = {"schema_version": schema_version}
        logger.debug(
            f"[STATEMENT_STORE] Calling base store: key={key}, "
            f"data_size={len(json.dumps(stored.model_dump(mode='json')))}"
        )
        result = self.store(key, stored, metadata=metadata)

        if result.success:
            logger.debug(f"[STATEMENT_STORE] SUCCESS: key={key}")
        else:
            logger.error(f"[STATEMENT_STORE] FAILED: key={key}, error={result.error}")

        return result

    def load_statement(self, content_hash: int) -> StatementResponse:
        """Read statement snapshot from S3."""
        key = str(content_hash)
        logger.debug(f"[STATEMENT_LOAD] Loading: bucket={self.bucket}, key={key}")

        try:
            load_response = self.load(key)
            if load_response is None:
                logger.warning(f"[STATEMENT_LOAD] NOT FOUND: key={key}")
                raise S3NotFoundError(f"Statement not found: {key}")
            data = load_response.data
            logger.debug(f"[STATEMENT_LOAD] Got data: key={key}, type={type(data)}")
            stored_statement = S3Statement.model_validate(data)

            logger.debug(
                f"[STATEMENT_LOAD] SUCCESS: key={key}, "
                f"statement_keys={list(stored_statement.statement.keys())}"
            )
            return StatementResponse(
                schema=stored_statement.schema_version,
                hash=stored_statement.content_hash,
                statement=stored_statement.statement,
                created_at=stored_statement.created_at,
            )
        except S3NotFoundError:
            raise  # Re-raise as is
        except Exception as e:
            logger.error(
                f"[STATEMENT_LOAD] ERROR: key={key}, error={type(e).__name__}: {e}"
            )
            raise

    def delete_statement(self, content_hash: int) -> OperationResult[None]:
        """Delete statement from S3."""
        key = str(content_hash)
        logger.debug(f"[STATEMENT_DELETE] Deleting: bucket={self.bucket}, key={key}")
        return self.delete(key)
