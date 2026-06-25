"""Unit tests for EntityUpdateTermsMixin."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from models.rest_api.entitybase.v1.handlers.entity.update_terms import (
    EntityUpdateTermsMixin,
    TermTransactionContext,
)


class TestEntityUpdateTermsMixin:
    """Unit tests for EntityUpdateTermsMixin._decrement_term_ref_count."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_vitess, mock_s3_client

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_handles_none_data(
        self, mock_terms_repo_class
    ) -> None:
        """Test handling when result.data is None - treats as orphaned (deletes)."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = None
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        mock_terms_repo.decrement_ref_count.assert_called_once_with(12345)

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_deletes_when_zero(
        self, mock_terms_repo_class
    ) -> None:
        """Test that term is Vitess and S3 deleted when ref_count hits 0."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = 0
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        mock_terms_repo.decrement_ref_count.assert_called_once_with(12345)
        mock_terms_repo.delete_term.assert_called_once_with(12345)
        mock_s3.delete_metadata.assert_called()

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_handles_failure(
        self, mock_terms_repo_class
    ) -> None:
        """Test graceful failure handling when decrement fails."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "DB error"
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        mock_terms_repo.decrement_ref_count.assert_called_once_with(12345)
        mock_terms_repo.delete_term.assert_not_called()
        mock_s3.delete_metadata.assert_not_called()

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_deletes_all_metadata_types(
        self, mock_terms_repo_class
    ) -> None:
        """Test that all three metadata types are cleaned up when ref_count hits 0."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = 0
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        assert mock_s3.delete_metadata.call_count == 3


class TestUpdateLabelErrors:
    """Unit tests for EntityUpdateTermsMixin.update_label error handling."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_update_label_language_mismatch(self) -> None:
        """Test that language mismatch between request and path raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            TermUpdateContext,
        )
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        context = TermUpdateContext(language="en", language_code="de", value="Test")
        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_label("Q1", context, edit_headers)

        assert exc_info.value.status_code == 400
        assert "does not match" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_label_invalid_entity_id(self) -> None:
        """Test that invalid entity ID raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            TermUpdateContext,
        )
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        context = TermUpdateContext(language="en", language_code="en", value="Test")
        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_label("invalid", context, edit_headers)

        assert exc_info.value.status_code == 400
        assert "Invalid entity ID format" in exc_info.value.detail


class TestDeleteLabelErrors:
    """Unit tests for EntityUpdateTermsMixin.delete_label error handling."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_delete_label_invalid_entity_id(self) -> None:
        """Test that invalid entity ID raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_label("invalid", "en", edit_headers)

        assert exc_info.value.status_code == 400
        assert "Invalid entity ID format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_label_entity_deleted(self) -> None:
        """Test that deleting label on deleted entity raises 410."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_label("Q1", "en", edit_headers)

        assert exc_info.value.status_code == 410
        assert "Entity deleted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_label_entity_locked(self) -> None:
        """Test that deleting label on locked entity raises 423."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_label("Q1", "en", edit_headers)

        assert exc_info.value.status_code == 423
        assert "Entity locked" in exc_info.value.detail


class TestUpdateDescriptionErrors:
    """Unit tests for EntityUpdateTermsMixin.update_description error handling."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_update_description_language_mismatch(self) -> None:
        """Test that language mismatch between request and path raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            TermUpdateContext,
        )
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        context = TermUpdateContext(language="en", language_code="de", value="Test")
        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_description("Q1", context, edit_headers)

        assert exc_info.value.status_code == 400
        assert "does not match" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_description_invalid_entity_id(self) -> None:
        """Test that invalid entity ID raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            TermUpdateContext,
        )
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        context = TermUpdateContext(language="en", language_code="en", value="Test")
        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_description("invalid", context, edit_headers)

        assert exc_info.value.status_code == 400
        assert "Invalid entity ID format" in exc_info.value.detail


class TestDeleteDescriptionErrors:
    """Unit tests for EntityUpdateTermsMixin.delete_description error handling."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_delete_description_invalid_entity_id(self) -> None:
        """Test that invalid entity ID raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_description("invalid", "en", edit_headers)

        assert exc_info.value.status_code == 400
        assert "Invalid entity ID format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_description_entity_deleted(self) -> None:
        """Test that deleting description on deleted entity raises 410."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_description("Q1", "en", edit_headers)

        assert exc_info.value.status_code == 410
        assert "Entity deleted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_description_entity_locked(self) -> None:
        """Test that deleting description on locked entity raises 423."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_description("Q1", "en", edit_headers)

        assert exc_info.value.status_code == 423
        assert "Entity locked" in exc_info.value.detail


class TestUpdateAliasesErrors:
    """Unit tests for EntityUpdateTermsMixin.update_aliases error handling."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_update_aliases_invalid_entity_id(self) -> None:
        """Test that invalid entity ID raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.update_aliases("invalid", "en", ["alias"], edit_headers)

        assert exc_info.value.status_code == 400
        assert "Invalid entity ID format" in exc_info.value.detail


class TestAddAliasErrors:
    """Unit tests for EntityUpdateTermsMixin.add_alias error handling."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_add_alias_invalid_entity_id(self) -> None:
        """Test that invalid entity ID raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.add_alias("invalid", "en", "alias", edit_headers)

        assert exc_info.value.status_code == 400
        assert "Invalid entity ID format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_add_alias_entity_deleted(self) -> None:
        """Test that adding alias to deleted entity raises 410."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.add_alias("Q1", "en", "alias", edit_headers)

        assert exc_info.value.status_code == 410
        assert "Entity deleted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_add_alias_entity_locked(self) -> None:
        """Test that adding alias to locked entity raises 423."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.add_alias("Q1", "en", "alias", edit_headers)

        assert exc_info.value.status_code == 423
        assert "Entity locked" in exc_info.value.detail


class TestDeleteAliasesErrors:
    """Unit tests for EntityUpdateTermsMixin.delete_aliases error handling."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_delete_aliases_invalid_entity_id(self) -> None:
        """Test that invalid entity ID raises 400."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_aliases("invalid", "en", edit_headers)

        assert exc_info.value.status_code == 400
        assert "Invalid entity ID format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_aliases_entity_deleted(self) -> None:
        """Test that deleting aliases on deleted entity raises 410."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_aliases("Q1", "en", edit_headers)

        assert exc_info.value.status_code == 410
        assert "Entity deleted" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_delete_aliases_entity_locked(self) -> None:
        """Test that deleting aliases on locked entity raises 423."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = True

        edit_headers = EditHeaders(x_edit_summary="test", x_user_id="0")

        with pytest.raises(HTTPException) as exc_info:
            await mixin.delete_aliases("Q1", "en", edit_headers)

        assert exc_info.value.status_code == 423
        assert "Entity locked" in exc_info.value.detail


class TestDeleteAliasesSuccess:
    """Unit tests for EntityUpdateTermsMixin.delete_aliases success."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mixin = EntityUpdateTermsMixin(state=mock_state)
        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_delete_aliases_success(self) -> None:
        """Test deleting all aliases successfully."""
        from models.data.infrastructure.s3.enums import EntityType
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data.revision = {
            "hashes": {"aliases": {"en": [111, 222]}},
        }

        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            with patch(
                "models.rest_api.entitybase.v1.handlers.entity.update_terms.EntityReadHandler",
                return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity)),
            ):
                with patch(
                    "models.rest_api.entitybase.v1.handlers.entity.update_terms.infer_entity_type_from_id",
                    return_value=EntityType.ITEM,
                ):
                    result = await mixin.delete_aliases(
                        "Q1", "en", EditHeaders(x_edit_summary="test", x_user_id="0")
                    )

                    assert result == mock_response

    @pytest.mark.asyncio
    async def test_delete_aliases_idempotent(self) -> None:
        """Test delete_aliases returns entity when language not in aliases."""
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data.revision = {
            "hashes": {"aliases": {"fr": [333]}},
        }

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_terms.EntityReadHandler",
            return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity)),
        ):
            with patch(
                "models.rest_api.entitybase.v1.handlers.entity.update_terms.infer_entity_type_from_id",
                return_value=MagicMock(),
            ):
                result = await mixin.delete_aliases(
                    "Q1", "en", EditHeaders(x_edit_summary="test", x_user_id="0")
                )

                assert result == mock_entity


class TestAddAliasSuccess:
    """Unit tests for EntityUpdateTermsMixin.add_alias success path."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mixin = EntityUpdateTermsMixin(state=mock_state)
        return mixin, mock_state

    @pytest.mark.asyncio
    async def test_add_alias_duplicate(self) -> None:
        """Test adding duplicate alias raises 409."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.enums import EntityType
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data.revision = {
            "hashes": {"aliases": {"en": [12345]}},
        }

        with patch(
            "models.internal_representation.metadata_extractor.MetadataExtractor"
        ) as MockExtractor:
            MockExtractor.hash_string.return_value = 12345

            with patch(
                "models.rest_api.entitybase.v1.handlers.entity.update_terms.EntityReadHandler",
                return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity)),
            ):
                with patch(
                    "models.rest_api.entitybase.v1.handlers.entity.update_terms.infer_entity_type_from_id",
                    return_value=EntityType.ITEM,
                ):
                    with pytest.raises(HTTPException) as exc_info:
                        await mixin.add_alias(
                            "Q1",
                            "en",
                            "alias",
                            EditHeaders(x_edit_summary="test", x_user_id="0"),
                        )

                    assert exc_info.value.status_code == 409
                    assert "already exists" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_add_alias_success_with_vitess_config(self) -> None:
        """Test add_alias success with vitess_config set."""
        from models.data.infrastructure.s3.enums import EntityType
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_config = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data.revision = {
            "hashes": {"aliases": {"en": []}},
        }

        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.internal_representation.metadata_extractor.MetadataExtractor"
        ) as MockExtractor:
            MockExtractor.hash_string.return_value = 99999

            with patch(
                "models.infrastructure.vitess.repositories.terms.TermsRepository"
            ) as MockTermsRepo:
                mock_terms_repo = MagicMock()
                MockTermsRepo.return_value = mock_terms_repo

                with patch(
                    "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
                ) as MockTx:
                    mock_tx = MagicMock()
                    mock_tx.state.vitess_client.get_head.return_value = 2
                    mock_tx.create_revision_with_hashes = AsyncMock(
                        return_value=mock_response
                    )
                    mock_tx.publish_event = AsyncMock()
                    MockTx.return_value = mock_tx

                    with patch(
                        "models.rest_api.entitybase.v1.handlers.entity.update_terms.EntityReadHandler",
                        return_value=MagicMock(
                            get_entity=MagicMock(return_value=mock_entity)
                        ),
                    ):
                        with patch(
                            "models.rest_api.entitybase.v1.handlers.entity.update_terms.infer_entity_type_from_id",
                            return_value=EntityType.ITEM,
                        ):
                            result = await mixin.add_alias(
                                "Q1",
                                "en",
                                "newalias",
                                EditHeaders(x_edit_summary="test", x_user_id="0"),
                            )

                            assert result == mock_response
                            mock_state.s3_client.store_term_metadata.assert_called_once()
                            mock_terms_repo.insert_term.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_alias_success_no_vitess_config(self) -> None:
        """Test add_alias success without vitess_config."""
        from models.data.infrastructure.s3.enums import EntityType
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mixin, mock_state = self._create_mixin_with_mocks()
        mock_state.vitess_client.is_entity_deleted.return_value = False
        mock_state.vitess_client.is_entity_locked.return_value = False
        mock_state.vitess_config = None

        mock_entity = MagicMock()
        mock_entity.entity_data.revision = {
            "hashes": {"aliases": {"en": []}},
        }

        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.internal_representation.metadata_extractor.MetadataExtractor"
        ) as MockExtractor:
            MockExtractor.hash_string.return_value = 77777

            with patch(
                "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
            ) as MockTx:
                mock_tx = MagicMock()
                mock_tx.state.vitess_client.get_head.return_value = 2
                mock_tx.create_revision_with_hashes = AsyncMock(
                    return_value=mock_response
                )
                mock_tx.publish_event = AsyncMock()
                MockTx.return_value = mock_tx

                with patch(
                    "models.rest_api.entitybase.v1.handlers.entity.update_terms.EntityReadHandler",
                    return_value=MagicMock(
                        get_entity=MagicMock(return_value=mock_entity)
                    ),
                ):
                    with patch(
                        "models.rest_api.entitybase.v1.handlers.entity.update_terms.infer_entity_type_from_id",
                        return_value=EntityType.ITEM,
                    ):
                        result = await mixin.add_alias(
                            "Q1",
                            "en",
                            "newalias",
                            EditHeaders(x_edit_summary="test", x_user_id="0"),
                        )

                        assert result == mock_response


class TestExecuteTermAddTransaction:
    """Unit tests for _execute_term_add_transaction."""

    @pytest.mark.asyncio
    async def test_add_transaction_success(self) -> None:
        """Test successful term add transaction."""
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mock_state.vitess_client.user_repository.log_user_activity = AsyncMock(
            return_value=MagicMock(success=True)
        )
        mixin = EntityUpdateTermsMixin(state=mock_state)

        from models.data.infrastructure.s3.enums import EntityType as ET

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )
        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            result = await mixin._execute_term_add_transaction(context)

            assert result == mock_response
            mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_transaction_http_exception(self) -> None:
        """Test term add transaction rolls back on HTTPException."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(
                side_effect=HTTPException(status_code=409, detail="Conflict")
            )
            MockTx.return_value = mock_tx

            with pytest.raises(HTTPException):
                await mixin._execute_term_add_transaction(context)

            mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_transaction_generic_exception(self) -> None:
        """Test term add transaction rolls back on generic exception."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(
                side_effect=ValueError("DB error")
            )
            MockTx.return_value = mock_tx

            with pytest.raises(HTTPException) as exc_info:
                await mixin._execute_term_add_transaction(context)

            assert exc_info.value.status_code == 500
            mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_transaction_user_activity_failure(self) -> None:
        """Test term add transaction logs warning on user activity failure."""
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mock_state.vitess_client.user_repository.log_user_activity = AsyncMock(
            return_value=MagicMock(success=False, error="Log error")
        )
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )
        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            result = await mixin._execute_term_add_transaction(context)

            assert result == mock_response
            mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_transaction_no_user_id(self) -> None:
        """Test term add transaction without user ID skips activity log."""
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id=0),
        )
        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            result = await mixin._execute_term_add_transaction(context)

            assert result == mock_response
            mock_state.vitess_client.user_repository.log_user_activity.assert_not_called()


class TestExecuteTermDeleteTransaction:
    """Unit tests for _execute_term_delete_transaction."""

    @pytest.mark.asyncio
    async def test_delete_transaction_success_with_removed_hashes(self) -> None:
        """Test successful term delete with removed hashes."""
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mock_state.vitess_client.user_repository.log_user_activity = AsyncMock(
            return_value=MagicMock(success=True)
        )
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )
        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            with patch.object(mixin, "_decrement_term_ref_count") as mock_decrement:
                result = await mixin._execute_term_delete_transaction(
                    context, removed_hashes=[12345]
                )

                assert result == mock_response
                mock_decrement.assert_called_once_with(12345)
                mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_transaction_success_no_removed_hashes(self) -> None:
        """Test successful term delete without removed hashes."""
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mock_state.vitess_client.user_repository.log_user_activity = AsyncMock(
            return_value=MagicMock(success=True)
        )
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )
        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            result = await mixin._execute_term_delete_transaction(context)

            assert result == mock_response
            mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_transaction_http_exception(self) -> None:
        """Test term delete transaction rolls back on HTTPException."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(
                side_effect=HTTPException(status_code=409, detail="Conflict")
            )
            MockTx.return_value = mock_tx

            with pytest.raises(HTTPException):
                await mixin._execute_term_delete_transaction(context)

            mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_transaction_generic_exception(self) -> None:
        """Test term delete transaction rolls back on generic exception."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(
                side_effect=ValueError("DB error")
            )
            MockTx.return_value = mock_tx

            with pytest.raises(HTTPException) as exc_info:
                await mixin._execute_term_delete_transaction(context)

            assert exc_info.value.status_code == 500
            mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_transaction_user_activity_failure(self) -> None:
        """Test term delete transaction logs warning on user activity failure."""
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mock_state.vitess_client.user_repository.log_user_activity = AsyncMock(
            return_value=MagicMock(success=False, error="Log error")
        )
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id="0"),
        )
        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            result = await mixin._execute_term_delete_transaction(
                context, removed_hashes=[12345]
            )

            assert result == mock_response
            mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_transaction_no_user_id(self) -> None:
        """Test term delete transaction without user ID skips activity log."""
        from models.data.infrastructure.s3.enums import EntityType as ET
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders

        mock_state = MagicMock()
        mixin = EntityUpdateTermsMixin(state=mock_state)

        context = TermTransactionContext(
            entity_id="Q1",
            entity_type=ET.ITEM,
            updated_hashes={"labels": {}},
            existing_revision={},
            edit_headers=EditHeaders(x_edit_summary="test", x_user_id=0),
        )
        mock_response = MagicMock()
        mock_response.revision_id = 3

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.UpdateTransaction"
        ) as MockTx:
            mock_tx = MagicMock()
            mock_tx.state.vitess_client.get_head.return_value = 2
            mock_tx.create_revision_with_hashes = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            MockTx.return_value = mock_tx

            result = await mixin._execute_term_delete_transaction(context)

            assert result == mock_response
            mock_state.vitess_client.user_repository.log_user_activity.assert_not_called()
