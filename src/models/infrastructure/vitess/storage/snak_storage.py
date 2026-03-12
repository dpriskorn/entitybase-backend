"""Snak storage operations using Vitess."""

import logging
from typing import Any

from models.data.common import OperationResult
from models.data.infrastructure.s3.snak_data import S3SnakData
from models.infrastructure.vitess.storage.base import BaseVitessStorage

logger = logging.getLogger(__name__)


class SnakVitessStorage(BaseVitessStorage):
    """Storage operations for snaks using Vitess."""

    table_name: str = "snaks"

    def store_snak(
        self,
        content_hash: int,
        snak_data: S3SnakData,
    ) -> OperationResult[None]:
        """Store snak in Vitess."""
        logger.debug(f"[SNAK_VITESS_STORE] hash={content_hash}")
        data = {
            "snak": snak_data.snak,
            "hash": content_hash,
            "schema": snak_data.schema_version,
            "created_at": snak_data.created_at,
        }
        result = self._store(content_hash, data)
        if result.success:
            logger.debug(f"[SNAK_VITESS_STORE] SUCCESS: hash={content_hash}")
        else:
            logger.error(f"[SNAK_VITESS_STORE] FAILED: {result.error}")
        return result

    def load_snak(self, content_hash: int) -> S3SnakData | None:
        """Load snak from Vitess."""
        logger.debug(f"[SNAK_VITESS_LOAD] hash={content_hash}")
        data = self._load(content_hash)
        if data is None:
            logger.debug(f"[SNAK_VITESS_LOAD] NOT FOUND: hash={content_hash}")
            return None

        return S3SnakData(
            snak=data.get("snak", {}),
            hash=content_hash,
            schema=data.get("schema", "1.0.0"),
            created_at=data.get("created_at", ""),
        )

    def load_snaks_batch(self, content_hashes: list[int]) -> list[S3SnakData | None]:
        """Load multiple snaks by content hashes."""
        logger.debug(f"[SNAK_VITESS_LOAD_BATCH] count={len(content_hashes)}")
        data_list = self._load_batch(content_hashes)

        results: list[S3SnakData | None] = []

        for i, data in enumerate(data_list):
            if data is None:
                results.append(None)
            else:
                results.append(
                    S3SnakData(
                        snak=data.get("snak", {}),
                        hash=content_hashes[i],
                        schema=data.get("schema", "1.0.0"),
                        created_at=data.get("created_at", ""),
                    )
                )
        return results

    def delete_snak(self, content_hash: int) -> OperationResult[None]:
        """Delete or decrement ref_count for snak."""
        logger.debug(f"[SNAK_VITESS_DELETE] hash={content_hash}")
        return self._decrement_ref_count(content_hash)

    def increment_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Increment reference count for snak."""
        return self._increment_ref_count(content_hash)

    def decrement_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Decrement reference count for snak."""
        return self._decrement_ref_count(content_hash)

    def exists(self, content_hash: int) -> bool:
        """Check if snak exists."""
        return self._exists(content_hash)
