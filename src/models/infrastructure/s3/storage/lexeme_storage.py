"""Lexeme storage operations for forms and senses."""

import logging
from typing import List, Optional

from models.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.enums import MetadataType
from models.infrastructure.s3.storage.metadata_storage import MetadataStorage

logger = logging.getLogger(__name__)


class LexemeStorage(MetadataStorage):
    """Storage operations for lexeme-specific terms (forms and senses)."""

    bucket: str = settings.s3_terms_bucket  # Use terms bucket for deduplication

    def store_form_representation(self, text: str, content_hash: int) -> OperationResult[None]:
        """Store form representation text in terms bucket."""
        logger.debug(f"Storing form representation: hash={content_hash}, text='{text[:50]}...'")
        return self.store_metadata(MetadataType.FORM_REPRESENTATIONS, content_hash, text)

    def store_sense_gloss(self, text: str, content_hash: int) -> OperationResult[None]:
        """Store sense gloss text in terms bucket."""
        logger.debug(f"Storing sense gloss: hash={content_hash}, text='{text[:50]}...'")
        return self.store_metadata(MetadataType.SENSE_GLOSSES, content_hash, text)

    def load_form_representations_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load form representations by content hashes."""
        logger.debug(f"Loading {len(hashes)} form representations")
        return self._load_metadata_batch(MetadataType.FORM_REPRESENTATIONS, hashes)

    def load_sense_glosses_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load sense glosses by content hashes."""
        logger.debug(f"Loading {len(hashes)} sense glosses")
        return self._load_metadata_batch(MetadataType.SENSE_GLOSSES, hashes)

    def _load_metadata_batch(self, metadata_type: MetadataType, hashes: List[int]) -> List[Optional[str]]:
        """Helper method to load metadata in batches."""
        from models.data.infrastructure.s3 import StringLoadResponse
        results = []
        for hash_val in hashes:
            try:
                data = self.load_metadata(metadata_type, hash_val)
                if isinstance(data, StringLoadResponse):
                    results.append(data.data)
                else:
                    logger.warning(f"Unexpected data type for {metadata_type} hash {hash_val}: {type(data)}")
                    results.append(None)
            except Exception as e:
                logger.warning(f"Failed to load {metadata_type} hash {hash_val}: {e}")
                results.append(None)
        return results