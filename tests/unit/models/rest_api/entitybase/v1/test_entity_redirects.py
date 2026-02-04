from typing import Any, cast
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType
from models.data.rest_api.v1.entitybase.request import (
    EntityRedirectRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityRedirectResponse,
    EntityResponse,
)


# noinspection PyUnusedLocal
class MockVitessClient:
    """Mock Vitess client for testing without database"""

    def __init__(self) -> None:
        self.resolved_ids: dict[str, int] = {}
        self.redirects: dict[int, int] = {}
        self.redirects_to: dict[str, str | None] = {}
        self.deleted_entities: set[str] = set()
        self.locked_entities: set[str] = set()
        self.archived_entities: set[str] = set()
        self._internal_to_entity_id: dict[int, str] = {}

    def resolve_id(self, entity_id: str) -> int | None:
        if entity_id in self.resolved_ids:
            internal_id = self.resolved_ids[entity_id]
            self._internal_to_entity_id[internal_id] = entity_id
            return internal_id
        return None

    @staticmethod
    def get_incoming_redirects(entity_id: str) -> list[str]:
        return []  # Mock implementation returning empty list

    def get_redirect_target(self, entity_id: str) -> str | None:
        return self.redirects_to.get(entity_id, None)

    def is_entity_deleted(self, entity_id: str) -> bool:
        return entity_id in self.deleted_entities

    def is_entity_locked(self, entity_id: str) -> bool:
        return entity_id in self.locked_entities

    def is_entity_archived(self, entity_id: str) -> bool:
        return entity_id in self.archived_entities

    @staticmethod
    def get_head(entity_id: int) -> int:
        """Get current head revision for entity (for testing)"""
        return 42

    def create_redirect(
        self,
        redirect_from_entity_id: str,
        redirect_to_entity_id: str,
        created_by: str = "rest-api",
    ) -> None:
        redirect_from_internal_id = self.resolved_ids.get(redirect_from_entity_id)
        redirect_to_internal_id = self.resolved_ids.get(redirect_to_entity_id)

        if not redirect_from_internal_id:
            raise ValueError(f"Source entity {redirect_from_entity_id} not found")
        if not redirect_to_internal_id:
            raise ValueError(f"Target entity {redirect_to_entity_id} not found")

        self.redirects[redirect_from_internal_id] = redirect_to_internal_id
        self.redirects_to[redirect_from_entity_id] = redirect_to_entity_id

    def set_redirect_target(
        self,
        entity_id: str,
        redirects_to_entity_id: str | None,
    ) -> None:
        self.redirects_to[entity_id] = redirects_to_entity_id


class MockS3Client:
    """Mock S3 client for testing without S3"""

    def __init__(self) -> None:
        self.written_revisions: dict[int, dict[str, Any]] = {}

    def read_revision(self, entity_id: str, revision_id: int) -> dict[str, Any]:
        return self.written_revisions.get(
            revision_id,
            {
                "revision_id": revision_id,
                "data": {
                    "id": entity_id,
                    "type": "item",
                    "labels": {},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                    "sitelinks": {},
                },
            },
        )

    # noinspection PyUnusedLocal
    def write_entity_revision(
        self,
        data: dict[str, Any],
    ) -> int:
        revision_id = data["revision_id"]
        self.written_revisions[revision_id] = data
        return cast(int, revision_id)

    def read_full_revision(self, entity_id: str, revision_id: int) -> dict:
        """Read S3 object and return parsed full revision JSON (matches real client)"""
        return self.written_revisions.get(
            revision_id,
            {
                "schema_version": "1.0.0",
                "revision_id": revision_id,
                "created_at": "2024-01-01T00:00:00Z",
                "created_by": "rest-api",
                "is_mass_edit": False,
                "edit_type": "",
                "entity_type": "item",
                "is_semi_protected": False,
                "is_locked": False,
                "is_archived": False,
                "is_dangling": False,
                "is_mass_edit_protected": False,
                "is_deleted": False,
                "is_redirect": False,
                "data": {
                    "id": entity_id,
                    "type": "item",
                    "labels": {},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                    "sitelinks": {},
                },
            },
        )


class RedirectService:
    """Mock RedirectService for testing"""

    def __init__(
        self, s3_client: MockS3Client, vitess_client: MockVitessClient
    ) -> None:
        self.s3 = s3_client
        self.vitess = vitess_client

    def create_redirect(self, request: EntityRedirectRequest) -> EntityRedirectResponse:
        vitess = self.vitess
        s3 = self.s3

        from_internal_id = vitess.resolve_id(request.redirect_from_id)
        to_internal_id = vitess.resolve_id(request.redirect_to_id)

        print(
            f"DEBUG: from_id={request.redirect_from_id}, to_id={request.redirect_to_id}"
        )
        print(
            f"DEBUG: from_internal_id={from_internal_id}, to_internal_id={to_internal_id}"
        )

        if from_internal_id is None:
            raise HTTPException(status_code=404, detail="Source entity not found")
        if to_internal_id is None:
            raise HTTPException(status_code=404, detail="Target entity not found")

        if from_internal_id == to_internal_id:
            raise HTTPException(status_code=400, detail="Cannot redirect to self")

        existing_target = vitess.get_redirect_target(request.redirect_to_id)
        if existing_target is not None:
            raise HTTPException(status_code=409, detail="Redirect already exists")

        if vitess.is_entity_deleted(request.redirect_from_id):
            raise HTTPException(
                status_code=423, detail="Source entity has been deleted"
            )
        if vitess.is_entity_deleted(request.redirect_to_id):
            raise HTTPException(
                status_code=423, detail="Target entity has been deleted"
            )

        if vitess.is_entity_locked(request.redirect_to_id) or vitess.is_entity_archived(
            request.redirect_to_id
        ):
            raise HTTPException(
                status_code=423, detail="Target entity is locked or archived"
            )

        redirect_revision_data = {
            "schema_version": "1.1.0",
            "redirects_to": request.redirect_to_id,
            "entity": {
                "id": request.redirect_from_id,
                "type": "item",
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "claims": {},
                "sitelinks": {},
            },
        }

        redirect_revision_data["revision_id"] = 1
        redirect_revision_id = s3.write_entity_revision(data=redirect_revision_data)

        vitess.create_redirect(
            redirect_from_entity_id=request.redirect_from_id,
            redirect_to_entity_id=request.redirect_to_id,
            created_by=request.created_by,
        )

        vitess.set_redirect_target(
            entity_id=request.redirect_from_id,
            redirects_to_entity_id=request.redirect_to_id,
        )

        from datetime import datetime, timezone

        return EntityRedirectResponse(
            redirect_from_id=request.redirect_from_id,
            redirect_to_id=request.redirect_to_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            revision_id=redirect_revision_id,
        )

    def revert_redirect(
        self, entity_id: str, revert_to_revision_id: int, edit_headers
    ) -> EntityResponse:
        vitess = self.vitess
        s3 = self.s3

        internal_id = vitess.resolve_id(entity_id)
        if internal_id is None:
            raise HTTPException(status_code=404, detail="Entity not found")

        current_redirect_target = vitess.get_redirect_target(entity_id)

        if current_redirect_target is None:
            raise HTTPException(status_code=404, detail="Entity is not a redirect")

        if vitess.is_entity_deleted(entity_id):
            raise HTTPException(status_code=423, detail="Entity has been deleted")

        if vitess.is_entity_locked(entity_id) or vitess.is_entity_archived(entity_id):
            raise HTTPException(status_code=423, detail="Entity is locked or archived")

        target_revision = s3.read_full_revision(entity_id, revert_to_revision_id)
        target_data = target_revision

        new_revision_data = {
            "schema_version": "1.1.0",
            "redirects_to": None,
            "entity": target_data.get("data", target_data),
        }

        new_revision_data["revision_id"] = 2
        new_revision_id = s3.write_entity_revision(data=new_revision_data)

        vitess.set_redirect_target(
            entity_id=entity_id,
            redirects_to_entity_id=None,
        )

        return EntityResponse(
            id=entity_id,
            rev_id=new_revision_id,
            data=new_revision_data["entity"],
            state=EntityState(),
        )


@pytest.fixture
def redirect_service() -> RedirectService:
    """Fixture providing RedirectService with mock clients"""
    vitess = MockVitessClient()
    s3 = MockS3Client()

    # Set up default Q42 entity for tests
    vitess.resolved_ids["Q42"] = 42

    return RedirectService(s3, vitess)


def test_revert_redirect_success(redirect_service: RedirectService) -> None:
        """Test successful redirect revert"""
        vitess = redirect_service.vitess
        s3 = redirect_service.s3

        vitess.resolved_ids["Q100"] = 100
        vitess.resolved_ids["Q42"] = 42
        vitess.set_redirect_target("Q100", "Q42")
        s3.written_revisions[1] = {
            "revision_id": 1,
            "data": {
                "id": "Q100",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Original Label"}},
                "descriptions": {"en": {"language": "en", "value": "Original Description"}},
                "claims": {},
                "sitelinks": {},
            },
        }

        edit_headers = Mock()
        edit_headers.x_edit_summary = "Test revert"
        edit_headers.x_user_id = 1

        response = redirect_service.revert_redirect(
            entity_id="Q100", revert_to_revision_id=1, edit_headers=edit_headers
        )

        assert response.id == "Q100"
        assert response.revision_id == 2
        assert response.entity_data["id"] == "Q100"
        assert response.entity_data["labels"]["en"]["value"] == "Original Label"

        assert vitess.get_redirect_target("Q100") is None


def test_revert_redirect_entity_not_redirect(redirect_service: RedirectService) -> None:
        """Test that reverting a non-redirect entity raises 404"""
        vitess = redirect_service.vitess

        vitess.resolved_ids["Q100"] = 100

        edit_headers = Mock()
        edit_headers.x_edit_summary = "Test revert"
        edit_headers.x_user_id = 1

        from fastapi import HTTPException

        try:
            redirect_service.revert_redirect(
                entity_id="Q100", revert_to_revision_id=1, edit_headers=edit_headers
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            assert "not a redirect" in e.detail.lower()


def test_revert_redirect_entity_deleted(redirect_service: RedirectService) -> None:
        """Test that reverting a deleted entity raises 423"""
        vitess = redirect_service.vitess

        vitess.resolved_ids["Q100"] = 100
        vitess.resolved_ids["Q42"] = 42
        vitess.set_redirect_target("Q100", "Q42")  # Set up as redirect first
        vitess.deleted_entities.add("Q100")

        edit_headers = Mock()
        edit_headers.x_edit_summary = "Test revert"
        edit_headers.x_user_id = 1

        from fastapi import HTTPException

        try:
            redirect_service.revert_redirect(
                entity_id="Q100", revert_to_revision_id=1, edit_headers=edit_headers
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 423
            assert "deleted" in e.detail.lower()


def test_revert_redirect_entity_locked(redirect_service: RedirectService) -> None:
        """Test that reverting a locked entity raises 423"""
        vitess = redirect_service.vitess

        vitess.resolved_ids["Q100"] = 100
        vitess.resolved_ids["Q42"] = 42
        vitess.set_redirect_target("Q100", "Q42")  # Set up as redirect first
        vitess.locked_entities.add("Q100")

        edit_headers = Mock()
        edit_headers.x_edit_summary = "Test revert"
        edit_headers.x_user_id = 1

        from fastapi import HTTPException

        try:
            redirect_service.revert_redirect(
                entity_id="Q100", revert_to_revision_id=1, edit_headers=edit_headers
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 423
            assert "locked" in e.detail.lower()


def test_revert_redirect_entity_archived(redirect_service: RedirectService) -> None:
        """Test that reverting an archived entity raises 423"""
        vitess = redirect_service.vitess

        vitess.resolved_ids["Q100"] = 100
        vitess.resolved_ids["Q42"] = 42
        vitess.set_redirect_target("Q100", "Q42")  # Set up as redirect first
        vitess.archived_entities.add("Q100")

        edit_headers = Mock()
        edit_headers.x_edit_summary = "Test revert"
        edit_headers.x_user_id = 1

        from fastapi import HTTPException

        try:
            redirect_service.revert_redirect(
                entity_id="Q100", revert_to_revision_id=1, edit_headers=edit_headers
            )
            assert False, "Should have raised HTTPException"
        except HTTPException as e:
            assert e.status_code == 423
            assert "archived" in e.detail.lower()
