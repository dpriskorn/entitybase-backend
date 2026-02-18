"""Mock classes for contract tests.

This module provides mock implementations of VitessClient, S3Client, and StateHandler
for use in contract tests. These mocks simulate the real clients without requiring
external services (Vitess, S3).
"""

import sys
from typing import Any, Literal
from unittest.mock import MagicMock

sys.path.insert(0, "src")


class MockHistoryEntry:
    def __init__(self, revision_id: int, created_at: str) -> None:
        self.revision_id = revision_id
        self.created_at = created_at


class MockConnectionManager:
    """Mock Vitess connection manager."""

    def __init__(self) -> None:
        self.connection = MagicMock()

    def acquire(self) -> Any:
        return self.connection

    def release(self, connection: Any) -> None:
        pass

    @property
    def healthy_connection(self) -> bool:
        return True


class MockCursor:
    def __init__(self) -> None:
        self._rows: list[tuple] = []

    def execute(self, query: str, params: Any = None) -> None:
        pass

    def fetchone(self) -> tuple | None:
        if self._rows:
            return self._rows[0]
        return None

    def fetchall(self) -> list[tuple]:
        return self._rows

    def close(self) -> None:
        pass

    def __enter__(self) -> "MockCursor":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
        return False


class MockIdResolver:
    def __init__(self) -> None:
        self._entity_to_internal: dict[str, int] = {}
        self._internal_to_entity: dict[int, str] = {}
        self._next_internal_id = 1

    def resolve_id(self, entity_id: str) -> int:
        return self._entity_to_internal.get(entity_id, 0)

    def resolve_entity_id(self, internal_id: int) -> str | None:
        return self._internal_to_entity.get(internal_id)

    def entity_exists(self, entity_id: str) -> bool:
        return entity_id in self._entity_to_internal

    def register_entity(self, entity_id: str) -> int:
        if entity_id in self._entity_to_internal:
            return self._entity_to_internal[entity_id]
        internal_id = self._next_internal_id
        self._next_internal_id += 1
        self._entity_to_internal[entity_id] = internal_id
        self._internal_to_entity[internal_id] = entity_id
        return internal_id


class MockUserRepository:
    def user_exists(self, user_id: int) -> bool:
        return False

    def is_watchlist_enabled(self, user_id: int) -> bool:
        return False

    def update_user_activity(self, user_id: int) -> MagicMock:
        result = MagicMock()
        result.success = True
        return result


class MockWatchlistRepository:
    def get_watches_for_user(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> MagicMock:
        result = MagicMock()
        result.success = True
        result.watches = []
        return result


class MockEntityRepository:
    def __init__(self, vitess_client: Any) -> None:
        self.vitess_client = vitess_client

    def list_entities_filtered(
        self,
        entity_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[str]:
        return []

    def create_entity(self, entity_id: str) -> None:
        self.vitess_client.id_resolver.register_entity(entity_id)

    def delete_entity(self, entity_id: str) -> None:
        pass

    def delete(self, entity_id: str, revision_id: int) -> None:
        pass


class MockRevisionRepository:
    def get_revision(self, entity_id: int, revision_id: int) -> MagicMock | None:
        return None


class MockHeadRepository:
    def get_head_revision(self, entity_id: int) -> MagicMock | None:
        return None


class MockStatementRepository:
    def get_most_used(self, limit: int = 100) -> list[int]:
        return []


class MockVitessClient:
    def __init__(self) -> None:
        self.id_resolver = MockIdResolver()
        self.connection_manager = MockConnectionManager()
        self.user_repository = MockUserRepository()
        self.watchlist_repository = MockWatchlistRepository()
        self.entity_repository = MockEntityRepository(vitess_client=self)
        self.revision_repository = MockRevisionRepository()
        self.head_repository = MockHeadRepository()
        self.statement_repository = MockStatementRepository()
        self._cursor = MockCursor()
        self._s3_client: Any = None
        self._pending_revisions: dict[tuple[str, int], int] = {}

    def set_s3_client(self, s3_client: Any) -> None:
        self._s3_client = s3_client

    @property
    def cursor(self) -> "MockCursor":
        return self._cursor

    @property
    def healthy_connection(self) -> bool:
        return True

    def entity_exists(self, entity_id: str) -> bool:
        return self.id_resolver.entity_exists(entity_id)

    def is_entity_deleted(self, entity_id: str) -> bool:
        return False

    def get_head(self, entity_id: str) -> int:
        return 1 if self.entity_exists(entity_id) else 0

    def get_history(self, entity_id: str) -> list[Any]:
        return (
            [MockHistoryEntry(revision_id=1, created_at="2024-01-01T00:00:00Z")]
            if self.entity_exists(entity_id)
            else []
        )

    def get_entity_history(
        self, entity_id: str, limit: int = 20, offset: int = 0
    ) -> list[Any]:
        return self.get_history(entity_id)

    def get_backlinks(
        self, internal_id: int, limit: int = 100, offset: int = 0
    ) -> list[MagicMock]:
        return []

    def disconnect(self) -> None:
        pass

    def create_revision(
        self,
        entity_id: str,
        entity_data: Any,
        revision_id: int,
        content_hash: int,
        expected_revision_id: int | None = None,
    ) -> None:
        self._pending_revisions[(entity_id, revision_id)] = content_hash

    def get_pending_revisions(self) -> dict[tuple[str, int], int]:
        return self._pending_revisions.copy()

    def clear_pending_revisions(self) -> None:
        self._pending_revisions.clear()

    def decrement_ref_count(self, hash_val: int) -> None:
        pass

    def get_ref_count(self, hash_val: int) -> int:
        return 0

    def delete_revision(self, entity_id: str, revision_id: int) -> None:
        pass


class MockS3ConnectionManager:
    @property
    def healthy_connection(self) -> bool:
        return True


class MockS3Client:
    def __init__(self) -> None:
        self.connection_manager = MockS3ConnectionManager()
        self._revisions: dict[int, dict[str, Any]] = {}
        self._revision_hashes: dict[tuple[str, int], int] = {}
        self._vitess_client: Any = None
        self._term_metadata: dict[int, tuple[str, str]] = {}  # hash -> (value, type)

    def set_vitess_client(self, vitess_client: Any) -> None:
        self._vitess_client = vitess_client

    @property
    def healthy_connection(self) -> bool:
        return True

    def read_revision(self, entity_id: str, revision_id: int) -> MagicMock:
        from models.data.infrastructure.s3 import S3RevisionData

        mock_revision = MagicMock(spec=S3RevisionData)
        key = (entity_id, revision_id)
        if key in self._revision_hashes:
            content_hash = self._revision_hashes[key]
            if content_hash in self._revisions:
                mock_revision.revision = self._revisions[content_hash].get(
                    "revision", {}
                )
            else:
                mock_revision.revision = {}
        else:
            mock_revision.revision = {
                "state": {
                    "is_semi_protected": False,
                    "is_locked": False,
                    "is_archived": False,
                    "is_dangling": False,
                    "is_mass_edit_protected": False,
                }
            }
        return mock_revision

    def read_full_revision(self, entity_id: str, revision_id: int) -> MagicMock:
        return self.read_revision(entity_id, revision_id)

    def disconnect(self) -> None:
        pass

    def store_revision(self, content_hash: int, revision_data: Any) -> None:
        self._revisions[content_hash] = (
            revision_data.model_dump(mode="json")
            if hasattr(revision_data, "model_dump")
            else revision_data
        )
        if self._vitess_client:
            pending_revisions = self._vitess_client.get_pending_revisions()
            for (entity_id, revision_id), hash_val in pending_revisions.items():
                self._revision_hashes[(entity_id, revision_id)] = hash_val
            self._vitess_client.clear_pending_revisions()

    def delete_statement(self, hash_val: int) -> None:
        pass

    def store_term_metadata(self, value: Any, hash_value: int) -> None:
        self._term_metadata[hash_value] = (value, "term")

    def store_sitelink_metadata(self, title: str, hash_value: int) -> None:
        self._term_metadata[hash_value] = (title, "sitelink")

    def load_metadata(self, metadata_type: str, content_hash: int) -> Any:
        if content_hash in self._term_metadata:
            value, _ = self._term_metadata[content_hash]
            from models.data.infrastructure.s3.load_response import StringLoadResponse

            return StringLoadResponse(data=value)
        return None


class MockValidator:
    """Mock validator for contract tests."""

    pass


def create_test_state_handler() -> "TestStateHandler":
    """Factory function to create a TestStateHandler instance."""
    return TestStateHandler()


class TestStateHandler:
    """Test StateHandler that uses mock clients.

    This class mimics the StateHandler interface but uses pre-configured
    mock clients instead of real Vitess/S3 connections.
    """

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self) -> None:
        self._vitess_client = MockVitessClient()
        self._s3_client = MockS3Client()
        self._vitess_client.set_s3_client(self._s3_client)
        self._s3_client.set_vitess_client(self._vitess_client)
        self._validator = MockValidator()
        self._settings = MagicMock()
        self._vitess_config = MagicMock()
        self.cached_vitess_client: MockVitessClient | None = None
        self.cached_s3_client: MockS3Client | None = None
        self.cached_enumeration_service: Any = None
        self.entity_change_stream_producer = None

    @property
    def settings(self) -> Any:
        return self._settings

    @property
    def vitess_client(self) -> MockVitessClient:
        if self.cached_vitess_client is None:
            self.cached_vitess_client = self._vitess_client
        return self.cached_vitess_client

    @property
    def s3_client(self) -> MockS3Client:
        if self.cached_s3_client is None:
            self.cached_s3_client = self._s3_client
        return self.cached_s3_client

    @property
    def validator(self) -> Any:
        return self._validator

    @property
    def vitess_config(self) -> Any:
        return self._vitess_config

    @property
    def enumeration_service(self) -> Any:
        if self.cached_enumeration_service is None:
            from models.rest_api.entitybase.v1.services.enumeration_service import (
                EnumerationService,
            )

            class MockEnumerationServiceClass(EnumerationService):
                """Mock EnumerationService that inherits from real class."""

                def __init__(self, **data: Any) -> None:
                    super().__init__(**data)
                    self._mock_mode = True

                def get_next_id(self, entity_type: str) -> int:
                    return 1

                def get_next_entity_id(self, entity_type: str) -> str:
                    """Get the next available entity ID for the given entity type."""
                    type_mapping = {
                        "item": "Q",
                        "property": "P",
                        "lexeme": "L",
                        "entityschema": "E",
                    }
                    if entity_type not in type_mapping:
                        from models.rest_api.utils import raise_validation_error

                        raise_validation_error(
                            f"Unsupported entity type: {entity_type}"
                        )
                    return f"{type_mapping[entity_type]}1"

                @property
                def range_manager(self) -> Any:
                    return MagicMock()

            self.cached_enumeration_service = MockEnumerationServiceClass(
                worker_id="test", vitess_client=self._vitess_client
            )
        return self.cached_enumeration_service

    def disconnect(self) -> None:
        if self._vitess_client:
            self._vitess_client.disconnect()
        if self._s3_client:
            self._s3_client.disconnect()
