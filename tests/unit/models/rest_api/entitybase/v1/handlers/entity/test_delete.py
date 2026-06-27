"""Unit tests for delete handler."""

from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from models.data.infrastructure.s3.enums import DeleteType
from models.data.rest_api.v1.entitybase.request.entity.entity_delete_request import (
    EntityDeleteRequest,
)
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.entitybase.v1.handlers.entity.delete import EntityDeleteHandler


def _make_protection_info(
    is_archived: bool = False, is_locked: bool = False
) -> MagicMock:
    """Create a protection info mock that works with both attr and dict access."""
    mock_info = MagicMock()
    mock_info.is_archived = is_archived
    mock_info.get.side_effect = lambda key, default=None: {
        "is_locked": is_locked,
    }.get(key, default)
    return mock_info


def _make_current_revision(statements: list | None = None) -> MagicMock:
    """Create a current revision mock for delete operations."""
    return MagicMock(
        revision={
            "entity_type": "item",
            "properties": [],
            "property_counts": {},
            "statements": statements or [],
            "sitelinks": {},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
            "is_semi_protected": False,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": False,
        }
    )


class TestEntityDeleteHandler:
    """Unit tests for EntityDeleteHandler."""

    @pytest.mark.asyncio
    async def test_soft_delete_success(self) -> None:
        """Test successful soft delete of an entity."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = MagicMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.get_head.return_value = 5
        mock_mysql.create_revision.return_value = True
        mock_mysql.entity_repository.get_protection_info.return_value = (
            _make_protection_info()
        )
        mock_s3.read_revision.return_value = _make_current_revision()

        handler = EntityDeleteHandler(state=mock_state)

        request = EntityDeleteRequest(delete_type=DeleteType.SOFT)
        edit_headers = EditHeaders(x_edit_summary="Soft delete test")

        response = await handler.delete_entity("Q42", request, edit_headers, user_id=123)

        assert response.id == "Q42"
        assert response.revision_id == 6
        assert response.is_deleted is True
        assert response.deletion_status == "soft_deleted"
        mock_mysql.create_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_hard_delete_success(self) -> None:
        """Test successful hard delete of an entity with reference cleanup."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = MagicMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.get_head.return_value = 3
        mock_mysql.create_revision.return_value = True
        mock_mysql.entity_repository.get_protection_info.return_value = (
            _make_protection_info()
        )
        mock_s3.read_revision.return_value = _make_current_revision(
            statements=[1001, 1002]
        )

        handler = EntityDeleteHandler(state=mock_state)

        request = EntityDeleteRequest(delete_type=DeleteType.HARD)
        edit_headers = EditHeaders(x_edit_summary="Hard delete test")

        response = await handler.delete_entity("Q42", request, edit_headers, user_id=456)

        assert response.id == "Q42"
        assert response.revision_id == 4
        assert response.is_deleted is True
        assert response.deletion_status == "hard_deleted"
        mock_mysql.create_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_entity_not_found(self) -> None:
        """Test delete when entity doesn't exist."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = MagicMock()

        mock_mysql.entity_exists.return_value = False

        handler = EntityDeleteHandler(state=mock_state)
        request = EntityDeleteRequest(delete_type=DeleteType.SOFT)
        edit_headers = EditHeaders(x_edit_summary="Delete test")

        with pytest.raises(Exception):
            await handler.delete_entity("Q999", request, edit_headers, user_id=123)


    @pytest.mark.asyncio
    async def test_delete_entity_already_deleted(self) -> None:
        """Test delete when entity is already deleted."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = MagicMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = True

        handler = EntityDeleteHandler(state=mock_state)
        request = EntityDeleteRequest(delete_type=DeleteType.SOFT)
        edit_headers = EditHeaders(x_edit_summary="Delete test")

        with pytest.raises(Exception):
            await handler.delete_entity("Q42", request, edit_headers, user_id=123)


    @pytest.mark.asyncio
    async def test_delete_s3_not_found(self) -> None:
        """Test delete when S3 revision is not found."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.get_head.return_value = 5
        mock_mysql.entity_repository.get_protection_info.return_value = (
            _make_protection_info()
        )
        mock_s3.read_revision.side_effect = S3NotFoundError("Object not found")

        handler = EntityDeleteHandler(state=mock_state)
        request = EntityDeleteRequest(delete_type=DeleteType.SOFT)
        edit_headers = EditHeaders(x_edit_summary="Delete test")

        with pytest.raises(Exception):
            await handler.delete_entity("Q42", request, edit_headers, user_id=123)


    @pytest.mark.asyncio
    async def test_delete_conflict(self) -> None:
        """Test delete when revision creation fails due to conflict."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.get_head.return_value = 5
        mock_mysql.entity_repository.get_protection_info.return_value = (
            _make_protection_info()
        )
        mock_mysql.create_revision.side_effect = [False]
        mock_s3.read_revision.return_value = _make_current_revision()

        handler = EntityDeleteHandler(state=mock_state)
        request = EntityDeleteRequest(delete_type=DeleteType.SOFT)
        edit_headers = EditHeaders(x_edit_summary="Delete test")

        with pytest.raises(Exception):
            await handler.delete_entity("Q42", request, edit_headers, user_id=123)


    @pytest.mark.asyncio
    async def test_delete_mysql_not_initialized(self) -> None:
        """Test delete when Sql client is not initialized."""
        mock_state = MagicMock()
        mock_state.mysql_client = None
        mock_state.s3_client = MagicMock()

        handler = EntityDeleteHandler(state=mock_state)
        request = EntityDeleteRequest(delete_type=DeleteType.SOFT)
        edit_headers = EditHeaders(x_edit_summary="Delete test")

        with pytest.raises(Exception):
            await handler.delete_entity("Q42", request, edit_headers, user_id=123)


    @pytest.mark.asyncio
    async def test_delete_s3_not_initialized(self) -> None:
        """Test delete when S3 client is not initialized."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = None

        handler = EntityDeleteHandler(state=mock_state)

        request = EntityDeleteRequest(delete_type=DeleteType.SOFT)
        edit_headers = EditHeaders(x_edit_summary="Delete test")

        with pytest.raises(Exception):
            await handler.delete_entity("Q42", request, edit_headers, user_id=123)
