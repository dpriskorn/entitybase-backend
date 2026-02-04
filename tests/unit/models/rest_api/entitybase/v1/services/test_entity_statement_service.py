"""Unit tests for EntityStatementService."""

from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.rest_api.entitybase.v1.services.entity_statement_service import (
    EntityStatementService,
    _PropertyCountHelper,
)


class TestEntityStatementService:
    """Unit tests for EntityStatementService."""

    # add_property tests
    @pytest.mark.asyncio
    async def test_add_property_success(self) -> None:
        """Test adding claims to a property successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_read_handler = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.user_repository = MagicMock()
        mock_vitess.user_repository.log_user_activity.return_value = MagicMock(success=True)

        service = EntityStatementService(state=mock_state)

        with patch(
            'models.rest_api.entitybase.v1.services.entity_statement_service.EntityReadHandler',
            return_value=mock_read_handler
        ):
            with patch.object(service, '_process_entity_update', new_callable=AsyncMock) as mock_update:
                mock_response = MagicMock()
                mock_response.rev_id = 3
                mock_update.return_value = mock_response

                request = MagicMock()
                request.claims = [{"test": "data"}]

                result = await service.add_property(
                    "Q42",
                    "P31",
                    request,
                    EditHeaders(x_user_id=1, x_edit_summary="Add property"),
                )

                assert result.success
                assert result.data.revision_id == 3

    @pytest.mark.asyncio
    async def test_add_property_new_property(self) -> None:
        """Test adding claims to a new property."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        service = EntityStatementService(state=mock_state)
        current_data = MagicMock()
        current_data.data = {"claims": {}}

        service._merge_claims(current_data.data, "P31", [{"test": "data"}])

        assert "P31" in current_data.data["claims"]
        assert current_data.data["claims"]["P31"] == [{"test": "data"}]

    @pytest.mark.asyncio
    async def test_add_property_invalid_property_id(self) -> None:
        """Test adding property with invalid ID format."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        service = EntityStatementService(state=mock_state)

        with pytest.raises(ValueError):
            await service.add_property(
                "Q42",
                "INVALID",
                MagicMock(),
                EditHeaders(x_user_id=1, x_edit_summary="Test"),
            )

    @pytest.mark.asyncio
    async def test_add_property_not_exist(self) -> None:
        """Test adding property when it doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        service = EntityStatementService(state=mock_state)

        with pytest.raises(ValueError):
            await service.add_property(
                "Q42",
                "P31",
                MagicMock(),
                EditHeaders(x_user_id=1, x_edit_summary="Test"),
            )

    # remove_statement tests
    @pytest.mark.asyncio
    async def test_remove_statement_success(self) -> None:
        """Test removing a statement by hash successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.get_head.return_value = 2
        mock_s3.read_revision.return_value = MagicMock()

        service = EntityStatementService(state=mock_state)

        with patch.object(service, '_remove_statement_from_revision') as mock_remove:
            mock_remove.return_value = OperationResult(success=True)

            with patch.object(service, '_decrement_statement_ref_count'):
                with patch.object(service, '_store_updated_revision', new_callable=AsyncMock, return_value=3):
                    result = await service.remove_statement(
                        "Q42",
                        "12345",
                        EditHeaders(x_user_id=1, x_edit_summary="Remove statement"),
                    )

                    assert result.success
                    assert result.data.revision_id == 3

    @pytest.mark.asyncio
    async def test_remove_statement_not_found(self) -> None:
        """Test removing statement when hash not found."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.get_head.return_value = 2
        mock_s3.read_revision.return_value = MagicMock()

        service = EntityStatementService(state=mock_state)

        with patch.object(service, '_remove_statement_from_revision') as mock_remove:
            mock_remove.return_value = OperationResult(
                success=False, error="Statement not found"
            )

            result = await service.remove_statement(
                "Q42",
                "99999",
                EditHeaders(x_user_id=1, x_edit_summary="Remove statement"),
            )

            assert not result.success

    @pytest.mark.asyncio
    async def test_remove_statement_decrements_ref_count(self) -> None:
        """Test that remove_statement decrements reference count."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_stmt_repo = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_vitess.decrement_ref_count = mock_vitess.statement_repository.decrement_ref_count = mock_stmt_repo.decrement_ref_count
        mock_stmt_repo.decrement_ref_count.return_value = OperationResult(success=True)

        service = EntityStatementService(state=mock_state)
        service._decrement_statement_ref_count("12345")

        mock_stmt_repo.decrement_ref_count.assert_called_once_with(12345)

    # patch_statement tests
    @pytest.mark.asyncio
    async def test_patch_statement_success(self) -> None:
        """Test patching (replacing) a statement successfully."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        service = EntityStatementService(state=mock_state)

        with patch.object(service, '_process_entity_update', new_callable=AsyncMock) as mock_update:
            mock_response = MagicMock()
            mock_response.rev_id = 3
            mock_update.return_value = mock_response

            result = await service.patch_statement(
                "Q42",
                "12345",
                MagicMock(claim={"new": "data"}),
                EditHeaders(x_user_id=1, x_edit_summary="Patch statement"),
            )

            assert result.success
            assert result.data.revision_id == 3

    @pytest.mark.asyncio
    async def test_patch_statement_not_found(self) -> None:
        """Test patching statement when it doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

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

    def test_validate_property_id_no_prefix(self) -> None:
        """Test validating property ID without P prefix."""
        service = EntityStatementService(state=MagicMock())
        with pytest.raises(ValueError):
            service._validate_property_id("31")

    def test_validate_property_id_non_digit(self) -> None:
        """Test validating property ID with non-numeric suffix."""
        service = EntityStatementService(state=MagicMock())
        with pytest.raises(ValueError):
            service._validate_property_id("PAB")

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

    # _PropertyCountHelper tests
    def test_recalculate_property_counts_decrements(self) -> None:
        """Test recalculating property counts decrements count."""
        mock_revision = MagicMock()
        mock_revision.properties = ["P31", "P279"]
        mock_revision.property_counts = {"P31": 2, "P279": 3}

        result = _PropertyCountHelper.recalculate_property_counts(mock_revision, 2)

        assert "P31" in result.properties
        assert result.property_counts.root["P31"] == 1

    def test_recalculate_property_counts_removes_property(self) -> None:
        """Test recalculating removes property when count is 0."""
        mock_revision = MagicMock()
        mock_revision.properties = ["P31", "P279"]
        mock_revision.property_counts = {"P31": 1, "P279": 3}

        result = _PropertyCountHelper.recalculate_property_counts(mock_revision, 0)

        assert "P31" not in result.properties
        assert "P31" not in result.property_counts.root

    def test_recalculate_property_counts_multiple_properties(self) -> None:
        """Test recalculating with multiple properties."""
        mock_revision = MagicMock()
        mock_revision.properties = ["P31", "P279", "P21"]
        mock_revision.property_counts = {"P31": 1, "P279": 2, "P21": 1}

        result = _PropertyCountHelper.recalculate_property_counts(mock_revision, 3)

        assert len(result.properties) == 3
        assert result.property_counts.root["P279"] == 1

    # _find_and_replace_statement (static)
    def test_find_and_replace_statement_found(self) -> None:
        """Test finding and replacing statement."""
        current_data = {
            "claims": {
                "P31": [{"mainsnak": {"datavalue": {"value": "Q146"}}}]
            }
        }
        from models.internal_representation.statement_hasher import StatementHasher
        old_stmt = {"mainsnak": {"datavalue": {"value": "Q146"}}}
        stmt_hash = StatementHasher.compute_hash(old_stmt)

        replaced = EntityStatementService._find_and_replace_statement(
            current_data, str(stmt_hash), {"mainsnak": {"datavalue": {"value": "Q515"}}}
        )

        assert replaced is True
        assert current_data["claims"]["P31"][0]["mainsnak"]["datavalue"]["value"] == "Q515"

    def test_find_and_replace_statement_not_found(self) -> None:
        """Test finding statement when hash not found."""
        current_data = {"claims": {"P31": [{"test": "data"}]}}

        replaced = EntityStatementService._find_and_replace_statement(
            current_data, "99999", {"new": "data"}
        )

        assert replaced is False

    # _fetch_revision_data
    def test_fetch_revision_data_success(self) -> None:
        """Test fetching revision data from S3."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.read_revision.return_value = MagicMock(revision={})

        service = EntityStatementService(state=mock_state)

        revision_data = service._fetch_revision_data("Q42", 2)

        assert revision_data is not None
        mock_s3.read_revision.assert_called_once_with("Q42", 2)

    def test_fetch_revision_data_invalid_type(self) -> None:
        """Test fetching revision data when type is invalid."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3
        mock_s3.read_revision.return_value = MagicMock(schema=1, revision={})

        service = EntityStatementService(state=mock_state)

        with pytest.raises(ValueError):
            service._fetch_revision_data("Q42", 2)

    # _store_updated_revision
    @pytest.mark.asyncio
    async def test_store_updated_revision_success(self) -> None:
        """Test storing updated revision to S3."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_revision_data = MagicMock()
        mock_revision_data.revision_id = 3
        mock_revision_data.model_dump = MagicMock(return_value={})

        service = EntityStatementService(state=mock_state)

        new_rev_id = await service._store_updated_revision(
            mock_revision_data, "Q42", 2, EditHeaders(x_user_id=1, x_edit_summary="Test")
        )

        assert new_rev_id == 3
        mock_s3.store_revision.assert_called_once()
        mock_vitess.update_head_revision.assert_called_once_with("Q42", 3)

    @pytest.mark.asyncio
    async def test_store_updated_revision_s3_failure(self) -> None:
        """Test storing updated revision when S3 fails."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3
        mock_s3.store_revision.side_effect = Exception("S3 failure")

        mock_revision_data = MagicMock()
        mock_revision_data.revision_id = 3
        mock_revision_data.model_dump = MagicMock(return_value={})

        service = EntityStatementService(state=mock_state)

        with pytest.raises(ValueError):
            await service._store_updated_revision(
                mock_revision_data, "Q42", 2, EditHeaders(x_user_id=1, x_edit_summary="Test")
            )
