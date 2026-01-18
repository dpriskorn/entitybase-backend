"""Unit tests for EntityHandler.patch_labels."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from models.rest_api.entitybase.handlers.entity.base import EntityHandler
from models.rest_api.entitybase.request.entity.patch import LabelPatchRequest, JsonPatchOperation
from models.common import OperationResult


class TestPatchLabels:
    @pytest.fixture
    def handler(self):
        return EntityHandler()

    @pytest.fixture
    def mock_vitess_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_s3_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_read_handler(self):
        mock = MagicMock()
        mock.get_entity.return_value = MagicMock(
            entity_data={"labels": {"en": "English"}},
            revision_id=100,
            entity_type="item",
            state=MagicMock(sp=False, locked=False, archived=False, dangling=False, mep=False)
        )
        return mock

    @pytest.fixture
    def patch_request_add(self):
        return LabelPatchRequest(
            edit_summary="Add French label",
            patch=JsonPatchOperation(op="add", path="/labels/fr", value="Français")
        )

    @pytest.fixture
    def patch_request_replace(self):
        return LabelPatchRequest(
            edit_summary="Update English label",
            patch=JsonPatchOperation(op="replace", path="/labels/en", value="Updated English")
        )

    @pytest.fixture
    def patch_request_remove(self):
        return LabelPatchRequest(
            edit_summary="Remove English label",
            patch=JsonPatchOperation(op="remove", path="/labels/en")
        )

    @pytest.mark.asyncio
    async def test_patch_labels_add_success(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler, patch_request_add
    ):
        """Test successful add operation."""
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            mock_result = OperationResult(success=True, data={"revision_id": 101})
            handler._create_and_store_revision = AsyncMock(return_value=mock_result)

            result = await handler.patch_labels(
                "Q42", patch_request_add, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is True
            assert result.data["revision_id"] == 101
            handler._create_and_store_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_patch_labels_replace_success(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler, patch_request_replace
    ):
        """Test successful replace operation."""
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            mock_result = OperationResult(success=True, data={"revision_id": 101})
            handler._create_and_store_revision = AsyncMock(return_value=mock_result)

            result = await handler.patch_labels(
                "Q42", patch_request_replace, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is True
            handler._create_and_store_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_patch_labels_remove_success(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler, patch_request_remove
    ):
        """Test successful remove operation."""
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            mock_result = OperationResult(success=True, data={"revision_id": 101})
            handler._create_and_store_revision = AsyncMock(return_value=mock_result)

            result = await handler.patch_labels(
                "Q42", patch_request_remove, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is True
            handler._create_and_store_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_patch_labels_invalid_path(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler
    ):
        """Test invalid path (not starting with /labels/)."""
        request = LabelPatchRequest(
            edit_summary="Invalid path",
            patch=JsonPatchOperation(op="add", path="/invalid/en", value="Test")
        )
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            result = await handler.patch_labels(
                "Q42", request, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is False
            assert "Path must start with /labels/" in result.error

    @pytest.mark.asyncio
    async def test_patch_labels_add_existing_label(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler
    ):
        """Test adding a label that already exists."""
        request = LabelPatchRequest(
            edit_summary="Add existing label",
            patch=JsonPatchOperation(op="add", path="/labels/en", value="New English")
        )
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            result = await handler.patch_labels(
                "Q42", request, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is False
            assert "already exists" in result.error

    @pytest.mark.asyncio
    async def test_patch_labels_replace_nonexistent_label(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler
    ):
        """Test replacing a label that doesn't exist."""
        request = LabelPatchRequest(
            edit_summary="Replace nonexistent label",
            patch=JsonPatchOperation(op="replace", path="/labels/de", value="German")
        )
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            result = await handler.patch_labels(
                "Q42", request, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is False
            assert "does not exist" in result.error

    @pytest.mark.asyncio
    async def test_patch_labels_remove_nonexistent_label(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler
    ):
        """Test removing a label that doesn't exist."""
        request = LabelPatchRequest(
            edit_summary="Remove nonexistent label",
            patch=JsonPatchOperation(op="remove", path="/labels/de")
        )
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            result = await handler.patch_labels(
                "Q42", request, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is False
            assert "does not exist" in result.error

    @pytest.mark.asyncio
    async def test_patch_labels_unsupported_operation(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler
    ):
        """Test unsupported operation."""
        request = LabelPatchRequest(
            edit_summary="Unsupported op",
            patch=JsonPatchOperation(op="move", path="/labels/en", value="/labels/new")
        )
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            result = await handler.patch_labels(
                "Q42", request, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is False
            assert "Unsupported operation" in result.error

    @pytest.mark.asyncio
    async def test_patch_labels_entity_not_found(
        self, handler, mock_vitess_client, mock_s3_client, patch_request_add
    ):
        """Test when entity fetch fails."""
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler") as mock_read_class:
            mock_read_class.return_value.get_entity.side_effect = Exception("Entity not found")

            result = await handler.patch_labels(
                "Q42", patch_request_add, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is False
            assert "Failed to fetch entity" in result.error

    @pytest.mark.asyncio
    async def test_patch_labels_revision_creation_failure(
        self, handler, mock_vitess_client, mock_s3_client, mock_read_handler, patch_request_add
    ):
        """Test when revision creation fails."""
        with patch("models.rest_api.entitybase.handlers.entity.base.EntityReadHandler", return_value=mock_read_handler):
            mock_result = OperationResult(success=False, error="Revision failed")
            handler._create_and_store_revision = AsyncMock(return_value=mock_result)

            result = await handler.patch_labels(
                "Q42", patch_request_add, mock_vitess_client, mock_s3_client, user_id=123
            )

            assert result.success is False
            assert result.error == "Revision failed"