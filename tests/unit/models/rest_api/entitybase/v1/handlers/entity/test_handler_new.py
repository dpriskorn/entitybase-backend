"""Unit tests for EntityHandler - additional coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.data.infrastructure.s3.enums import EditType, EntityType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes
from models.data.rest_api.v1.entitybase.request.entity.context import (
    ProcessEntityRevisionContext,
    RevisionContext,
)
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    StatementHashResult,
)
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.entitybase.v1.handlers.entity.handler import (
    EntityHandler,
    RevisionResult,
    edit_type_to_change_type,
)
from models.data.infrastructure.stream.change_type import ChangeType


class TestEditTypeToChangeType:
    """Unit tests for edit_type_to_change_type function."""

    def test_manual_create(self) -> None:
        result = edit_type_to_change_type(EditType.MANUAL_CREATE.value)
        assert result == ChangeType.CREATION

    def test_manual_update(self) -> None:
        result = edit_type_to_change_type(EditType.MANUAL_UPDATE.value)
        assert result == ChangeType.EDIT

    def test_redirect_create(self) -> None:
        result = edit_type_to_change_type(EditType.REDIRECT_CREATE.value)
        assert result == ChangeType.REDIRECT

    def test_redirect_revert(self) -> None:
        result = edit_type_to_change_type(EditType.REDIRECT_REVERT.value)
        assert result == ChangeType.UNREDIRECT

    def test_archive_added(self) -> None:
        result = edit_type_to_change_type(EditType.ARCHIVE_ADDED.value)
        assert result == ChangeType.ARCHIVAL

    def test_archive_removed(self) -> None:
        result = edit_type_to_change_type(EditType.ARCHIVE_REMOVED.value)
        assert result == ChangeType.UNARCHIVAL

    def test_lock_added(self) -> None:
        result = edit_type_to_change_type(EditType.LOCK_ADDED.value)
        assert result == ChangeType.LOCK

    def test_lock_removed(self) -> None:
        result = edit_type_to_change_type(EditType.LOCK_REMOVED.value)
        assert result == ChangeType.UNLOCK

    def test_soft_delete(self) -> None:
        result = edit_type_to_change_type(EditType.SOFT_DELETE.value)
        assert result == ChangeType.SOFT_DELETE

    def test_hard_delete(self) -> None:
        result = edit_type_to_change_type(EditType.HARD_DELETE.value)
        assert result == ChangeType.HARD_DELETE

    def test_string_manual_create(self) -> None:
        result = edit_type_to_change_type("manual-create")
        assert result == ChangeType.CREATION

    def test_string_soft_delete(self) -> None:
        result = edit_type_to_change_type("soft-delete")
        assert result == ChangeType.SOFT_DELETE

    def test_unspecified_edit_type(self) -> None:
        result = edit_type_to_change_type(EditType.UNSPECIFIED.value)
        assert result == ChangeType.EDIT

    def test_unknown_string_defaults_to_edit(self) -> None:
        result = edit_type_to_change_type("unknown-type")
        assert result == ChangeType.EDIT


class TestEntityHandlerNew:
    """Additional unit tests for EntityHandler."""

    @pytest.mark.asyncio
    async def test_validate_revision_request_empty_id(self) -> None:
        """Test _validate_revision_request with empty entity ID."""
        ctx = RevisionContext(
            entity_id="",
            request_data={},
            entity_type=EntityType.ITEM,
        )

        from models.rest_api.utils import raise_validation_error

        with pytest.raises(Exception):
            EntityHandler._validate_revision_request(ctx)

    @pytest.mark.asyncio
    async def test_validate_revision_request_valid_id(self) -> None:
        """Test _validate_revision_request with valid entity ID."""
        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
        )

        EntityHandler._validate_revision_request(ctx)

    @pytest.mark.asyncio
    async def test_check_idempotency_new_no_head(self) -> None:
        """Test _check_idempotency_new when head revision is 0."""
        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
            mysql_client=MagicMock(),
            s3_client=MagicMock(),
        )
        ctx.mysql_client.get_head.return_value = 0

        result = await EntityHandler._check_idempotency_new(ctx)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_revision_new_success(self) -> None:
        """Test _create_revision_new successful path."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        mock_mysql.get_head.return_value = 5
        mock_mysql.create_revision.return_value = True

        ctx = RevisionContext(
            entity_id="Q42",
            request_data={"labels": {"en": {"value": "Test"}}},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test edit",
            mysql_client=mock_mysql,
            s3_client=mock_s3,
        )

        hash_result = StatementHashResult(
            statements=[123],
            properties=["P31"],
            property_counts={"P31": 1},
        )

        with patch.object(
            handler, "_hash_terms_new", new_callable=AsyncMock
        ) as mock_hash_terms:
            mock_hash_terms.return_value = HashMaps(
                labels={"en": 111},
                descriptions={},
                aliases={},
            )
            with patch.object(
                handler, "_hash_sitelinks_new", new_callable=AsyncMock
            ) as mock_hash_sitelinks:
                mock_hash_sitelinks.return_value = SitelinkHashes(root={})
                with patch.object(EntityHandler, "_build_revision_data") as mock_build:
                    from models.infrastructure.s3.revision.revision_data import (
                        RevisionData,
                    )

                    mock_build.return_value = MagicMock(spec=RevisionData)
                    with patch.object(
                        EntityHandler,
                        "_store_revision_s3_new",
                        new_callable=AsyncMock,
                    ) as mock_store:
                        mock_store.return_value = 999

                        result = await handler._create_revision_new(ctx, hash_result)

                        assert result.success is True
                        assert result.revision_id == 6
                        mock_mysql.create_revision.assert_called_once_with(
                            entity_id="Q42",
                            entity_data=mock_build.return_value,
                            revision_id=6,
                            content_hash=999,
                            expected_revision_id=0,
                        )

    @pytest.mark.asyncio
    async def test_create_revision_new_conflict(self) -> None:
        """Test _create_revision_new when revision creation fails due to conflict."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        mock_mysql.get_head.return_value = 5
        mock_mysql.create_revision.return_value = False
        mock_mysql.get_head.return_value = 6

        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test edit",
            mysql_client=mock_mysql,
            s3_client=mock_s3,
            base_revision_id=5,
        )

        hash_result = StatementHashResult(
            statements=[],
            properties=[],
            property_counts={},
        )

        with patch.object(
            handler, "_hash_terms_new", new_callable=AsyncMock
        ) as mock_hash_terms:
            mock_hash_terms.return_value = HashMaps(
                labels={}, descriptions={}, aliases={}
            )
            with patch.object(
                handler, "_hash_sitelinks_new", new_callable=AsyncMock
            ) as mock_hash_sitelinks:
                mock_hash_sitelinks.return_value = SitelinkHashes(root={})
                with patch.object(EntityHandler, "_build_revision_data"):
                    with patch.object(
                        EntityHandler,
                        "_store_revision_s3_new",
                        new_callable=AsyncMock,
                    ):
                        result = await handler._create_revision_new(ctx, hash_result)

                        assert result.success is False

    @pytest.mark.asyncio
    async def test_create_revision_new_exception(self) -> None:
        """Test _create_revision_new when an exception occurs."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        mock_mysql.get_head.side_effect = Exception("DB connection failed")

        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
            mysql_client=mock_mysql,
            s3_client=mock_s3,
        )

        hash_result = StatementHashResult(
            statements=[],
            properties=[],
            property_counts={},
        )

        result = await handler._create_revision_new(ctx, hash_result)

        assert result.success is False
        assert "DB connection failed" in result.error

    @pytest.mark.asyncio
    async def test_publish_events_new_streaming_disabled(self) -> None:
        """Test _publish_events_new when streaming is disabled."""
        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
        )
        result = RevisionResult(success=True, revision_id=1)

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.handler.settings"
        ) as mock_settings:
            mock_settings.streaming_enabled = False

            await EntityHandler._publish_events_new(ctx, result)

    @pytest.mark.asyncio
    async def test_publish_events_new_no_producer(self) -> None:
        """Test _publish_events_new when stream producer is not available."""
        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
            stream_producer=None,
        )
        result = RevisionResult(success=True, revision_id=1)

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.handler.settings"
        ) as mock_settings:
            mock_settings.streaming_enabled = True

            await EntityHandler._publish_events_new(ctx, result)

    @pytest.mark.asyncio
    async def test_publish_events_new_producer_exception(self) -> None:
        """Test _publish_events_new when stream producer raises an exception."""
        mock_producer = AsyncMock()
        mock_producer.publish.side_effect = Exception("Kafka unavailable")

        edit_headers = MagicMock()
        edit_headers.x_user_id = 123

        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_UPDATE,
            edit_summary="Test edit",
            stream_producer=mock_producer,
            edit_headers=edit_headers,
        )
        result = RevisionResult(success=True, revision_id=1)

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.handler.settings"
        ) as mock_settings:
            mock_settings.streaming_enabled = True

            await EntityHandler._publish_events_new(ctx, result)
            mock_producer.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_entity_response_no_success(self) -> None:
        """Test _build_entity_response when result is not successful."""
        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
        )
        result = RevisionResult(success=False, error="Something went wrong")

        with pytest.raises(Exception):
            await EntityHandler._build_entity_response(ctx, result)

    @pytest.mark.asyncio
    async def test_build_entity_response_no_revision_id(self) -> None:
        """Test _build_entity_response when revision_id is 0."""
        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
        )
        result = RevisionResult(success=True, revision_id=0)

        with pytest.raises(Exception):
            await EntityHandler._build_entity_response(ctx, result)

    @pytest.mark.asyncio
    async def test_build_entity_response_generic_exception(self) -> None:
        """Test _build_entity_response when S3 raises a generic exception."""
        mock_s3 = MagicMock()
        mock_s3.read_revision.side_effect = Exception("S3 read failed")

        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
            s3_client=mock_s3,
        )
        result = RevisionResult(success=True, revision_id=1)

        with pytest.raises(Exception):
            await EntityHandler._build_entity_response(ctx, result)

    @pytest.mark.asyncio
    async def test_store_revision_s3_new(self) -> None:
        """Test _store_revision_s3_new stores and returns content hash."""
        mock_s3 = MagicMock()

        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.data.infrastructure.s3.entity_state import EntityState
        from models.data.infrastructure.s3.enums import EditData, EditType

        revision_data = MagicMock(spec=RevisionData)
        revision_data.model_dump.return_value = {
            "revision_id": 1,
            "entity_type": "item",
        }

        ctx = RevisionContext(
            entity_id="Q42",
            request_data={},
            entity_type=EntityType.ITEM,
            s3_client=mock_s3,
        )

        content_hash = await EntityHandler._store_revision_s3_new(ctx, revision_data)

        assert isinstance(content_hash, int)
        mock_s3.store_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_revision_data_lexeme_forms_senses(self) -> None:
        """Test _build_revision_data with lexeme entity including forms and senses."""
        mock_state = MagicMock()
        handler = EntityHandler(state=mock_state)

        ctx = RevisionContext(
            entity_id="L123",
            request_data={
                "lemmas": {"en": {"language": "en", "value": "test"}},
                "language": "en",
                "lexical_category": "Q1234",
                "forms": [
                    {
                        "id": "L123-F1",
                        "representations": {"en": {"language": "en", "value": "test"}},
                    }
                ],
                "senses": [
                    {
                        "id": "L123-S1",
                        "glosses": {"en": {"language": "en", "value": "a test"}},
                    }
                ],
            },
            entity_type=EntityType.LEXEME,
        )

        hash_result = StatementHashResult(
            statements=[],
            properties=[],
            property_counts={},
        )
        term_hashes = HashMaps(labels={}, descriptions={}, aliases={})
        sitelink_hashes = SitelinkHashes(root={})

        with patch("models.config.settings.settings") as mock_settings:
            mock_settings.dangling_property_id = "P6104"
            mock_settings.s3_schema_revision_version = "2.0.0"

            result = handler._build_revision_data(
                ctx, hash_result, term_hashes, sitelink_hashes, 1
            )

            assert result.revision_id == 1
            assert result.entity_type == EntityType.LEXEME
            assert result.lemmas == {"en": {"language": "en", "value": "test"}}
            assert result.language == "en"
            assert result.lexical_category == "Q1234"
            assert len(result.forms) > 0
            assert len(result.senses) > 0

    @pytest.mark.asyncio
    async def test_process_entity_revision_new_flow(self) -> None:
        """Test the full process_entity_revision_new flow with mocks."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        handler = EntityHandler(state=mock_state)

        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        ctx = ProcessEntityRevisionContext(
            entity_id="Q42",
            request_data={"labels": {"en": {"value": "Test"}}},
            entity_type=EntityType.ITEM,
            edit_type=EditType.MANUAL_CREATE,
            edit_headers=EditHeaders(x_edit_summary="Create test"),
            is_creation=True,
        )

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "state": {
                    "is_semi_protected": False,
                    "is_locked": False,
                    "is_archived": False,
                    "is_dangling": False,
                    "is_mass_edit_protected": False,
                }
            },
            hash=123,
            created_at="2023-01-01T12:00:00Z",
        )

        mock_mysql.get_head.return_value = 0
        mock_mysql.create_revision.return_value = True
        mock_s3.read_revision.return_value = s3_revision_data

        with patch.object(
            handler, "_process_entity_data_new", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = StatementHashResult(
                statements=[],
                properties=[],
                property_counts={},
            )
            with patch.object(
                handler, "_hash_terms_new", new_callable=AsyncMock
            ) as mock_terms:
                mock_terms.return_value = HashMaps(
                    labels={"en": 111}, descriptions={}, aliases={}
                )
                with patch.object(
                    handler, "_hash_sitelinks_new", new_callable=AsyncMock
                ) as mock_sitelinks:
                    mock_sitelinks.return_value = SitelinkHashes(root={})
                    with patch.object(
                        EntityHandler, "_build_revision_data"
                    ) as mock_build:
                        mock_build.return_value = MagicMock()
                        with patch.object(
                            EntityHandler,
                            "_store_revision_s3_new",
                            new_callable=AsyncMock,
                        ) as mock_store:
                            mock_store.return_value = 999
                            with patch.object(
                                EntityHandler,
                                "_publish_events_new",
                                new_callable=AsyncMock,
                            ):
                                response = await handler.process_entity_revision_new(
                                    ctx
                                )

                                assert response.id == "Q42"

    def test_process_statements_hash_failure(self) -> None:
        """Test process_statements when statement hashing fails."""
        mock_state = MagicMock()
        handler = EntityHandler(state=mock_state)

        from models.data.rest_api.v1.entitybase.request.entity import (
            PreparedRequestData,
        )

        request_data = PreparedRequestData(id="Q42")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.handler.StatementService"
        ) as mock_ss:
            mock_service = MagicMock()
            mock_ss.return_value = mock_service
            hash_operation = MagicMock()
            hash_operation.success = False
            hash_operation.error = "Statement hashing failed"
            mock_service.hash_entity_statements.return_value = hash_operation

            with pytest.raises(Exception):
                handler.process_statements("Q42", request_data, None)

    def test_process_statements_store_failure(self) -> None:
        """Test process_statements when statement storage fails."""
        mock_state = MagicMock()
        handler = EntityHandler(state=mock_state)

        from models.data.rest_api.v1.entitybase.request.entity import (
            PreparedRequestData,
        )

        request_data = PreparedRequestData(id="Q42")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.handler.StatementService"
        ) as mock_ss:
            mock_service = MagicMock()
            mock_ss.return_value = mock_service
            hash_operation = MagicMock()
            hash_operation.success = True
            hash_operation.get_data.return_value = StatementHashResult(
                statements=[123],
                properties=["P31"],
                property_counts={"P31": 1},
            )
            mock_service.hash_entity_statements.return_value = hash_operation
            store_result = MagicMock()
            store_result.success = False
            store_result.error = "Storage failed"
            mock_service.deduplicate_and_store_statements.return_value = store_result

            with pytest.raises(Exception):
                handler.process_statements("Q42", request_data, None)

    def test_process_statements_success(self) -> None:
        """Test process_statements successful path."""
        mock_state = MagicMock()
        handler = EntityHandler(state=mock_state)

        from models.data.rest_api.v1.entitybase.request.entity import (
            PreparedRequestData,
        )

        request_data = PreparedRequestData(id="Q42")

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.handler.StatementService"
        ) as mock_ss:
            mock_service = MagicMock()
            mock_ss.return_value = mock_service
            hash_operation = MagicMock()
            hash_operation.success = True
            hash_operation.get_data.return_value = StatementHashResult(
                statements=[123, 456],
                properties=["P31", "P21"],
                property_counts={"P31": 1, "P21": 1},
            )
            mock_service.hash_entity_statements.return_value = hash_operation
            store_result = MagicMock()
            store_result.success = True
            mock_service.deduplicate_and_store_statements.return_value = store_result

            result = handler.process_statements("Q42", request_data, None)

            assert len(result.statements) == 2
            assert result.properties == ["P31", "P21"]
