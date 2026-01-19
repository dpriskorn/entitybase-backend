"""Unit tests for new EntityHandler services and methods."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.infrastructure.s3.enums import EntityType, EditType
from models.rest_api.entitybase.handlers.entity.handler import (
    EntityHandler,
    EntityHashingService,
    EntityValidationService,
    RevisionContext,
)
from models.rest_api.entitybase.response import EntityResponse


@pytest.mark.unit
class TestEntityHashingService:
    """Unit tests for EntityHashingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EntityHashingService()

    @patch("models.rest_api.entitybase.handlers.entity.handler.hash_entity_statements")
    @pytest.mark.asyncio
    async def test_hash_statements_success(self, mock_hash):
        """Test successful statement hashing."""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = MagicMock()
        mock_hash.return_value = mock_result

        result = await self.service.hash_statements({"claims": {}})

        assert result == mock_result.data
        mock_hash.assert_called_once_with({"claims": {}})

    @patch("models.rest_api.entitybase.handlers.entity.handler.hash_entity_statements")
    @pytest.mark.asyncio
    async def test_hash_statements_failure(self, mock_hash):
        """Test statement hashing failure."""
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Hash failed"
        mock_hash.return_value = mock_result

        with pytest.raises(Exception):  # EntityProcessingError
            await self.service.hash_statements({"claims": {}})


@pytest.mark.unit
class TestEntityValidationService(unittest.TestCase):
    """Unit tests for EntityValidationService."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = EntityValidationService()
        self.mock_vitess = MagicMock()

    def test_validate_protection_settings_mass_edit_blocked(self) -> None:
        """Test mass edit protection validation."""
        self.mock_vitess.is_entity_semi_protected.return_value = True

        with pytest.raises(Exception):  # ValidationError
            self.service.validate_protection_settings(
                "Q1", True, True, self.mock_vitess
            )

    def test_validate_idempotency_with_existing_revision(self) -> None:
        """Test idempotency validation with existing revision."""
        mock_s3 = MagicMock()
        mock_revision = MagicMock()
        mock_revision.data.get.side_effect = lambda key, default=False: 12345 if key == "content_hash" else default
        mock_revision.entity = {"id": "Q1", "labels": {}}
        mock_s3.read_revision.return_value = mock_revision

        result = self.service.validate_idempotency("Q1", 1, 12345, {}, mock_s3)

        assert isinstance(result, EntityResponse)
        assert result.id == "Q1"


@pytest.mark.unit
class TestEntityHandlerNewMethods:
    """Unit tests for new EntityHandler methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = EntityHandler()
        self.mock_vitess = MagicMock()
        self.mock_s3 = MagicMock()
        self.mock_stream = MagicMock()

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_process_entity_revision_new_success(self):
        """Test successful entity revision processing."""
        ctx = RevisionContext(
            entity_id="Q1",
            request_data={"id": "Q1", "labels": {}},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test update",
            is_creation=False,
            vitess_client=self.mock_vitess,
            s3_client=self.mock_s3,
            stream_producer=self.mock_stream,
            validator=None,
        )

        # Mock the helper methods
        mock_response = MagicMock(spec=EntityResponse)
        with patch.object(self.handler, '_validate_revision_request') as mock_validate, \
             patch.object(self.handler, '_check_idempotency_new', new_callable=AsyncMock, return_value=None) as mock_idem, \
             patch.object(self.handler, '_process_entity_data_new') as mock_process, \
             patch.object(self.handler, '_create_revision_new') as mock_create, \
             patch.object(self.handler, '_publish_events_new') as mock_publish, \
             patch.object(self.handler, '_build_entity_response', new_callable=AsyncMock, return_value=mock_response) as mock_build:

            mock_hash_result = MagicMock()
            mock_process.return_value = mock_hash_result

            mock_revision_result = MagicMock()
            mock_revision_result.success = True
            mock_create.return_value = mock_revision_result

            result = await self.handler.process_entity_revision_new(
                entity_id="Q1",
                request_data={"id": "Q1", "labels": {}},
                entity_type=EntityType.ITEM,
                edit_type=EditType.MANUAL_UPDATE,
                edit_summary="Test update",
                is_creation=False,
                vitess_client=self.mock_vitess,
                s3_client=self.mock_s3,
                stream_producer=self.mock_stream,
                validator=None,
            )

            assert result is mock_response
            mock_validate.assert_called_once_with(ctx)
            mock_idem.assert_called_once_with(ctx)
            mock_process.assert_called_once_with(ctx)
            mock_create.assert_called_once_with(ctx, mock_hash_result)
            mock_publish.assert_called_once_with(ctx, mock_revision_result)
            mock_build.assert_called_once_with(ctx, mock_revision_result)

    def test_validate_revision_request_success(self) -> None:
        """Test successful revision request validation."""
        ctx = RevisionContext(
            entity_id="Q1",
            request_data={},
            entity_type=EntityType.ITEM,
            vitess_client=self.mock_vitess,
            s3_client=self.mock_s3,
        )

        # Should not raise
        self.handler._validate_revision_request(ctx)

    def test_validate_revision_request_invalid_id(self) -> None:
        """Test validation failure for invalid entity ID."""
        ctx = RevisionContext(
            entity_id="",
            request_data={},
            entity_type=EntityType.ITEM,
            vitess_client=self.mock_vitess,
            s3_client=self.mock_s3,
        )

        with pytest.raises(Exception):  # EntityProcessingError
            self.handler._validate_revision_request(ctx)


if __name__ == "__main__":
    unittest.main()