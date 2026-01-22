"""Unit tests for redirects service."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.request.entity import EntityRedirectRequest
from models.rest_api.entitybase.v1.response import EntityRedirectResponse
from models.rest_api.entitybase.v1.response.entity import EntityRevertResponse
from models.rest_api.entitybase.v1.services.redirects import RedirectService


# Import classes that need to be mocked


class TestRedirectService:
    """Unit tests for RedirectService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = RedirectService.__new__(RedirectService)
        self.service.vitess = MagicMock()
        self.service.s3 = MagicMock()
        self.service.stream_producer = AsyncMock()
        self.service.state = MagicMock()

    @pytest.mark.asyncio
    async def test_create_redirect_success(self):
        """Test successful redirect creation."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        # Mock vitess methods
        self.service.vitess.get_redirect_target.return_value = None
        self.service.vitess.is_entity_deleted.return_value = False
        self.service.vitess.is_entity_locked.return_value = False
        self.service.vitess.is_entity_archived.return_value = False
        self.service.vitess.get_head.side_effect = [0, 1]  # from: 0, to: 1

        with patch('models.rest_api.entitybase.v1.services.redirects.RevisionData') as mock_revision_data, \
             patch('models.rest_api.entitybase.v1.services.redirects.EntityType'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EditType'), \
             patch('models.rest_api.entitybase.v1.services.redirects.HashMaps'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EntityState'), \
             patch('models.rest_api.entitybase.v1.services.redirects.datetime') as mock_datetime:

            mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)

            result = await self.service.create_redirect(request)

            assert isinstance(result, EntityRedirectResponse)
            assert result.redirect_from_id == "Q1"
            assert result.redirect_to_id == "Q2"
            assert result.revision_id == 1

            # Verify vitess calls
            self.service.vitess.create_redirect.assert_called_once_with(
                redirect_from_entity_id="Q1",
                redirect_to_entity_id="Q2",
                created_by="test_user"
            )
            self.service.vitess.set_redirect_target.assert_called_once_with(
                entity_id="Q1",
                redirects_to_entity_id="Q2"
            )

            # Verify S3 calls
            self.service.s3.write_revision.assert_called_once()
            self.service.s3.mark_published.assert_called_once_with(
                entity_id="Q1",
                revision_id=1,
                publication_state="published"
            )

            # Verify stream event
            self.service.stream_producer.publish_change.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_redirect_self_redirect_error(self):
        """Test redirect to self raises error."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q1",
            user_id=123,
            created_by="test_user"
        )

        with pytest.raises(Exception) as exc_info:
            await self.service.create_redirect(request)

        assert "Cannot redirect to self" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_redirect_already_exists_error(self):
        """Test redirect creation when redirect already exists."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        self.service.vitess.get_redirect_target.return_value = "Q3"

        with pytest.raises(Exception) as exc_info:
            await self.service.create_redirect(request)

        assert "Redirect already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_redirect_source_deleted_error(self):
        """Test redirect creation when source entity is deleted."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        self.service.vitess.get_redirect_target.return_value = None
        self.service.vitess.is_entity_deleted.side_effect = [True, False]  # source deleted

        with pytest.raises(Exception) as exc_info:
            await self.service.create_redirect(request)

        assert "Source entity has been deleted" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_redirect_target_deleted_error(self):
        """Test redirect creation when target entity is deleted."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        self.service.vitess.get_redirect_target.return_value = None
        self.service.vitess.is_entity_deleted.side_effect = [False, True]  # target deleted

        with pytest.raises(Exception) as exc_info:
            await self.service.create_redirect(request)

        assert "Target entity has been deleted" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_redirect_target_locked_error(self):
        """Test redirect creation when target entity is locked."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        self.service.vitess.get_redirect_target.return_value = None
        self.service.vitess.is_entity_deleted.return_value = False
        self.service.vitess.is_entity_locked.return_value = True
        self.service.vitess.is_entity_archived.return_value = False

        with pytest.raises(Exception) as exc_info:
            await self.service.create_redirect(request)

        assert "Target entity is locked or archived" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_redirect_target_no_revisions_error(self):
        """Test redirect creation when target has no revisions."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        self.service.vitess.get_redirect_target.return_value = None
        self.service.vitess.is_entity_deleted.return_value = False
        self.service.vitess.is_entity_locked.return_value = False
        self.service.vitess.is_entity_archived.return_value = False
        self.service.vitess.get_head.side_effect = [1, 0]  # target has no revisions

        with pytest.raises(Exception) as exc_info:
            await self.service.create_redirect(request)

        assert "Target entity has no revisions" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_redirect_with_existing_revisions(self):
        """Test redirect creation with existing source revisions."""
        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        self.service.vitess.get_redirect_target.return_value = None
        self.service.vitess.is_entity_deleted.return_value = False
        self.service.vitess.is_entity_locked.return_value = False
        self.service.vitess.is_entity_archived.return_value = False
        self.service.vitess.get_head.side_effect = [5, 1]  # source has rev 5, target has rev 1

        with patch('models.rest_api.entitybase.v1.services.redirects.RevisionData'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EntityType'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EditType'), \
             patch('models.rest_api.entitybase.v1.services.redirects.HashMaps'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EntityState'), \
             patch('models.rest_api.entitybase.v1.services.redirects.datetime') as mock_datetime:

            mock_datetime.now.return_value = datetime(2023, 1, 1, tzinfo=timezone.utc)

            result = await self.service.create_redirect(request)

            assert result.revision_id == 6  # 5 + 1

            self.service.vitess.create_revision.assert_called_once_with(
                entity_id="Q1",
                revision_id=6,
                entity_data={},
                expected_revision_id=5
            )

    @pytest.mark.asyncio
    async def test_create_redirect_no_stream_producer(self):
        """Test redirect creation without stream producer."""
        self.service.stream_producer = None

        request = EntityRedirectRequest(
            redirect_from_id="Q1",
            redirect_to_id="Q2",
            user_id=123,
            created_by="test_user"
        )

        self.service.vitess.get_redirect_target.return_value = None
        self.service.vitess.is_entity_deleted.return_value = False
        self.service.vitess.is_entity_locked.return_value = False
        self.service.vitess.is_entity_archived.return_value = False
        self.service.vitess.get_head.side_effect = [0, 1]

        with patch('models.rest_api.entitybase.v1.services.redirects.RevisionData'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EntityType'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EditType'), \
             patch('models.rest_api.entitybase.v1.services.redirects.HashMaps'), \
             patch('models.rest_api.entitybase.v1.services.redirects.EntityState'), \
             patch('models.rest_api.entitybase.v1.services.redirects.datetime'):

            result = await self.service.create_redirect(request)

            # Stream producer not called
            assert not hasattr(self.service, 'stream_producer') or self.service.stream_producer is None

    @pytest.mark.asyncio
    async def test_revert_redirect_success(self):
        """Test successful redirect revert."""
        self.service.vitess.get_redirect_target.return_value = "Q2"
        self.service.vitess.is_entity_deleted.return_value = False
        self.service.vitess.is_entity_locked.return_value = False
        self.service.vitess.is_entity_archived.return_value = False

        mock_revert_result = MagicMock(spec=EntityRevertResponse)

        with patch('models.rest_api.entitybase.v1.services.redirects.EntityRevertHandler') as mock_handler_class, \
             patch('models.rest_api.entitybase.v1.services.redirects.EntityRevertRequest') as mock_request_class:

            mock_handler = MagicMock()
            mock_handler.revert_entity = AsyncMock(return_value=mock_revert_result)
            mock_handler_class.return_value = mock_handler

            result = await self.service.revert_redirect("Q1", 5, 123)

            assert result == mock_revert_result

            # Verify revert redirect called
            self.service.vitess.revert_redirect.assert_called_once_with("Q1")

    @pytest.mark.asyncio
    async def test_revert_redirect_not_a_redirect_error(self):
        """Test revert when entity is not a redirect."""
        self.service.vitess.get_redirect_target.return_value = None

        with pytest.raises(Exception) as exc_info:
            await self.service.revert_redirect("Q1", 5, 123)

        assert "Entity is not a redirect" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_revert_redirect_deleted_error(self):
        """Test revert when entity is deleted."""
        self.service.vitess.get_redirect_target.return_value = "Q2"
        self.service.vitess.is_entity_deleted.return_value = True

        with pytest.raises(Exception) as exc_info:
            await self.service.revert_redirect("Q1", 5, 123)

        assert "Entity has been deleted" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_revert_redirect_locked_error(self):
        """Test revert when entity is locked."""
        self.service.vitess.get_redirect_target.return_value = "Q2"
        self.service.vitess.is_entity_deleted.return_value = False
        self.service.vitess.is_entity_locked.return_value = True

        with pytest.raises(Exception) as exc_info:
            await self.service.revert_redirect("Q1", 5, 123)

        assert "Entity is locked or archived" in str(exc_info.value)