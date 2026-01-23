"""Unit tests for patch_statement endpoint."""

import unittest
from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler
from models.data.rest_api.v1.request import (
    PatchStatementRequest,
)


@pytest.mark.asyncio
class TestPatchStatement:
    """Unit tests for patch_statement functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_state = MagicMock()
        self.mock_vitess = MagicMock()
        self.mock_s3 = MagicMock()
        self.mock_validator = MagicMock()
        self.mock_state.vitess_client = self.mock_vitess
        self.mock_state.s3_client = self.mock_s3
        self.handler = EntityHandler(state=self.mock_state)

    async def test_statement_hash_not_found(self) -> None:
        """Test statement hash not found."""
        request = PatchStatementRequest(
            claim={"mainsnak": {"property": "P1"}}, edit_summary="Patch"
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.handler.EntityReadHandler"
        ) as mock_read_handler_class:
            mock_read_handler = MagicMock()
            mock_read_handler_class.return_value = mock_read_handler
            mock_entity_response = MagicMock()
            mock_entity_response.entity_data = {
                "claims": {"P1": [{"mainsnak": {"property": "P1"}}]}
            }
            mock_read_handler.get_entity.return_value = mock_entity_response

            result = await self.handler.patch_statement(
                "Q1", "999", request, self.mock_validator
            )
            assert not result.success
            assert "Statement not found" in result.error


if __name__ == "__main__":
    unittest.main()
