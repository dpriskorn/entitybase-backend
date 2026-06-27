"""Unit tests for EntityStatementService."""

from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.rest_api.entitybase.v1.services.entity_statement_service import (
    EntityStatementService,
    _PropertyCountHelper,
)


def _make_edit_headers() -> EditHeaders:
    """Create standard edit headers for testing."""
    return EditHeaders(
        x_edit_summary="test edit",
    )


class TestEntityStatementService:
    """Unit tests for EntityStatementService."""

    # add_property tests

    @pytest.mark.asyncio
    async def test_add_property_new_property(self) -> None:
        """Test adding claims to a new property."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql

        service = EntityStatementService(state=mock_state)
        current_data = MagicMock()
        current_data.data = {"claims": {}}

        service._merge_claims(current_data.data, "P31", [{"test": "data"}])

        assert "P31" in current_data.data["claims"]
        assert current_data.data["claims"]["P31"] == [{"test": "data"}]

    # remove_statement tests

    @pytest.mark.asyncio
    async def test_remove_statement_decrements_ref_count(self) -> None:
        """Test that remove_statement decrements reference count."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_mysql.cursor = mock_cursor

        service = EntityStatementService(state=mock_state)
        service._decrement_statement_ref_count("12345")

        mock_cursor.execute.assert_called()

    def test_decrement_statement_ref_count_failure(self) -> None:
        """Test that _decrement_statement_ref_count raises on failure."""
        from fastapi import HTTPException
        from models.data.common import OperationResult

        mock_state = MagicMock()
        mock_repo = MagicMock()
        mock_repo.decrement_ref_count.return_value = OperationResult(
            success=False, error="DB error"
        )

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.StatementRepository",
            return_value=mock_repo,
        ):
            service = EntityStatementService(state=mock_state)

            with pytest.raises(HTTPException) as exc_info:
                service._decrement_statement_ref_count("12345")

            assert exc_info.value.status_code == 500
            assert "DB error" in str(exc_info.value.detail)

    # patch_statement tests

    @pytest.mark.asyncio
    async def test_patch_statement_not_found(self) -> None:
        """Test patching statement when it doesn't exist."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql

        service = EntityStatementService(state=mock_state)
        current_data = MagicMock()
        current_data.data = {"claims": {}}

        replaced = service._find_and_replace_statement(
            current_data.data, "99999", {"new": "data"}
        )

        assert replaced is False

    # _validate_property_id (static)
    def test_validate_property_id_valid(self) -> None:
        """Test validating valid property ID."""
        service = EntityStatementService(state=MagicMock())
        service._validate_property_id("P31")
        assert True  # No exception raised

    # _merge_claims (static)
    def test_merge_claims_new_property(self) -> None:
        """Test merging claims for new property."""
        current_data = {"claims": {}}
        EntityStatementService._merge_claims(current_data, "P31", [{"test": "data"}])

        assert "P31" in current_data["claims"]
        assert current_data["claims"]["P31"] == [{"test": "data"}]

    def test_merge_claims_existing_property(self) -> None:
        """Test merging claims for existing property."""
        current_data = {"claims": {"P31": [{"old": "data"}]}}
        EntityStatementService._merge_claims(current_data, "P31", [{"new": "data"}])

        assert len(current_data["claims"]["P31"]) == 2
        assert {"new": "data"} in current_data["claims"]["P31"]

    def test_merge_claims_no_claims_key(self) -> None:
        """Test merging claims when no claims key exists."""
        current_data = {}
        EntityStatementService._merge_claims(current_data, "P31", [{"test": "data"}])

        assert "claims" in current_data
        assert current_data["claims"]["P31"] == [{"test": "data"}]

    def test_merge_claims_empty_claims_dict(self) -> None:
        """Test merging claims when claims dict is empty."""
        current_data = {"claims": {}}
        EntityStatementService._merge_claims(current_data, "P31", [{"test": "data"}])

        assert current_data["claims"]["P31"] == [{"test": "data"}]

    # _PropertyCountHelper tests

    def test_recalculate_property_counts_removes_property(self) -> None:
        """Test recalculating removes property when count is 0."""
        mock_revision = MagicMock()
        mock_revision.properties = ["P31", "P279"]
        mock_property_counts = MagicMock()
        mock_property_counts.root = {"P31": 1, "P279": 3}
        mock_revision.property_counts = mock_property_counts

        result = _PropertyCountHelper.recalculate_property_counts(mock_revision, 0)

        assert "P31" not in result.properties
        assert "P31" not in result.property_counts.root

    def test_recalculate_property_counts_keeps_property_when_count_above_zero(
        self,
    ) -> None:
        """Test recalculating keeps property when count is still above 0."""
        mock_revision = MagicMock()
        mock_revision.properties = ["P31", "P279"]
        mock_property_counts = MagicMock()
        mock_property_counts.root = {"P31": 2, "P279": 3}
        mock_revision.property_counts = mock_property_counts

        result = _PropertyCountHelper.recalculate_property_counts(mock_revision, 0)

        assert "P31" in result.properties
        assert result.property_counts.root["P31"] == 1

    # _find_and_replace_statement (static)
    def test_find_and_replace_statement_found(self) -> None:
        """Test finding and replacing statement."""
        current_data = {
            "claims": {"P31": [{"mainsnak": {"datavalue": {"value": "Q146"}}}]}
        }
        from models.internal_representation.statement_hasher import StatementHasher

        old_stmt = {"mainsnak": {"datavalue": {"value": "Q146"}}}
        stmt_hash = StatementHasher.compute_hash(old_stmt)

        replaced = EntityStatementService._find_and_replace_statement(
            current_data, str(stmt_hash), {"mainsnak": {"datavalue": {"value": "Q515"}}}
        )

        assert replaced is True
        assert (
            current_data["claims"]["P31"][0]["mainsnak"]["datavalue"]["value"] == "Q515"
        )

    def test_find_and_replace_statement_not_found(self) -> None:
        """Test finding statement when hash not found."""
        current_data = {"claims": {"P31": [{"test": "data"}]}}

        replaced = EntityStatementService._find_and_replace_statement(
            current_data, "99999", {"new": "data"}
        )

        assert replaced is False

    # _fetch_revision_data

    # _store_updated_revision

    def test_validate_property_id_invalid_format(self) -> None:
        """Test validating invalid property ID format."""
        from fastapi import HTTPException

        service = EntityStatementService(state=MagicMock())

        with pytest.raises(HTTPException) as exc_info:
            service._validate_property_id("Q31")

        assert exc_info.value.status_code == 400

    def test_validate_property_id_not_numeric(self) -> None:
        """Test validating property ID with non-numeric suffix."""
        from fastapi import HTTPException

        service = EntityStatementService(state=MagicMock())

        with pytest.raises(HTTPException) as exc_info:
            service._validate_property_id("Pabc")

        assert exc_info.value.status_code == 400

    def test_validate_property_id_empty(self) -> None:
        """Test validating empty property ID."""
        from fastapi import HTTPException

        service = EntityStatementService(state=MagicMock())

        with pytest.raises(HTTPException) as exc_info:
            service._validate_property_id("")

        assert exc_info.value.status_code == 400

    def test_validate_property_exists_not_property(self) -> None:
        """Test validating entity that is not a property."""
        from fastapi import HTTPException

        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_response = MagicMock()
        mock_response.entity_data.revision = {"entity_type": "item"}
        mock_read_handler.get_entity.return_value = mock_response

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
            return_value=mock_read_handler,
        ):
            service = EntityStatementService(state=mock_state)

            with pytest.raises(HTTPException) as exc_info:
                service._validate_property_exists("Q31")

            assert exc_info.value.status_code == 400

    def test_validate_property_exists_not_found(self) -> None:
        """Test validating non-existent property."""
        from fastapi import HTTPException

        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_read_handler.get_entity.side_effect = Exception("Not found")

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
            return_value=mock_read_handler,
        ):
            service = EntityStatementService(state=mock_state)

            with pytest.raises(HTTPException) as exc_info:
                service._validate_property_exists("P99999")

            assert exc_info.value.status_code == 400

    def test_fetch_current_entity_data_success(self) -> None:
        """Test fetching current entity data successfully."""
        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_response = MagicMock()
        mock_response.entity_data.revision = {"id": "Q1", "type": "item"}
        mock_read_handler.get_entity.return_value = mock_response

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
            return_value=mock_read_handler,
        ):
            service = EntityStatementService(state=mock_state)
            result = service._fetch_current_entity_data("Q1")

            assert result.data["id"] == "Q1"

    def test_fetch_current_entity_data_exception(self) -> None:
        """Test fetching current entity data with exception."""
        from fastapi import HTTPException

        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_read_handler.get_entity.side_effect = Exception("Error")

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
            return_value=mock_read_handler,
        ):
            service = EntityStatementService(state=mock_state)

            with pytest.raises(HTTPException) as exc_info:
                service._fetch_current_entity_data("Q1")

            assert exc_info.value.status_code == 400

    def test_fetch_current_entity_not_found(self) -> None:
        """Test fetching current entity when not found."""
        from fastapi import HTTPException
        from models.infrastructure.s3.exceptions import S3NotFoundError

        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_read_handler.get_entity.side_effect = S3NotFoundError("Not found")

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
            return_value=mock_read_handler,
        ):
            service = EntityStatementService(state=mock_state)

            with pytest.raises(HTTPException) as exc_info:
                service._fetch_current_entity("Q1")

            assert exc_info.value.status_code == 404

    def test_fetch_current_entity_exception(self) -> None:
        """Test fetching current entity with exception."""
        from fastapi import HTTPException

        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_read_handler.get_entity.side_effect = Exception("Error")

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
            return_value=mock_read_handler,
        ):
            service = EntityStatementService(state=mock_state)

            with pytest.raises(HTTPException) as exc_info:
                service._fetch_current_entity("Q1")

            assert exc_info.value.status_code == 400

    def test_remove_statement_from_revision_no_statements(self) -> None:
        """Test removing statement when there are no statements."""
        mock_revision = MagicMock()
        mock_revision.hashes = MagicMock()
        mock_revision.hashes.statements = None

        result = EntityStatementService._remove_statement_from_revision(
            mock_revision, "12345"
        )

        assert result.success is False
        assert "No statements" in result.error

    def test_remove_statement_from_revision_hash_not_found(self) -> None:
        """Test removing statement when hash not found."""
        mock_revision = MagicMock()
        mock_hashes = MagicMock()
        mock_hashes.statements = MagicMock()
        mock_hashes.statements.root = [11111, 22222]
        mock_revision.hashes = mock_hashes
        mock_revision.properties = ["P31"]
        mock_revision.property_counts = MagicMock()
        mock_revision.property_counts.root = {"P31": 2}

        result = EntityStatementService._remove_statement_from_revision(
            mock_revision, "99999"
        )

        assert result.success is False
        assert "not found" in result.error

    def test_remove_statement_from_revision_invalid_hash(self) -> None:
        """Test removing statement with invalid hash format."""
        mock_revision = MagicMock()
        mock_revision.hashes = MagicMock()
        mock_revision.hashes.statements = MagicMock()
        mock_revision.hashes.statements.root = []

        result = EntityStatementService._remove_statement_from_revision(
            mock_revision, "invalid"
        )

        assert result.success is False
        assert "Invalid" in result.error

    def test_remove_statement_from_revision_success(self) -> None:
        """Test removing statement successfully."""
        mock_revision = MagicMock()
        mock_hashes = MagicMock()
        mock_hashes.statements = MagicMock()
        mock_hashes.statements.root = [11111, 22222]
        mock_revision.hashes = mock_hashes
        mock_revision.properties = ["P31"]
        mock_revision.property_counts = MagicMock()
        mock_revision.property_counts.root = {"P31": 2}

        result = EntityStatementService._remove_statement_from_revision(
            mock_revision, "11111"
        )

        assert result.success is True
        assert 11111 not in mock_revision.hashes.statements.root

    # Async method integration tests for EntityStatementService

    @pytest.mark.asyncio
    async def test_add_property_success(self) -> None:
        """Test add_property successfully adds claims and returns revision ID."""
        from models.data.rest_api.v1.entitybase.request import AddPropertyRequest
        from models.data.rest_api.v1.entitybase.response import (
            RevisionIdResult,
            EntityResponse,
        )

        mock_state = MagicMock()
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 42

        service = EntityStatementService(state=mock_state)

        with (
            patch.object(
                service,
                "_validate_property_exists",
                return_value=None,
            ),
            patch.object(
                service,
                "_fetch_current_entity_data",
            ) as mock_fetch,
            patch.object(
                service,
                "_process_entity_update",
                new=AsyncMock(return_value=mock_response),
            ),
        ):
            mock_fetch.return_value.data = {"claims": {}}
            request = AddPropertyRequest(claims=[{"test": "data"}])
            edit_headers = _make_edit_headers()
            result = await service.add_property(
                "Q1",
                "P31",
                request,
                edit_headers,
            )

        assert result.success is True
        assert isinstance(result.data, RevisionIdResult)
        assert result.data.revision_id == 42

    @pytest.mark.asyncio
    async def test_remove_statement_success(self) -> None:
        """Test remove_statement successfully removes and returns revision ID."""
        from models.data.rest_api.v1.entitybase.response import (
            RevisionIdResult,
        )

        mock_state = MagicMock()
        mock_state.mysql_client = MagicMock()
        mock_state.mysql_client.get_head.return_value = 5

        service = EntityStatementService(state=mock_state)
        mock_revision_data = MagicMock()

        with (
            patch.object(
                service,
                "_fetch_revision_data",
                return_value=mock_revision_data,
            ),
            patch.object(
                service,
                "_remove_statement_from_revision",
                return_value=OperationResult(success=True),
            ),
            patch.object(
                service,
                "_decrement_statement_ref_count",
                return_value=None,
            ),
            patch.object(
                service,
                "_store_updated_revision",
                new=AsyncMock(return_value=99),
            ),
        ):
            edit_headers = _make_edit_headers()
            result = await service.remove_statement("Q1", "12345", edit_headers)

        assert result.success is True
        assert isinstance(result.data, RevisionIdResult)
        assert result.data.revision_id == 99

    @pytest.mark.asyncio
    async def test_remove_statement_not_found(self) -> None:
        """Test remove_statement when statement is not found."""
        mock_state = MagicMock()
        mock_state.mysql_client = MagicMock()
        mock_state.mysql_client.get_head.return_value = 5

        service = EntityStatementService(state=mock_state)
        mock_revision_data = MagicMock()

        with (
            patch.object(
                service,
                "_fetch_revision_data",
                return_value=mock_revision_data,
            ),
            patch.object(
                service,
                "_remove_statement_from_revision",
                return_value=OperationResult(
                    success=False, error="Statement hash not found"
                ),
            ),
        ):
            edit_headers = _make_edit_headers()
            result = await service.remove_statement("Q1", "99999", edit_headers)

        assert result.success is False
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_add_statement_success(self) -> None:
        """Test add_statement successfully adds a single statement."""
        from models.data.rest_api.v1.entitybase.request import AddStatementRequest
        from models.data.rest_api.v1.entitybase.response import (
            RevisionIdResult,
            EntityResponse,
        )

        mock_state = MagicMock()
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 77

        service = EntityStatementService(state=mock_state)

        with (
            patch.object(
                service,
                "_validate_property_exists",
                return_value=None,
            ),
            patch.object(
                service,
                "_fetch_current_entity_data",
            ) as mock_fetch,
            patch.object(
                service,
                "_process_entity_update",
                new=AsyncMock(return_value=mock_response),
            ),
        ):
            mock_fetch.return_value.data = {"claims": {}}
            request = AddStatementRequest(
                claim={
                    "property": {"id": "P31"},
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {"type": "string", "value": "test"},
                    },
                }
            )
            edit_headers = _make_edit_headers()
            result = await service.add_statement("Q1", request, edit_headers)

        assert result.success is True
        assert isinstance(result.data, RevisionIdResult)
        assert result.data.revision_id == 77

    @pytest.mark.asyncio
    async def test_add_statement_missing_property_id(self) -> None:
        """Test add_statement raises error when claim has no property ID."""
        from fastapi import HTTPException
        from models.data.rest_api.v1.entitybase.request import AddStatementRequest

        service = EntityStatementService(state=MagicMock())
        request = AddStatementRequest(claim={"mainsnak": {"snaktype": "value"}})
        edit_headers = _make_edit_headers()

        with pytest.raises(HTTPException) as exc_info:
            await service.add_statement("Q1", request, edit_headers)

        assert exc_info.value.status_code == 400
        assert "property ID" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_patch_statement_success(self) -> None:
        """Test patch_statement successfully replaces a statement."""
        from models.data.rest_api.v1.entitybase.request import PatchStatementRequest
        from models.data.rest_api.v1.entitybase.response import (
            RevisionIdResult,
            EntityResponse,
        )

        mock_state = MagicMock()
        mock_response = MagicMock(spec=EntityResponse)
        mock_response.revision_id = 55

        service = EntityStatementService(state=mock_state)

        with (
            patch.object(
                service,
                "_fetch_current_entity_data",
            ) as mock_fetch,
            patch.object(
                service,
                "_find_and_replace_statement",
                return_value=True,
            ),
            patch.object(
                service,
                "_process_entity_update",
                new=AsyncMock(return_value=mock_response),
            ),
        ):
            mock_fetch.return_value.data = {"claims": {"P31": [{"test": "data"}]}}
            request = PatchStatementRequest(claim={"new": "data"})
            edit_headers = _make_edit_headers()
            result = await service.patch_statement("Q1", "12345", request, edit_headers)

        assert result.success is True
        assert isinstance(result.data, RevisionIdResult)
        assert result.data.revision_id == 55

    # _fetch_revision_data tests

    def test_fetch_revision_data_success(self) -> None:
        """Test fetching revision data successfully."""
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        revision_dict = {
            "revision_id": 42,
            "entity_type": "item",
            "edit": {
                "type": "manual-update",
                "user_id": 0,
                "mass": False,
                "summary": "test edit",
                "at": "2024-01-01T00:00:00Z",
            },
            "hashes": {
                "statements": [],
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "sitelinks": {},
            },
        }
        s3_data = S3RevisionData(
            schema="1.0.0",
            revision=revision_dict,
            hash=12345,
            created_at="2024-01-01T00:00:00Z",
        )
        mock_s3.read_revision.return_value = s3_data

        service = EntityStatementService(state=mock_state)
        result = service._fetch_revision_data("Q1", 42)

        assert result.revision_id == 42

    def test_fetch_revision_data_s3_not_found(self) -> None:
        """Test fetching revision data when S3 raises not found."""
        from fastapi import HTTPException
        from models.infrastructure.s3.exceptions import S3NotFoundError

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.read_revision.side_effect = S3NotFoundError("Not found")

        service = EntityStatementService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            service._fetch_revision_data("Q1", 42)

        assert exc_info.value.status_code == 404

    def test_fetch_revision_data_generic_error(self) -> None:
        """Test fetching revision data when a generic error occurs."""
        from fastapi import HTTPException

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.read_revision.side_effect = Exception("Connection error")

        service = EntityStatementService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            service._fetch_revision_data("Q1", 42)

        assert exc_info.value.status_code == 400
        assert "Connection error" in exc_info.value.detail

    # _store_updated_revision tests

    @pytest.mark.asyncio
    async def test_store_updated_revision_success(self, mocker) -> None:
        """Test storing updated revision successfully."""
        from models.data.infrastructure.s3.enums import EditType
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
        from models.infrastructure.s3.revision.revision_data import RevisionData

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_mysql = MagicMock()
        mock_state.s3_client = mock_s3
        mock_state.mysql_client = mock_mysql
        mock_mysql.create_revision.return_value = True
        mocker.patch(
            "rapidhash.rapidhash",
            return_value=12345,
        )

        revision_data = RevisionData(
            revision_id=41,
            entity_type="item",
            edit={
                "type": "unspecified",
                "user_id": 0,
                "summary": "base",
                "at": "2024-01-01T00:00:00Z",
            },
            hashes=HashMaps(),
        )
        edit_headers = EditHeaders(**{"X-Edit-Summary": "test summary"})

        service = EntityStatementService(state=mock_state)
        result = await service._store_updated_revision(
            revision_data=revision_data,
            entity_id="Q1",
            head_revision_id=41,
            edit_headers=edit_headers,
        )

        assert result == 42
        assert revision_data.revision_id == 42
        assert revision_data.edit.edit_type == EditType.MANUAL_UPDATE
        assert revision_data.edit.edit_summary == "test summary"
        assert revision_data.edit.user_id == 5
        mock_s3.store_revision.assert_called_once()
        mock_mysql.create_revision.assert_called_once_with(
            entity_id="Q1",
            entity_data=revision_data,
            revision_id=42,
            content_hash=12345,
            expected_revision_id=41,
        )

    @pytest.mark.asyncio
    async def test_store_updated_revision_conflict(self, mocker) -> None:
        """Test storing updated revision when a conflict occurs."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
        from models.infrastructure.s3.revision.revision_data import RevisionData

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_mysql = MagicMock()
        mock_state.s3_client = mock_s3
        mock_state.mysql_client = mock_mysql
        mock_mysql.create_revision.return_value = False
        mock_mysql.get_head.return_value = 50
        mocker.patch(
            "rapidhash.rapidhash",
            return_value=12345,
        )

        revision_data = RevisionData(
            revision_id=41,
            entity_type="item",
            edit={
                "type": "unspecified",
                "user_id": 0,
                "summary": "base",
                "at": "2024-01-01T00:00:00Z",
            },
            hashes=HashMaps(),
        )
        edit_headers = EditHeaders(**{"X-Edit-Summary": "test summary"})

        service = EntityStatementService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            await service._store_updated_revision(
                revision_data=revision_data,
                entity_id="Q1",
                head_revision_id=41,
                edit_headers=edit_headers,
            )

        assert exc_info.value.status_code == 400
        assert "Conflict" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_store_updated_revision_generic_error(self, mocker) -> None:
        """Test storing updated revision when a generic error occurs."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
        from models.infrastructure.s3.revision.revision_data import RevisionData

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.store_revision.side_effect = Exception("S3 is down")
        mocker.patch(
            "rapidhash.rapidhash",
            return_value=12345,
        )

        revision_data = RevisionData(
            revision_id=41,
            entity_type="item",
            edit={
                "type": "unspecified",
                "user_id": 0,
                "summary": "base",
                "at": "2024-01-01T00:00:00Z",
            },
            hashes=HashMaps(),
        )
        edit_headers = EditHeaders(**{"X-Edit-Summary": "test summary"})

        service = EntityStatementService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            await service._store_updated_revision(
                revision_data=revision_data,
                entity_id="Q1",
                head_revision_id=41,
                edit_headers=edit_headers,
            )

        assert exc_info.value.status_code == 400
        assert "S3 is down" in exc_info.value.detail

    # --- Coverage edge cases ---

    @pytest.mark.asyncio
    async def test_patch_statement_not_found_path(self) -> None:
        """Line 164: patch_statement returns error when statement not found."""
        from models.rest_api.entitybase.v1.services.entity_statement_service import (
            EntityStatementService,
        )

        mock_state = MagicMock()
        service = EntityStatementService(state=mock_state)

        with (
            patch.object(
                service,
                "_fetch_current_entity_data",
            ) as mock_fetch,
            patch.object(
                service,
                "_find_and_replace_statement",
                return_value=False,
            ),
        ):
            mock_fetch.return_value.data = {"claims": {}}
            request = MagicMock()
            edit_headers = _make_edit_headers()
            result = await service.patch_statement("Q1", "99999", request, edit_headers)

            assert result.success is False
            assert "Statement not found" in str(result.error)

    def test_validate_property_exists_happy_path(self) -> None:
        """Line 189->exit: entity_type == 'property' returns without error."""
        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_response = MagicMock()
        mock_response.entity_data.revision = {"entity_type": "property"}
        mock_read_handler.get_entity.return_value = mock_response

        with patch(
            "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
            return_value=mock_read_handler,
        ):
            service = EntityStatementService(state=mock_state)
            service._validate_property_exists("P31")
            assert True

    def test_fetch_revision_data_invalid_type(self) -> None:
        """Line 223: non-S3RevisionData type raises validation error."""
        from fastapi import HTTPException

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.read_revision.return_value = {"not": "S3RevisionData"}

        service = EntityStatementService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            service._fetch_revision_data("Q1", 42)

        # Caught by outer except Exception and re-raised as 400
        assert exc_info.value.status_code == 400

    def test_fetch_revision_data_old_edit_format(self) -> None:
        """Lines 225-232: old-format edit keys are renamed."""
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        revision_dict = {
            "revision_id": 42,
            "entity_type": "item",
            "edit": {
                "edit_type": "manual-update",
                "edit_summary": "old format",
                "is_mass_edit": True,
                "user_id": 0,
                "at": "2024-01-01T00:00:00Z",
            },
            "hashes": {
                "statements": [],
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "sitelinks": {},
            },
        }
        s3_data = S3RevisionData(
            schema="1.0.0",
            revision=revision_dict,
            hash=12345,
            created_at="2024-01-01T00:00:00Z",
        )
        mock_s3.read_revision.return_value = s3_data

        service = EntityStatementService(state=mock_state)
        result = service._fetch_revision_data("Q1", 42)

        assert result.revision_id == 42

    def test_find_and_replace_statement_no_claims_key(self) -> None:
        """Line 357->367: no 'claims' key in current_data."""
        current_data = {"something_else": {}}

        replaced = EntityStatementService._find_and_replace_statement(
            current_data, "12345", {"new": "data"}
        )

        assert replaced is False

    @pytest.mark.asyncio
    async def test_process_entity_update_success(self) -> None:
        """Lines 377-393: _process_entity_update with mocked deps."""
        from models.rest_api.entitybase.v1.services.entity_statement_service import (
            EntityStatementService,
        )

        mock_state = MagicMock()
        mock_read_handler = MagicMock()
        mock_response = MagicMock()
        mock_response.revision_id = 42
        mock_response.entity_data.revision = {"entity_type": "item"}
        mock_read_handler.get_entity.return_value = mock_response

        mock_entity_handler = MagicMock()
        mock_entity_handler.process_entity_revision_new = AsyncMock(
            return_value=mock_response
        )

        with (
            patch(
                "models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler",
                return_value=mock_read_handler,
            ),
            patch(
                "models.rest_api.entitybase.v1.services.entity_statement_service.EntityHandler",
                return_value=mock_entity_handler,
            ),
        ):
            service = EntityStatementService(state=mock_state)
            edit_headers = _make_edit_headers()
            result = await service._process_entity_update(
                "Q1",
                {"claims": {"P31": [{"test": "data"}]}},
                edit_headers,
                None,
            )

        assert result.revision_id == 42

    def test_fetch_revision_data_no_edit_key(self) -> None:
        """Line 225->233: revision_data without 'edit' key hits False branch."""
        from fastapi import HTTPException
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        revision_dict = {
            "revision_id": 42,
            "entity_type": "item",
            "hashes": {
                "statements": [],
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "sitelinks": {},
            },
        }
        s3_data = S3RevisionData(
            schema="1.0.0",
            revision=revision_dict,
            hash=12345,
            created_at="2024-01-01T00:00:00Z",
        )
        mock_s3.read_revision.return_value = s3_data

        service = EntityStatementService(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            service._fetch_revision_data("Q1", 42)

        assert exc_info.value.status_code == 400
