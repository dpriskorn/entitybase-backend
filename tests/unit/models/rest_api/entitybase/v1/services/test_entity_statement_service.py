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

    # remove_statement tests

    @pytest.mark.asyncio
    async def test_remove_statement_decrements_ref_count(self) -> None:
        """Test that remove_statement decrements reference count."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess.cursor = mock_cursor

        service = EntityStatementService(state=mock_state)
        service._decrement_statement_ref_count("12345")

        mock_cursor.execute.assert_called()

    # patch_statement tests

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

    def test_recalculate_property_counts_removes_property(self) -> None:
        """Test recalculating removes property when count is 0."""
        mock_revision = MagicMock()
        mock_revision.properties = ["P31", "P279"]
        mock_revision.property_counts = {"P31": 1, "P279": 3}

        result = _PropertyCountHelper.recalculate_property_counts(mock_revision, 0)

        assert "P31" not in result.properties
        assert "P31" not in result.property_counts.root

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
