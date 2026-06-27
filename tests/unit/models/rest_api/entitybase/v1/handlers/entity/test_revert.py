"""Unit tests for EntityRevertHandler in revert.py."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request.entity.revert import EntityRevertRequest
from models.data.rest_api.v1.entitybase.response.entity.revert import (
    EntityRevertResponse,
)
from models.rest_api.entitybase.v1.handlers.entity.revert import EntityRevertHandler


class TestEntityRevertHandlerResolveEntityId:
    """Tests for EntityRevertHandler._resolve_entity_id."""

    @pytest.mark.asyncio
    async def test_resolve_entity_id_success(self) -> None:
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.id_resolver.resolve_id.return_value = 42

        handler = EntityRevertHandler(state=mock_state)
        result = await handler._resolve_entity_id("Q42")

        assert result == 42
        mock_mysql.id_resolver.resolve_id.assert_called_once_with("Q42")

    @pytest.mark.asyncio
    async def test_resolve_entity_id_not_found(self) -> None:
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.id_resolver.resolve_id.return_value = 0

        handler = EntityRevertHandler(state=mock_state)
        with pytest.raises(HTTPException) as exc_info:
            await handler._resolve_entity_id("Q999")
        assert exc_info.value.status_code == 404


class TestEntityRevertHandlerGetTargetRevision:
    """Tests for EntityRevertHandler._get_target_revision."""

    @pytest.mark.asyncio
    async def test_get_target_revision_success(self) -> None:
        from models.infrastructure.s3.revision.revision_data import RevisionData

        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql

        mock_revision = MagicMock(spec=RevisionData)
        mock_mysql.revision_repository.get_revision.return_value = mock_revision

        handler = EntityRevertHandler(state=mock_state)
        result = await handler._get_target_revision("Q42", 1, 42)

        assert result is mock_revision
        mock_mysql.revision_repository.get_revision.assert_called_once_with(42, 1)

    @pytest.mark.asyncio
    async def test_get_target_revision_not_found(self) -> None:
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.revision_repository.get_revision.return_value = None

        handler = EntityRevertHandler(state=mock_state)
        with pytest.raises(HTTPException) as exc_info:
            await handler._get_target_revision("Q42", 999, 42)
        assert exc_info.value.status_code == 404


class TestEntityRevertHandlerReadTargetRevisionFromS3:
    """Tests for EntityRevertHandler._read_target_revision_from_s3."""

    @pytest.mark.asyncio
    async def test_read_target_revision_from_s3_success(self) -> None:
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        mock_s3_data = MagicMock(spec=S3RevisionData)
        mock_s3.read_full_revision.return_value = mock_s3_data

        handler = EntityRevertHandler(state=mock_state)
        result = await handler._read_target_revision_from_s3("Q42", 1)

        assert result is mock_s3_data
        mock_s3.read_full_revision.assert_called_once_with("Q42", 1)


class TestEntityRevertHandlerGetHeadRevision:
    """Tests for EntityRevertHandler._get_head_revision."""

    @pytest.mark.asyncio
    async def test_get_head_revision_success(self) -> None:
        from models.data.common import OperationResult

        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.head_repository.get_head_revision.return_value = OperationResult(
            success=True, data=5
        )

        handler = EntityRevertHandler(state=mock_state)
        result = await handler._get_head_revision(42)

        assert result == 5
        mock_mysql.head_repository.get_head_revision.assert_called_once_with(42)

    @pytest.mark.asyncio
    async def test_get_head_revision_failure(self) -> None:
        from models.data.common import OperationResult

        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.head_repository.get_head_revision.return_value = OperationResult(
            success=False, error="DB error"
        )

        handler = EntityRevertHandler(state=mock_state)
        with pytest.raises(HTTPException) as exc_info:
            await handler._get_head_revision(42)
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_head_revision_data_none(self) -> None:
        from models.data.common import OperationResult

        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.head_repository.get_head_revision.return_value = OperationResult(
            success=True, data=None
        )

        handler = EntityRevertHandler(state=mock_state)
        result = await handler._get_head_revision(42)
        assert result == 0


class TestEntityRevertHandlerValidateRevertTarget:
    """Tests for EntityRevertHandler._validate_revert_target."""

    def test_validate_revert_target_valid(self) -> None:
        handler = EntityRevertHandler(state=MagicMock())
        handler._validate_revert_target("Q42", 5, 10)

    def test_validate_revert_target_already_at_revision(self) -> None:
        handler = EntityRevertHandler(state=MagicMock())
        with pytest.raises(HTTPException) as exc_info:
            handler._validate_revert_target("Q42", 5, 5)
        assert exc_info.value.status_code == 400


class TestEntityRevertHandlerCreateRevisionData:
    """Tests for EntityRevertHandler._create_revision_data."""

    def _make_target_data(
        self,
        hashes: dict | None = None,
        state: dict | None = None,
        property_counts: dict | None = None,
        properties: list | None = None,
    ) -> MagicMock:
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        data = MagicMock(spec=S3RevisionData)
        data.revision = {}
        if hashes is not None:
            data.revision["hashes"] = hashes
        if state is not None:
            data.revision["state"] = state
        if property_counts is not None:
            data.revision["property_counts"] = property_counts
        if properties is not None:
            data.revision["properties"] = properties
        return data

    @pytest.mark.asyncio
    async def test_create_revision_data_with_hashes_and_state(self) -> None:
        from models.data.infrastructure.s3.enums import EditType, EntityType

        handler = EntityRevertHandler(state=MagicMock())
        target_data = self._make_target_data(
            hashes={"labels": {"en": 111}, "statements": [111, 222]},
            state={"is_semi_protected": True, "locked": True},
            property_counts={"P1": 1},
            properties=["P1"],
        )
        edit_headers = EditHeaders(x_edit_summary="Revert")

        result = await handler._create_revision_data(
            "Q42", target_data, 11, edit_headers
        )

        assert result.revision_id == 11
        assert result.entity_type == EntityType.ITEM
        assert result.edit.edit_type == EditType.MANUAL_UPDATE
        assert result.edit.user_id == 123
        assert "Revert to revision 10" in result.edit.edit_summary
        assert result.hashes.labels.root == {"en": 111}
        assert result.hashes.statements.root == [111, 222]
        assert result.state.is_semi_protected is True
        assert result.state.is_locked is True
        assert result.property_counts.root == {"P1": 1}
        assert result.properties == ["P1"]

    @pytest.mark.asyncio
    async def test_create_revision_data_with_alias_state_keys(self) -> None:
        handler = EntityRevertHandler(state=MagicMock())
        target_data = self._make_target_data(
            state={"sp": True, "locked": False, "archived": True},
        )
        edit_headers = EditHeaders(x_edit_summary="test")

        result = await handler._create_revision_data(
            "Q42", target_data, 5, edit_headers
        )

        assert result.state.is_semi_protected is True
        assert result.state.is_locked is False
        assert result.state.is_archived is True

    @pytest.mark.asyncio
    async def test_create_revision_data_empty_target(self) -> None:
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        handler = EntityRevertHandler(state=MagicMock())
        empty_data = MagicMock(spec=S3RevisionData)
        empty_data.revision = None
        edit_headers = EditHeaders(x_edit_summary="test")

        result = await handler._create_revision_data("Q42", empty_data, 1, edit_headers)

        assert result.hashes.statements is None
        assert result.hashes.labels is None
        assert result.state.is_semi_protected is False
        assert result.property_counts is None
        assert result.properties == []

    @pytest.mark.asyncio
    async def test_create_revision_data_non_dict_hashes(self) -> None:
        handler = EntityRevertHandler(state=MagicMock())
        target_data = self._make_target_data(hashes="invalid")
        edit_headers = EditHeaders(x_edit_summary="test")

        result = await handler._create_revision_data(
            "Q42", target_data, 1, edit_headers
        )

        assert result.hashes.statements is None

    @pytest.mark.asyncio
    async def test_create_revision_data_non_dict_state(self) -> None:
        handler = EntityRevertHandler(state=MagicMock())
        target_data = self._make_target_data(state="invalid")
        edit_headers = EditHeaders(x_edit_summary="test")

        result = await handler._create_revision_data(
            "Q42", target_data, 1, edit_headers
        )

        assert result.state.is_semi_protected is False


class TestEntityRevertHandlerStoreRevision:
    """Tests for EntityRevertHandler._store_revision."""

    @pytest.mark.asyncio
    async def test_store_revision_success(self) -> None:
        from models.infrastructure.s3.revision.revision_data import RevisionData

        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_mysql.insert_revision.return_value = True

        mock_revision_data = MagicMock(spec=RevisionData)
        mock_revision_data.model_dump.return_value = {"key": "value"}

        handler = EntityRevertHandler(state=mock_state)

        with (
            patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string"
            ) as mock_hash,
            patch(
                "models.config.settings.settings.s3_schema_revision_version", "1.0.0"
            ),
        ):
            mock_hash.return_value = 999
            result = await handler._store_revision("Q42", 11, mock_revision_data)

        assert result == 999
        mock_s3.store_revision.assert_called_once()
        stored_args = mock_s3.store_revision.call_args[0]
        assert stored_args[0] == 999
        mock_mysql.insert_revision.assert_called_once_with(
            "Q42", 11, mock_revision_data, 999
        )

    @pytest.mark.asyncio
    async def test_store_revision_conflict(self) -> None:
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_mysql.insert_revision.return_value = False
        mock_mysql.get_head.return_value = 15

        mock_revision_data = MagicMock()
        mock_revision_data.model_dump.return_value = {"key": "value"}

        handler = EntityRevertHandler(state=mock_state)

        with (
            patch(
                "models.internal_representation.metadata_extractor.MetadataExtractor.hash_string"
            ) as mock_hash,
            patch(
                "models.config.settings.settings.s3_schema_revision_version", "1.0.0"
            ),
        ):
            mock_hash.return_value = 999
            with pytest.raises(HTTPException) as exc_info:
                await handler._store_revision("Q42", 11, mock_revision_data)
        assert exc_info.value.status_code == 409
        mock_mysql.get_head.assert_called_once_with("Q42")


class TestEntityRevertHandlerPublishChangeEvent:
    """Tests for EntityRevertHandler._publish_change_event."""

    @pytest.mark.asyncio
    async def test_publish_event_with_producer_streaming_enabled(self) -> None:
        mock_state = MagicMock()
        mock_producer = AsyncMock()
        mock_state.entity_change_stream_producer = mock_producer
        edit_headers = EditHeaders(x_edit_summary="Revert test")

        handler = EntityRevertHandler(state=mock_state)

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.revert.settings"
        ) as mock_settings:
            mock_settings.streaming_enabled = True
            await handler._publish_change_event("Q42", 11, 5, edit_headers)

        mock_producer.publish.assert_awaited_once()
        published_event = mock_producer.publish.call_args[0][0]
        assert published_event.entity_id == "Q42"
        assert published_event.revision_id == 11
        assert published_event.change_type.value == "revert"
        assert published_event.from_revision_id == 5
        assert published_event.user_id == "123"
        assert published_event.edit_summary == "Revert test"

    @pytest.mark.asyncio
    async def test_publish_event_with_producer_streaming_disabled(self) -> None:
        mock_state = MagicMock()
        mock_producer = AsyncMock()
        mock_state.entity_change_stream_producer = mock_producer
        edit_headers = EditHeaders(x_edit_summary="Revert test")

        handler = EntityRevertHandler(state=mock_state)

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.revert.settings"
        ) as mock_settings:
            mock_settings.streaming_enabled = False
            await handler._publish_change_event("Q42", 11, 5, edit_headers)

        mock_producer.publish.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_publish_event_without_producer(self) -> None:
        mock_state = MagicMock()
        mock_state.entity_change_stream_producer = None
        edit_headers = EditHeaders(x_edit_summary="test")

        handler = EntityRevertHandler(state=mock_state)
        await handler._publish_change_event("Q42", 11, 5, edit_headers)


class TestEntityRevertHandlerRevertEntity:
    """Tests for EntityRevertHandler.revert_entity orchestrator."""

    def _make_s3_mock(self) -> MagicMock:
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        s3_mock = MagicMock(spec=S3RevisionData)
        s3_mock.revision = {}
        return s3_mock

    @pytest.mark.asyncio
    async def test_revert_entity_success(self) -> None:
        mock_state = MagicMock()
        handler = EntityRevertHandler(state=mock_state)
        request = EntityRevertRequest(to_revision_id=3)
        edit_headers = EditHeaders(x_edit_summary="test revert")

        with (
            patch.object(
                handler, "_resolve_entity_id", new_callable=AsyncMock
            ) as mock_resolve,
            patch.object(
                handler, "_get_target_revision", new_callable=AsyncMock
            ) as mock_target,
            patch.object(
                handler, "_read_target_revision_from_s3", new_callable=AsyncMock
            ) as mock_read_s3,
            patch.object(
                handler, "_get_head_revision", new_callable=AsyncMock
            ) as mock_head,
            patch.object(
                handler, "_store_revision", new_callable=AsyncMock
            ) as mock_store,
            patch.object(
                handler, "_publish_change_event", new_callable=AsyncMock
            ) as mock_publish,
        ):
            mock_resolve.return_value = 42
            mock_target.return_value = MagicMock()
            mock_read_s3.return_value = self._make_s3_mock()
            mock_head.return_value = 10
            mock_store.return_value = 999
            mock_mysql = MagicMock()
            mock_state.mysql_client = mock_mysql
            mock_mysql.user_repository.log_user_activity.return_value = MagicMock(
                success=True
            )

            response = await handler.revert_entity("Q42", request, edit_headers, user_id=123)

        assert isinstance(response, EntityRevertResponse)
        assert response.entity_id == "Q42"
        assert response.new_revision_id == 11
        assert response.reverted_from_revision_id == 10
        mock_resolve.assert_called_once_with("Q42")
        mock_target.assert_called_once_with("Q42", 3, 42)
        mock_read_s3.assert_called_once_with("Q42", 3)
        mock_head.assert_called_once_with(42)
        mock_store.assert_called_once()
        mock_publish.assert_called_once_with("Q42", 11, 10, edit_headers)

    @pytest.mark.asyncio
    async def test_revert_entity_logs_user_activity_success(self) -> None:
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.user_repository.log_user_activity.return_value = MagicMock(
            success=True
        )
        handler = EntityRevertHandler(state=mock_state)
        request = EntityRevertRequest(to_revision_id=1)
        edit_headers = EditHeaders(x_edit_summary="revert")

        with (
            patch.object(
                handler, "_resolve_entity_id", new_callable=AsyncMock
            ) as mock_resolve,
            patch.object(
                handler, "_get_target_revision", new_callable=AsyncMock
            ) as mock_target,
            patch.object(
                handler, "_read_target_revision_from_s3", new_callable=AsyncMock
            ) as mock_read,
            patch.object(
                handler, "_get_head_revision", new_callable=AsyncMock
            ) as mock_head,
            patch.object(
                handler, "_store_revision", new_callable=AsyncMock
            ) as mock_store,
            patch.object(
                handler, "_publish_change_event", new_callable=AsyncMock
            ) as mock_publish,
        ):
            mock_resolve.return_value = 42
            mock_target.return_value = MagicMock()
            mock_read.return_value = self._make_s3_mock()
            mock_head.return_value = 5
            mock_store.return_value = 999

            response = await handler.revert_entity("Q42", request, edit_headers, user_id=456)

        mock_mysql.user_repository.log_user_activity.assert_called_once_with(
            user_id=456,
            activity_type="entity_revert",
            entity_id="Q42",
            revision_id=6,
        )
        assert response.new_revision_id == 6

    @pytest.mark.asyncio
    async def test_revert_entity_logs_user_activity_failure(self) -> None:
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_mysql.user_repository.log_user_activity.return_value = MagicMock(
            success=False, error="DB err"
        )
        handler = EntityRevertHandler(state=mock_state)
        request = EntityRevertRequest(to_revision_id=1)
        edit_headers = EditHeaders(x_edit_summary="revert")

        with (
            patch.object(
                handler, "_resolve_entity_id", new_callable=AsyncMock
            ) as mock_resolve,
            patch.object(
                handler, "_get_target_revision", new_callable=AsyncMock
            ) as mock_target,
            patch.object(
                handler, "_read_target_revision_from_s3", new_callable=AsyncMock
            ) as mock_read,
            patch.object(
                handler, "_get_head_revision", new_callable=AsyncMock
            ) as mock_head,
            patch.object(
                handler, "_store_revision", new_callable=AsyncMock
            ) as mock_store,
            patch.object(
                handler, "_publish_change_event", new_callable=AsyncMock
            ) as mock_publish,
        ):
            mock_resolve.return_value = 42
            mock_target.return_value = MagicMock()
            mock_read.return_value = self._make_s3_mock()
            mock_head.return_value = 5
            mock_store.return_value = 999

            response = await handler.revert_entity("Q42", request, edit_headers, user_id=789)

        assert response.new_revision_id == 6

    @pytest.mark.asyncio
    async def test_revert_entity_skips_user_activity_when_anonymous(self) -> None:
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        handler = EntityRevertHandler(state=mock_state)
        request = EntityRevertRequest(to_revision_id=1)
        edit_headers = EditHeaders(x_edit_summary="revert")

        with (
            patch.object(
                handler, "_resolve_entity_id", new_callable=AsyncMock
            ) as mock_resolve,
            patch.object(
                handler, "_get_target_revision", new_callable=AsyncMock
            ) as mock_target,
            patch.object(
                handler, "_read_target_revision_from_s3", new_callable=AsyncMock
            ) as mock_read,
            patch.object(
                handler, "_get_head_revision", new_callable=AsyncMock
            ) as mock_head,
            patch.object(
                handler, "_store_revision", new_callable=AsyncMock
            ) as mock_store,
            patch.object(
                handler, "_publish_change_event", new_callable=AsyncMock
            ) as mock_publish,
        ):
            mock_resolve.return_value = 42
            mock_target.return_value = MagicMock()
            mock_read.return_value = self._make_s3_mock()
            mock_head.return_value = 5
            mock_store.return_value = 999

            response = await handler.revert_entity("Q42", request, edit_headers, user_id=0)

        mock_mysql.user_repository.log_user_activity.assert_not_called()
        assert response.new_revision_id == 6

    @pytest.mark.asyncio
    async def test_revert_entity_propagates_sub_method_errors(self) -> None:
        mock_state = MagicMock()
        handler = EntityRevertHandler(state=mock_state)
        request = EntityRevertRequest(to_revision_id=3)
        edit_headers = EditHeaders(x_edit_summary="test")

        with patch.object(
            handler, "_resolve_entity_id", new_callable=AsyncMock
        ) as mock_resolve:
            mock_resolve.side_effect = HTTPException(
                status_code=404, detail="Entity not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                await handler.revert_entity("Q999", request, edit_headers, user_id=123)
            assert exc_info.value.status_code == 404
