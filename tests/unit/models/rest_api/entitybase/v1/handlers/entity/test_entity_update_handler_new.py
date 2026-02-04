"""Tests for new EntityUpdateHandler specialized methods."""

from unittest.mock import MagicMock, patch

import pytest

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.enums import EntityType
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler


class TestEntityUpdateHandlerNewLabelMethods:
    """Tests for label update methods."""

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


class TestEntityUpdateHandlerDescriptionMethods:
    """Tests for description update methods."""


class TestEntityUpdateHandlerAliasMethods:
    """Tests for alias update methods."""


class TestEntityUpdateHandlerSitelinkMethods:
    """Tests for sitelink update methods."""


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
