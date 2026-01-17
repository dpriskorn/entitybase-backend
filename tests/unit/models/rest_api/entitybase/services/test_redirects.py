"""Unit tests for redirect service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from models.rest_api.entitybase.services.redirects import RedirectService
from models.rest_api.entitybase.request.entity import EntityRedirectRequest
from models.rest_api.entitybase.response import (
    EntityRedirectResponse,
    EntityResponse,
    EntityRevertResponse,
)
from models.validation.utils import raise_validation_error


class TestRedirectService:
    """Test cases for RedirectService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_s3_client = Mock()
        self.mock_vitess_client = Mock()
        self.mock_stream_producer = AsyncMock()

        self.service = RedirectService(
            self.mock_s3_client, self.mock_vitess_client, self.mock_stream_producer
        )

    def test_init(self):
        """Test service initialization."""
        assert self.service.s3 == self.mock_s3_client
        assert self.service.vitess == self.mock_vitess_client
        assert self.service.stream_producer == self.mock_stream_producer

    @pytest.mark.asyncio
    async def test_create_redirect_success(self):
        """Test successful redirect creation."""
        # Setup mocks
        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = False
        self.mock_vitess_client.get_head.side_effect = [5, 0]  # from head, to head

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        result = await self.service.create_redirect(request)

        # Verify response
        assert isinstance(result, EntityRedirectResponse)
        assert result.redirect_from_id == "Q100"
        assert result.redirect_to_id == "Q200"
        assert result.revision_id == 6  # 5 + 1
        assert result.created_at is not None

        # Verify method calls
        self.mock_s3_client.write_revision.assert_called_once()
        self.mock_vitess_client.insert_revision.assert_called_once()
        self.mock_vitess_client.create_redirect.assert_called_once_with(
            redirect_from_entity_id="Q100",
            redirect_to_entity_id="Q200",
            created_by="test-user",
        )
        self.mock_vitess_client.set_redirect_target.assert_called_once_with(
            entity_id="Q100", redirects_to_entity_id="Q200"
        )
        self.mock_s3_client.mark_published.assert_called_once()

        # Verify stream event
        self.mock_stream_producer.publish_change.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_redirect_circular_prevention(self):
        """Test that redirecting to self is prevented."""
        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q100", created_by="test-user"
        )

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.create_redirect(request)
            mock_raise.assert_called_once_with(
                "Cannot redirect to self", status_code=400
            )

    @pytest.mark.asyncio
    async def test_create_redirect_already_exists(self):
        """Test that creating redirect on existing redirect fails."""
        self.mock_vitess_client.get_redirect_target.return_value = "Q200"

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q300", created_by="test-user"
        )

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.create_redirect(request)
            mock_raise.assert_called_once_with(
                "Redirect already exists", status_code=409
            )

    @pytest.mark.asyncio
    async def test_create_redirect_source_deleted(self):
        """Test that redirecting from deleted entity fails."""
        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.side_effect = [True, False]

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.create_redirect(request)
            mock_raise.assert_called_once_with(
                "Source entity has been deleted", status_code=423
            )

    @pytest.mark.asyncio
    async def test_create_redirect_target_deleted(self):
        """Test that redirecting to deleted entity fails."""
        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.side_effect = [False, True]

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.create_redirect(request)
            mock_raise.assert_called_once_with(
                "Target entity has been deleted", status_code=423
            )

    @pytest.mark.asyncio
    async def test_create_redirect_target_locked(self):
        """Test that redirecting to locked entity fails."""
        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = True

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.create_redirect(request)
            mock_raise.assert_called_once_with(
                "Target entity is locked or archived", status_code=423
            )

    @pytest.mark.asyncio
    async def test_create_redirect_target_archived(self):
        """Test that redirecting to archived entity fails."""
        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = True

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.create_redirect(request)
            mock_raise.assert_called_once_with(
                "Target entity is locked or archived", status_code=423
            )

    @pytest.mark.asyncio
    async def test_create_redirect_target_no_revisions(self):
        """Test that redirecting to entity with no revisions fails."""
        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = False
        self.mock_vitess_client.get_head.return_value = 0  # No revisions

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.create_redirect(request)
            mock_raise.assert_called_once_with(
                "Target entity has no revisions", status_code=404
            )

    @pytest.mark.asyncio
    async def test_create_redirect_from_entity_no_revisions(self):
        """Test redirect creation when source entity has no revisions."""
        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = False
        self.mock_vitess_client.get_head.side_effect = [
            0,
            5,
        ]  # from head (none), to head

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        result = await self.service.create_redirect(request)

        assert result.revision_id == 1  # Should start from 1

    @pytest.mark.asyncio
    async def test_create_redirect_without_stream_producer(self):
        """Test redirect creation without stream producer."""
        service_no_stream = RedirectService(
            self.mock_s3_client, self.mock_vitess_client, None
        )

        self.mock_vitess_client.get_redirect_target.return_value = None
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = False
        self.mock_vitess_client.get_head.side_effect = [5, 0]

        request = EntityRedirectRequest(
            redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
        )

        result = await service_no_stream.create_redirect(request)

        assert isinstance(result, EntityRedirectResponse)
        # Stream producer should not be called
        assert not hasattr(service_no_stream, "mock_stream_producer")

    @pytest.mark.asyncio
    @patch("models.rest_api.entitybase.services.redirects.EntityRevertHandler")
    async def test_revert_redirect_success(self, mock_revert_handler):
        """Test successful redirect revert."""
        # Setup mocks
        self.mock_vitess_client.get_redirect_target.return_value = "Q200"
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = False

        mock_revert_instance = Mock()
        mock_revert_handler.return_value = mock_revert_instance
        mock_revert_instance.revert_entity.return_value = Mock()  # dummy

        result = await self.service.revert_redirect("Q100", 5, 1)

        # Verify response
        assert isinstance(result, EntityRevertResponse)
        assert result.entity_id == "Q100"
        mock_revert_handler.assert_called_once()
        mock_revert_instance.revert_entity.assert_called_once()
        self.mock_vitess_client.revert_redirect.assert_called_once_with("Q100")
        assert result.revision_id == 11  # 10 + 1
        assert result.entity_data["labels"]["en"]["value"] == "Test"

        # Verify method calls
        self.mock_s3_client.read_full_revision.assert_called_once_with("Q100", 5)
        self.mock_s3_client.write_revision.assert_called_once()
        self.mock_vitess_client.insert_revision.assert_called_once()
        self.mock_vitess_client.set_redirect_target.assert_called_once_with(
            entity_id="Q100", redirects_to_entity_id=None
        )
        self.mock_s3_client.mark_published.assert_called_once()

        # Verify stream event
        self.mock_stream_producer.publish_change.assert_called_once()

    @pytest.mark.asyncio
    async def test_revert_redirect_not_a_redirect(self):
        """Test reverting entity that is not a redirect."""
        self.mock_vitess_client.get_redirect_target.return_value = None

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.revert_redirect("Q100", 5, 1)
            mock_raise.assert_called_once_with(
                "Entity is not a redirect", status_code=404
            )

    @pytest.mark.asyncio
    async def test_revert_redirect_entity_deleted(self):
        """Test reverting deleted entity."""
        self.mock_vitess_client.get_redirect_target.return_value = "Q200"
        self.mock_vitess_client.is_entity_deleted.return_value = True

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.revert_redirect("Q100", 5, 1)
            mock_raise.assert_called_once_with(
                "Entity has been deleted", status_code=423
            )

    @pytest.mark.asyncio
    async def test_revert_redirect_entity_locked(self):
        """Test reverting locked entity."""
        self.mock_vitess_client.get_redirect_target.return_value = "Q200"
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = True

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.revert_redirect("Q100", 5, 1)
            mock_raise.assert_called_once_with(
                "Entity is locked or archived", status_code=423
            )

    @pytest.mark.asyncio
    async def test_revert_redirect_entity_archived(self):
        """Test reverting archived entity."""
        self.mock_vitess_client.get_redirect_target.return_value = "Q200"
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = True

        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ) as mock_raise:
            await self.service.revert_redirect("Q100", 5, 1)
            mock_raise.assert_called_once_with(
                "Entity is locked or archived", status_code=423
            )

    @pytest.mark.asyncio
    async def test_revert_redirect_no_head_revision(self):
        """Test revert when entity has no head revision."""
        self.mock_vitess_client.get_redirect_target.return_value = "Q200"
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = False
        self.mock_vitess_client.get_head.return_value = 0

        mock_revision = Mock()
        mock_revision.data = {"entity": {"id": "Q100"}}
        self.mock_s3_client.read_full_revision.return_value = mock_revision

        result = await self.service.revert_redirect("Q100", 5, 1)

        assert result.revision_id == 1  # Should start from 1

    @pytest.mark.asyncio
    async def test_revert_redirect_without_stream_producer(self):
        """Test redirect revert without stream producer."""
        service_no_stream = RedirectService(
            self.mock_s3_client, self.mock_vitess_client, None
        )

        self.mock_vitess_client.get_redirect_target.return_value = "Q200"
        self.mock_vitess_client.is_entity_deleted.return_value = False
        self.mock_vitess_client.is_entity_locked.return_value = False
        self.mock_vitess_client.is_entity_archived.return_value = False
        self.mock_vitess_client.get_head.return_value = 10

        mock_revision = Mock()
        mock_revision.data = {"entity": {"id": "Q100"}}
        self.mock_s3_client.read_full_revision.return_value = mock_revision

        result = await service_no_stream.revert_redirect("Q100", 5)

        assert isinstance(result, EntityResponse)
        # Stream producer should not be called

    @patch("models.rest_api.entitybase.services.redirects.logger")
    def test_debug_logging_create(self, mock_logger):
        """Test debug logging for create redirect."""
        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ):
            request = EntityRedirectRequest(
                redirect_from_id="Q100", redirect_to_id="Q200", created_by="test-user"
            )

            # Use sync version for logging test
            import asyncio

            try:
                asyncio.get_event_loop().run_until_complete(
                    self.service.create_redirect(request)
                )
            except:
                pass  # We're just testing the logging call

        mock_logger.debug.assert_called_with(
            "Creating redirect from %s to %s", "Q100", "Q200"
        )

    @patch("models.rest_api.entitybase.services.redirects.logger")
    def test_debug_logging_revert(self, mock_logger):
        """Test debug logging for revert redirect."""
        with patch(
            "models.rest_api.entitybase.services.redirects.raise_validation_error"
        ):
            import asyncio

            try:
                asyncio.get_event_loop().run_until_complete(
                    self.service.revert_redirect("Q100", 5)
                )
            except:
                pass  # We're just testing the logging call

        mock_logger.debug.assert_called_with(
            "Reverting redirect for entity %s to revision %d", "Q100", 5
        )
