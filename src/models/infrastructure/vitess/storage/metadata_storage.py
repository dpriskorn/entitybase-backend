"""Metadata storage operations using Vitess (terms and sitelinks)."""

import logging
from typing import Any, cast

from models.data.common import OperationResult
from models.infrastructure.vitess.repository import Repository

logger = logging.getLogger(__name__)


class MetadataVitessStorage(Repository):
    """Storage operations for metadata (labels, descriptions, aliases, lemmas, forms, senses) using Vitess."""

    table_name: str = "metadata_content"

    def store_lemma(self, content_hash: int, value: str) -> OperationResult[None]:
        """Store lemma in Vitess."""
        return self.store_metadata(content_hash, "lemma", value)

    def store_form_representation(
        self, content_hash: int, value: str
    ) -> OperationResult[None]:
        """Store form representation in Vitess."""
        return self.store_metadata(content_hash, "form_representation", value)

    def store_sense_gloss(self, content_hash: int, value: str) -> OperationResult[None]:
        """Store sense gloss in Vitess."""
        return self.store_metadata(content_hash, "sense_gloss", value)

    def load_lemmas_batch(self, hashes: list[int]) -> list[str | None]:
        """Load lemmas by content hashes."""
        return [self.load_metadata(h, "lemma") for h in hashes]

    def load_form_representations_batch(self, hashes: list[int]) -> list[str | None]:
        """Load form representations by content hashes."""
        return [self.load_metadata(h, "form_representation") for h in hashes]

    def load_sense_glosses_batch(self, hashes: list[int]) -> list[str | None]:
        """Load sense glosses by content hashes."""
        return [self.load_metadata(h, "sense_gloss") for h in hashes]

    def store_metadata(
        self,
        content_hash: int,
        content_type: str,
        value: str,
    ) -> OperationResult[None]:
        """Store metadata (label, description, alias) in Vitess."""
        logger.debug(
            f"[METADATA_VITESS_STORE] hash={content_hash}, type={content_type}"
        )
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""INSERT INTO {self.table_name} (content_hash, content_type, data, ref_count)
                        VALUES (%s, %s, %s, 1)
                        ON DUPLICATE KEY UPDATE
                        ref_count = ref_count + 1,
                        data = VALUES(data)""",
                    (content_hash, content_type, value),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            logger.error(f"[METADATA_VITESS_STORE] Failed: {e}")
            return OperationResult(success=False, error=str(e))

    def load_metadata(
        self,
        content_hash: int,
        content_type: str,
    ) -> str | None:
        """Load metadata from Vitess."""
        logger.debug(f"[METADATA_VITESS_LOAD] hash={content_hash}, type={content_type}")
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""SELECT data FROM {self.table_name}
                        WHERE content_hash = %s AND content_type = %s""",
                    (content_hash, content_type),
                )
                result = cursor.fetchone()
                if result:
                    return cast(str, result[0])
                return None
        except Exception as e:
            logger.error(f"[METADATA_VITESS_LOAD] Failed: {e}")
            return None

    def delete_metadata(
        self,
        content_hash: int,
        content_type: str,
    ) -> OperationResult[None]:
        """Delete or decrement ref_count for metadata."""
        logger.debug(
            f"[METADATA_VITESS_DELETE] hash={content_hash}, type={content_type}"
        )
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""UPDATE {self.table_name} SET ref_count = ref_count - 1
                        WHERE content_hash = %s AND content_type = %s AND ref_count > 0""",
                    (content_hash, content_type),
                )
                cursor.execute(
                    f"""DELETE FROM {self.table_name}
                        WHERE content_hash = %s AND content_type = %s AND ref_count <= 0""",
                    (content_hash, content_type),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            logger.error(f"[METADATA_VITESS_DELETE] Failed: {e}")
            return OperationResult(success=False, error=str(e))


class SitelinkVitessStorage(Repository):
    """Storage operations for sitelinks using Vitess."""

    table_name: str = "sitelinks"

    def store_sitelink(
        self,
        content_hash: int,
        title: str,
    ) -> OperationResult[None]:
        """Store sitelink in Vitess."""
        logger.debug(f"[SITELINK_VITESS_STORE] hash={content_hash}")
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""INSERT INTO {self.table_name} (content_hash, title, ref_count)
                        VALUES (%s, %s, 1)
                        ON DUPLICATE KEY UPDATE
                        ref_count = ref_count + 1,
                        title = VALUES(title)""",
                    (content_hash, title),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            logger.error(f"[SITELINK_VITESS_STORE] Failed: {e}")
            return OperationResult(success=False, error=str(e))

    def load_sitelink(self, content_hash: int) -> str | None:
        """Load sitelink from Vitess."""
        logger.debug(f"[SITELINK_VITESS_LOAD] hash={content_hash}")
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"SELECT title FROM {self.table_name} WHERE content_hash = %s",
                    (content_hash,),
                )
                result = cursor.fetchone()
                if result:
                    return cast(str, result[0])
                return None
        except Exception as e:
            logger.error(f"[SITELINK_VITESS_LOAD] Failed: {e}")
            return None

    def delete_sitelink(self, content_hash: int) -> OperationResult[None]:
        """Delete or decrement ref_count for sitelink."""
        logger.debug(f"[SITELINK_VITESS_DELETE] hash={content_hash}")
        try:
            with self.vitess_client.cursor as cursor:
                cursor.execute(
                    f"""UPDATE {self.table_name} SET ref_count = ref_count - 1
                        WHERE content_hash = %s AND ref_count > 0""",
                    (content_hash,),
                )
                cursor.execute(
                    f"""DELETE FROM {self.table_name}
                        WHERE content_hash = %s AND ref_count <= 0""",
                    (content_hash,),
                )
                return OperationResult(success=True, data=None)
        except Exception as e:
            logger.error(f"[SITELINK_VITESS_DELETE] Failed: {e}")
            return OperationResult(success=False, error=str(e))
