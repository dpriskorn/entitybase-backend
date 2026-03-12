"""Statement storage operations using Vitess."""

import logging
from typing import Any

from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.response import StatementResponse
from models.infrastructure.vitess.storage.base import BaseVitessStorage

logger = logging.getLogger(__name__)


class StatementVitessStorage(BaseVitessStorage):
    """Storage operations for statements using Vitess."""

    table_name: str = "statements"

    def store_statement(
        self,
        content_hash: int,
        statement_data: dict[str, Any],
    ) -> OperationResult[None]:
        """Store statement in Vitess."""
        logger.debug(f"[STMT_VITESS_STORE] hash={content_hash}")
        result = self._store(content_hash, statement_data)
        if result.success:
            logger.debug(f"[STMT_VITESS_STORE] SUCCESS: hash={content_hash}")
        else:
            logger.error(f"[STMT_VITESS_STORE] FAILED: {result.error}")
        return result

    def load_statement(self, content_hash: int) -> StatementResponse | None:
        """Load statement from Vitess."""
        logger.debug(f"[STMT_VITESS_LOAD] hash={content_hash}")
        data = self._load(content_hash)
        if data is None:
            logger.debug(f"[STMT_VITESS_LOAD] NOT FOUND: hash={content_hash}")
            return None

        return StatementResponse(
            schema=data.get("schema", "1.0.0"),
            hash=content_hash,
            statement=data.get("statement", {}),
            created_at=data.get("created_at", ""),
        )

    def load_statements_batch(
        self, content_hashes: list[int]
    ) -> list[StatementResponse | None]:
        """Load multiple statements by content hashes."""
        logger.debug(f"[STMT_VITESS_LOAD_BATCH] count={len(content_hashes)}")
        data_list = self._load_batch(content_hashes)

        results: list[StatementResponse | None] = []

        for i, data in enumerate(data_list):
            if data is None:
                results.append(None)
            else:
                results.append(
                    StatementResponse(
                        schema=data.get("schema", "1.0.0"),
                        hash=content_hashes[i],
                        statement=data.get("statement", {}),
                        created_at=data.get("created_at", ""),
                    )
                )
        return results

    def delete_statement(self, content_hash: int) -> OperationResult[None]:
        """Delete or decrement ref_count for statement."""
        logger.debug(f"[STMT_VITESS_DELETE] hash={content_hash}")
        return self._decrement_ref_count(content_hash)

    def increment_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Increment reference count for statement."""
        return self._increment_ref_count(content_hash)

    def decrement_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Decrement reference count for statement."""
        return self._decrement_ref_count(content_hash)

    def exists(self, content_hash: int) -> bool:
        """Check if statement exists."""
        return self._exists(content_hash)
