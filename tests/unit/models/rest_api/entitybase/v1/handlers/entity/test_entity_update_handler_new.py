"""Tests for new EntityUpdateHandler specialized methods."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from models.common import EditHeaders
from models.data.infrastructure.s3.enums import EntityType
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.utils import raise_validation_error


class TestEntityUpdateHandlerNewLabelMethods:
    """Tests for label update methods."""

    @pytest.mark.asyncio
    async def test_update_label_success(self):
        """Test successful label update."""
        # Mock setup
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "labels": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.update_label(
                    entity_id="Q42",
                    language_code="en",
                    language="en",
                    value="Test Label",
                    edit_headers=EditHeaders(
                        x_user_id=123,
                        x_edit_summary="Test"
                    ),
                    validator=None,
                )

                # Verify data was updated
                assert mock_entity.entity_data["labels"]["en"]["value"] == "Test Label"
                assert mock_update.called

    @pytest.mark.asyncio
    async def test_update_label_language_mismatch(self):
        """Test label update with language mismatch."""
        mock_state = MagicMock()
        handler = EntityUpdateHandler(state=mock_state)

        with pytest.raises(Exception):
            await handler.update_label(
                entity_id="Q42",
                language_code="en",
                language="fr",
                value="Test",
                edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
            )

    @pytest.mark.asyncio
    async def test_delete_label_idempotent(self):
        """Test deleting non-existent label is idempotent."""
        # Mock setup
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "labels": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.delete_label(
                    entity_id="Q42",
                    language_code="fr",
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                )

                # Should return current entity without error
                assert result == mock_entity
                # Should not call update (nothing changed)
                assert not mock_update.called


class TestEntityUpdateHandlerDescriptionMethods:
    """Tests for description update methods."""

    @pytest.mark.asyncio
    async def test_update_description_success(self):
        """Test successful description update."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "descriptions": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.update_description(
                    entity_id="Q42",
                    language_code="en",
                    language="en",
                    description="Test Description",
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                    validator=None,
                )

                # Verify data was updated
                assert mock_entity.entity_data["descriptions"]["en"]["value"] == "Test Description"
                assert mock_update.called

    @pytest.mark.asyncio
    async def test_delete_description_idempotent(self):
        """Test deleting non-existent description is idempotent."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "descriptions": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.delete_description(
                    entity_id="Q42",
                    language_code="fr",
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                )

                # Should return current entity without error
                assert result == mock_entity
                # Should not call update (nothing changed)
                assert not mock_update.called


class TestEntityUpdateHandlerAliasMethods:
    """Tests for alias update methods."""

    @pytest.mark.asyncio
    async def test_update_aliases_success(self):
        """Test successful alias update."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "aliases": {}}

        handler = EntityUpdateHandler(state=mock_state)

        aliases_data = ["alias1", "alias2"]

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.update_aliases(
                    entity_id="Q42",
                    language_code="en",
                    aliases=aliases_data,
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                    validator=None,
                )

                # Verify aliases were converted to internal format
                expected = [{"value": "alias1"}, {"value": "alias2"}]
                assert mock_entity.entity_data["aliases"]["en"] == expected
                assert mock_update.called

    @pytest.mark.asyncio
    async def test_update_aliases_converts_format(self):
        """Test that aliases are converted from list to dict format."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "aliases": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction'):
                await handler.update_aliases(
                    entity_id="Q42",
                    language_code="en",
                    aliases=["alias1", "alias2"],
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                )

                # Verify conversion format
                assert isinstance(mock_entity.entity_data["aliases"]["en"], list)
                assert all("value" in alias for alias in mock_entity.entity_data["aliases"]["en"])


class TestEntityUpdateHandlerSitelinkMethods:
    """Tests for sitelink update methods."""

    @pytest.mark.asyncio
    async def test_update_sitelink_post(self):
        """Test adding new sitelink."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "sitelinks": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.update_sitelink(
                    entity_id="Q42",
                    site="enwiki",
                    title="Test Page",
                    badges=["Q17437798"],
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                    validator=None,
                )

                # Verify sitelink was added
                assert mock_entity.entity_data["sitelinks"]["enwiki"]["title"] == "Test Page"
                assert mock_entity.entity_data["sitelinks"]["enwiki"]["badges"] == ["Q17437798"]
                assert mock_update.called

    @pytest.mark.asyncio
    async def test_update_sitelink_put(self):
        """Test updating existing sitelink."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "sitelinks": {"enwiki": {"title": "Old", "badges": []}}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.update_sitelink(
                    entity_id="Q42",
                    site="enwiki",
                    title="New Title",
                    badges=["Q17437798"],
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                    validator=None,
                )

                # Verify sitelink was updated
                assert mock_entity.entity_data["sitelinks"]["enwiki"]["title"] == "New Title"
                assert mock_update.called

    @pytest.mark.asyncio
    async def test_delete_sitelink_idempotent(self):
        """Test deleting non-existent sitelink is idempotent."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.entity_exists.return_value = True
        mock_vitess.is_entity_deleted.return_value = False
        mock_vitess.is_entity_locked.return_value = False

        mock_entity = MagicMock()
        mock_entity.entity_data = {"type": "item", "sitelinks": {}}

        handler = EntityUpdateHandler(state=mock_state)

        with patch.object(EntityReadHandler, 'get_entity', return_value=mock_entity):
            with patch.object(handler, '_update_with_transaction', return_value=mock_entity) as mock_update:
                result = await handler.delete_sitelink(
                    entity_id="Q42",
                    site="dewiki",
                    edit_headers=EditHeaders(x_user_id=123, x_edit_summary="Test"),
                )

                # Should return current entity without error
                assert result == mock_entity
                # Should not call update (nothing changed)
                assert not mock_update.called


class TestEntityUpdateHandlerHelperMethods:
    """Tests for helper methods."""

    def test_infer_entity_type_from_id_item(self):
        """Test entity type inference for items."""
        handler = EntityUpdateHandler(state=MagicMock())
        assert handler._infer_entity_type_from_id("Q42") == EntityType.ITEM
        assert handler._infer_entity_type_from_id("Q1") == EntityType.ITEM

    def test_infer_entity_type_from_id_property(self):
        """Test entity type inference for properties."""
        handler = EntityUpdateHandler(state=MagicMock())
        assert handler._infer_entity_type_from_id("P42") == EntityType.PROPERTY
        assert handler._infer_entity_type_from_id("P1") == EntityType.PROPERTY

    def test_infer_entity_type_from_id_lexeme(self):
        """Test entity type inference for lexemes."""
        handler = EntityUpdateHandler(state=MagicMock())
        assert handler._infer_entity_type_from_id("L42") == EntityType.LEXEME
        assert handler._infer_entity_type_from_id("L1") == EntityType.LEXEME

    def test_infer_entity_type_from_id_invalid(self):
        """Test entity type inference for invalid IDs."""
        handler = EntityUpdateHandler(state=MagicMock())
        assert handler._infer_entity_type_from_id("X42") is None
        assert handler._infer_entity_type_from_id("invalid") is None
        assert handler._infer_entity_type_from_id("") is None
