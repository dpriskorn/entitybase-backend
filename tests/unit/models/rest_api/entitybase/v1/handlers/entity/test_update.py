"""Unit tests for EntityUpdateHandler."""

from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler


class TestEntityUpdateHandler:
    """Unit tests for EntityUpdateHandler."""

    # _update_with_transaction tests
    @pytest.mark.asyncio
    async def test_update_with_transaction_success(self) -> None:
        """Test successful update with transaction."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_user_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3
        mock_vitess.user_repository = mock_user_repo

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False
        mock_vitess.get_head.return_value = 2
        mock_user_repo.log_user_activity.return_value = MagicMock(success=True)

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {"labels": {"en": {"language": "en", "value": "Test"}}}

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_response = EntityResponse(
                id="Q42",
                rev_id=3,
                data={"labels": {"en": {"language": "en", "value": "Test"}}}
            )
            mock_update.return_value = mock_response

            result = await mock_update(
                "Q42",
                modified_data,
                MagicMock(),
                EditHeaders(x_user_id=123, x_edit_summary="Test edit"),
            )

            assert result.id == "Q42"
            assert result.rev_id == 3

    @pytest.mark.asyncio
    async def test_update_with_transaction_entity_not_found(self) -> None:
        """Test update when entity doesn't exist (404)."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_vitess.entity_exists.return_value = False

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {}

        with pytest.raises(ValueError):
            await handler._update_with_transaction(
                "Q999",
                modified_data,
                MagicMock(),
                EditHeaders(x_user_id=1, x_edit_summary="Test"),
            )

    @pytest.mark.asyncio
    async def test_update_with_transaction_entity_deleted(self) -> None:
        """Test update when entity is deleted (410)."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = True

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {}

        with pytest.raises(ValueError):
            await handler._update_with_transaction(
                "Q42",
                modified_data,
                MagicMock(),
                EditHeaders(x_user_id=1, x_edit_summary="Test"),
            )

    @pytest.mark.asyncio
    async def test_update_with_transaction_entity_locked(self) -> None:
        """Test update when entity is locked (423)."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = True

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {}

        with pytest.raises(ValueError):
            await handler._update_with_transaction(
                "Q42",
                modified_data,
                MagicMock(),
                EditHeaders(x_user_id=1, x_edit_summary="Test"),
            )

    # update_label tests
    @pytest.mark.asyncio
    async def test_update_label_success(self) -> None:
        """Test updating a label successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"labels": {}, "descriptions": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_response = EntityResponse(
                id="Q42",
                rev_id=2,
                data={"labels": {"en": {"language": "en", "value": "New"}}}
            )
            mock_update.return_value = mock_response

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.update_label(
                        "Q42",
                        "en",
                        "en",
                        "New Label",
                        EditHeaders(x_user_id=1, x_edit_summary="Update label"),
                    )

                    assert mock_update.called

    @pytest.mark.asyncio
    async def test_update_label_language_mismatch(self) -> None:
        """Test update_label when path language doesn't match body language."""
        mock_state = MagicMock()
        handler = EntityUpdateHandler(state=mock_state)

        with pytest.raises(ValueError):
            await handler.update_label(
                "Q42",
                "en",
                "de",  # Mismatch
                "Neues Label",
                EditHeaders(x_user_id=1, x_edit_summary="Update label"),
            )

    @pytest.mark.asyncio
    async def test_update_label_invalid_entity_id(self) -> None:
        """Test update_label with invalid entity ID format."""
        mock_state = MagicMock()
        handler = EntityUpdateHandler(state=mock_state)

        with pytest.raises(ValueError):
            await handler.update_label(
                "INVALID",
                "en",
                "en",
                "Label",
                EditHeaders(x_user_id=1, x_edit_summary="Update label"),
            )

    # delete_label tests
    @pytest.mark.asyncio
    async def test_delete_label_success(self) -> None:
        """Test deleting a label successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"labels": {"en": {"language": "en", "value": "Old"}}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_entity

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.delete_label(
                        "Q42",
                        "en",
                        EditHeaders(x_user_id=1, x_edit_summary="Delete label"),
                    )

                    assert mock_update.called
                    # Verify label was removed from revision data
                    call_args = mock_update.call_args[0]
                    assert "en" not in call_args[1]["labels"]

    @pytest.mark.asyncio
    async def test_delete_label_idempotent(self) -> None:
        """Test delete_label is idempotent when label doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"labels": {"de": {"language": "de", "value": "Test"}}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
            with patch(
                'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
            ):
                result = await handler.delete_label(
                    "Q42",
                    "en",  # Label doesn't exist
                    EditHeaders(x_user_id=1, x_edit_summary="Delete label"),
                )

                # Should return current entity without calling update
                assert result == mock_entity

    # update_description tests
    @pytest.mark.asyncio
    async def test_update_description_success(self) -> None:
        """Test updating a description successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"labels": {}, "descriptions": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_entity

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.update_description(
                        "Q42",
                        "en",
                        "en",
                        "New description",
                        EditHeaders(x_user_id=1, x_edit_summary="Update description"),
                    )

                    assert mock_update.called

    @pytest.mark.asyncio
    async def test_update_description_language_mismatch(self) -> None:
        """Test update_description when path language doesn't match body language."""
        mock_state = MagicMock()
        handler = EntityUpdateHandler(state=mock_state)

        with pytest.raises(ValueError):
            await handler.update_description(
                "Q42",
                "en",
                "de",  # Mismatch
                "Beschreibung",
                EditHeaders(x_user_id=1, x_edit_summary="Update description"),
            )

    @pytest.mark.asyncio
    async def test_update_description_invalid_entity_id(self) -> None:
        """Test update_description with invalid entity ID format."""
        mock_state = MagicMock()
        handler = EntityUpdateHandler(state=mock_state)

        with pytest.raises(ValueError):
            await handler.update_description(
                "INVALID",
                "en",
                "en",
                "Description",
                EditHeaders(x_user_id=1, x_edit_summary="Update description"),
            )

    # delete_description tests
    @pytest.mark.asyncio
    async def test_delete_description_success(self) -> None:
        """Test deleting a description successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {
            "labels": {},
            "descriptions": {"en": {"language": "en", "value": "Old desc"}}
        }

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_entity

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.delete_description(
                        "Q42",
                        "en",
                        EditHeaders(x_user_id=1, x_edit_summary="Delete description"),
                    )

                    assert mock_update.called
                    # Verify description was removed
                    call_args = mock_update.call_args[0]
                    assert "en" not in call_args[1]["descriptions"]

    @pytest.mark.asyncio
    async def test_delete_description_idempotent(self) -> None:
        """Test delete_description is idempotent when description doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"labels": {}, "descriptions": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
            with patch(
                'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
            ):
                result = await handler.delete_description(
                    "Q42",
                    "en",  # Description doesn't exist
                    EditHeaders(x_user_id=1, x_edit_summary="Delete description"),
                )

                assert result == mock_entity

    # update_aliases tests
    @pytest.mark.asyncio
    async def test_update_aliases_success(self) -> None:
        """Test updating aliases successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"labels": {}, "aliases": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_entity

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.update_aliases(
                        "Q42",
                        "en",
                        ["Alias1", "Alias2"],
                        EditHeaders(x_user_id=1, x_edit_summary="Update aliases"),
                    )

                    assert mock_update.called
                    # Verify aliases were converted
                    call_args = mock_update.call_args[0]
                    assert call_args[1]["aliases"]["en"] == [
                        {"value": "Alias1"},
                        {"value": "Alias2"}
                    ]

    @pytest.mark.asyncio
    async def test_update_aliases_invalid_entity_id(self) -> None:
        """Test update_aliases with invalid entity ID format."""
        mock_state = MagicMock()
        handler = EntityUpdateHandler(state=mock_state)

        with pytest.raises(ValueError):
            await handler.update_aliases(
                "INVALID",
                "en",
                ["Alias"],
                EditHeaders(x_user_id=1, x_edit_summary="Update aliases"),
            )

    # update_sitelink tests
    @pytest.mark.asyncio
    async def test_update_sitelink_success(self) -> None:
        """Test updating a sitelink successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"sitelinks": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_entity

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.update_sitelink(
                        "Q42",
                        "enwiki",
                        "Test_Item",
                        ["Q123"],
                        EditHeaders(x_user_id=1, x_edit_summary="Update sitelink"),
                    )

                    assert mock_update.called
                    # Verify sitelink was added
                    call_args = mock_update.call_args[0]
                    assert call_args[1]["sitelinks"]["enwiki"]["title"] == "Test_Item"
                    assert call_args[1]["sitelinks"]["enwiki"]["badges"] == ["Q123"]

    @pytest.mark.asyncio
    async def test_update_sitelink_existing(self) -> None:
        """Test updating an existing sitelink."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {
            "sitelinks": {"enwiki": {"title": "Old", "badges": []}}
        }

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_entity

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.update_sitelink(
                        "Q42",
                        "enwiki",
                        "New_Title",
                        ["Q456"],
                        EditHeaders(x_user_id=1, x_edit_summary="Update sitelink"),
                    )

                    assert mock_update.called

    @pytest.mark.asyncio
    async def test_update_sitelink_invalid_entity_id(self) -> None:
        """Test update_sitelink with invalid entity ID format."""
        mock_state = MagicMock()
        handler = EntityUpdateHandler(state=mock_state)

        with pytest.raises(ValueError):
            await handler.update_sitelink(
                "INVALID",
                "enwiki",
                "Title",
                [],
                EditHeaders(x_user_id=1, x_edit_summary="Update sitelink"),
            )

    # delete_sitelink tests
    @pytest.mark.asyncio
    async def test_delete_sitelink_success(self) -> None:
        """Test deleting a sitelink successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {
            "sitelinks": {"enwiki": {"title": "Test", "badges": []}}
        }

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_update_with_transaction', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_entity

            with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
                with patch(
                    'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                    return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
                ):
                    result = await handler.delete_sitelink(
                        "Q42",
                        "enwiki",
                        EditHeaders(x_user_id=1, x_edit_summary="Delete sitelink"),
                    )

                    assert mock_update.called
                    # Verify sitelink was removed
                    call_args = mock_update.call_args[0]
                    assert "enwiki" not in call_args[1]["sitelinks"]

    @pytest.mark.asyncio
    async def test_delete_sitelink_idempotent(self) -> None:
        """Test delete_sitelink is idempotent when sitelink doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_entity = MagicMock()
        mock_entity.entity_data = MagicMock()
        mock_entity.entity_data.revision = {"sitelinks": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(handler, '_infer_entity_type_from_id', return_value=MagicMock()):
            with patch(
                'models.rest_api.entitybase.v1.handlers.entity.update.EntityReadHandler',
                return_value=MagicMock(get_entity=MagicMock(return_value=mock_entity))
            ):
                result = await handler.delete_sitelink(
                    "Q42",
                    "enwiki",  # Sitelink doesn't exist
                    EditHeaders(x_user_id=1, x_edit_summary="Delete sitelink"),
                )

                assert result == mock_entity

    # _infer_entity_type_from_id tests (static method)
    def test_infer_entity_type_from_id_item(self) -> None:
        """Test inferring ITEM type from Q prefix."""
        result = EntityUpdateHandler._infer_entity_type_from_id("Q42")
        from models.data.infrastructure.s3.enums import EntityType
        assert result == EntityType.ITEM

    def test_infer_entity_type_from_id_property(self) -> None:
        """Test inferring PROPERTY type from P prefix."""
        result = EntityUpdateHandler._infer_entity_type_from_id("P31")
        from models.data.infrastructure.s3.enums import EntityType
        assert result == EntityType.PROPERTY

    def test_infer_entity_type_from_id_lexeme(self) -> None:
        """Test inferring LEXEME type from L prefix."""
        result = EntityUpdateHandler._infer_entity_type_from_id("L123")
        from models.data.infrastructure.s3.enums import EntityType
        assert result == EntityType.LEXEME

    def test_infer_entity_type_from_id_invalid(self) -> None:
        """Test returning None for invalid ID formats."""
        assert EntityUpdateHandler._infer_entity_type_from_id("X123") is None
        assert EntityUpdateHandler._infer_entity_type_from_id("INVALID") is None
        assert EntityUpdateHandler._infer_entity_type_from_id("Q") is None
