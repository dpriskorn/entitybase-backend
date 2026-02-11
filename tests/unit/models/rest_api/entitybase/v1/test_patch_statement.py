"""Unit tests for patch_statement endpoint."""

import unittest
from unittest.mock import MagicMock

import pytest

from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler


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


if __name__ == "__main__":
    unittest.main()
