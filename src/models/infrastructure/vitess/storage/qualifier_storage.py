"""Qualifier storage operations using Vitess."""

import logging
from typing import Any

from models.data.common import OperationResult
from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.infrastructure.vitess.storage.base import BaseVitessStorage

logger = logging.getLogger(__name__)


class QualifierVitessStorage(BaseVitessStorage):
    """Storage operations for qualifiers using Vitess."""

    table_name: str = "qualifiers"

    def store_qualifier(
        self,
        content_hash: int,
        qualifier_data: S3QualifierData,
    ) -> OperationResult[None]:
        """Store qualifier in Vitess."""
        logger.debug(f"[QUAL_VITESS_STORE] hash={content_hash}")
        data = {
            "qualifier": qualifier_data.qualifier,
            "hash": content_hash,
            "created_at": qualifier_data.created_at,
        }
        result = self._store(content_hash, data)
        if result.success:
            logger.debug(f"[QUAL_VITESS_STORE] SUCCESS: hash={content_hash}")
        else:
            logger.error(f"[QUAL_VITESS_STORE] FAILED: {result.error}")
        return result

    def load_qualifier(self, content_hash: int) -> S3QualifierData | None:
        """Load qualifier from Vitess."""
        logger.debug(f"[QUAL_VITESS_LOAD] hash={content_hash}")
        data = self._load(content_hash)
        if data is None:
            logger.debug(f"[QUAL_VITESS_LOAD] NOT FOUND: hash={content_hash}")
            return None

        return S3QualifierData(
            qualifier=data.get("qualifier", {}),
            hash=content_hash,
            created_at=data.get("created_at", ""),
        )

    def load_qualifiers_batch(
        self, content_hashes: list[int]
    ) -> list[S3QualifierData | None]:
        """Load multiple qualifiers by content hashes."""
        logger.debug(f"[QUAL_VITESS_LOAD_BATCH] count={len(content_hashes)}")
        data_list = self._load_batch(content_hashes)

        results: list[S3QualifierData | None] = []

        for i, data in enumerate(data_list):
            if data is None:
                results.append(None)
            else:
                results.append(
                    S3QualifierData(
                        qualifier=data.get("qualifier", {}),
                        hash=content_hashes[i],
                        created_at=data.get("created_at", ""),
                    )
                )
        return results

    def delete_qualifier(self, content_hash: int) -> OperationResult[None]:
        """Delete or decrement ref_count for qualifier."""
        logger.debug(f"[QUAL_VITESS_DELETE] hash={content_hash}")
        return self._decrement_ref_count(content_hash)

    def increment_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Increment reference count for qualifier."""
        return self._increment_ref_count(content_hash)

    def decrement_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Decrement reference count for qualifier."""
        return self._decrement_ref_count(content_hash)

    def exists(self, content_hash: int) -> bool:
        """Check if qualifier exists."""
        return self._exists(content_hash)
