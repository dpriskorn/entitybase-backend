"""Unit tests for ReferenceStorage."""

import pytest
from unittest.mock import MagicMock, patch

from models.data.infrastructure.s3.reference_data import S3ReferenceData
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.storage.reference_storage import ReferenceStorage


class TestReferenceStorage:
    """Unit tests for ReferenceStorage class."""















    def test_load_references_batch_empty_list(self) -> None:
        """Test batch loading with empty hash list."""
        mock_connection_manager = MagicMock()
        storage = ReferenceStorage(connection_manager=mock_connection_manager)
        result = storage.load_references_batch([])

        assert result == []