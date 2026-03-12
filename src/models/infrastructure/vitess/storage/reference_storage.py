"""Reference storage operations using Vitess."""

import logging
from typing import Any

from models.data.common import OperationResult
from models.data.infrastructure.s3.reference_data import S3ReferenceData
from models.infrastructure.vitess.storage.base import BaseVitessStorage

logger = logging.getLogger(__name__)


class ReferenceVitessStorage(BaseVitessStorage):
    """Storage operations for references using Vitess."""

    table_name: str = "refs"

    def store_reference(
        self,
        content_hash: int,
        reference_data: S3ReferenceData,
    ) -> OperationResult[None]:
        """Store reference in Vitess."""
        logger.debug(f"[REF_VITESS_STORE] hash={content_hash}")
        data = {
            "reference": reference_data.reference,
            "hash": content_hash,
            "created_at": reference_data.created_at,
        }
        result = self._store(content_hash, data)
        if result.success:
            logger.debug(f"[REF_VITESS_STORE] SUCCESS: hash={content_hash}")
        else:
            logger.error(f"[REF_VITESS_STORE] FAILED: {result.error}")
        return result

    def load_reference(self, content_hash: int) -> S3ReferenceData | None:
        """Load reference from Vitess."""
        logger.debug(f"[REF_VITESS_LOAD] hash={content_hash}")
        data = self._load(content_hash)
        if data is None:
            logger.debug(f"[REF_VITESS_LOAD] NOT FOUND: hash={content_hash}")
            return None

        return S3ReferenceData(
            reference=data.get("reference", {}),
            hash=content_hash,
            created_at=data.get("created_at", ""),
        )

    def load_references_batch(
        self, content_hashes: list[int]
    ) -> list[S3ReferenceData | None]:
        """Load multiple references by content hashes."""
        logger.debug(f"[REF_VITESS_LOAD_BATCH] count={len(content_hashes)}")
        data_list = self._load_batch(content_hashes)

        results: list[S3ReferenceData | None] = []

        for i, data in enumerate(data_list):
            if data is None:
                results.append(None)
            else:
                results.append(
                    S3ReferenceData(
                        reference=data.get("reference", {}),
                        hash=content_hashes[i],
                        created_at=data.get("created_at", ""),
                    )
                )
        return results

    def delete_reference(self, content_hash: int) -> OperationResult[None]:
        """Delete or decrement ref_count for reference."""
        logger.debug(f"[REF_VITESS_DELETE] hash={content_hash}")
        return self._decrement_ref_count(content_hash)

    def increment_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Increment reference count for reference."""
        return self._increment_ref_count(content_hash)

    def decrement_ref_count(self, content_hash: int) -> OperationResult[None]:
        """Decrement reference count for reference."""
        return self._decrement_ref_count(content_hash)

    def exists(self, content_hash: int) -> bool:
        """Check if reference exists."""
        return self._exists(content_hash)
