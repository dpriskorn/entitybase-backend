"""Unit tests for RevisionStorage."""

from unittest.mock import MagicMock, patch

import pytest

from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.s3.storage.revision_storage import RevisionStorage


class TestRevisionStorage:
    """Unit tests for RevisionStorage class."""

    def test_load_revision_not_found(self) -> None:
        """Test loading non-existent revision."""
        from models.infrastructure.s3.base_storage import BaseS3Storage
        
        storage = RevisionStorage()
        # Mock the connection manager to avoid S3 connection
        mock_connection_manager = MagicMock()
        mock_connection_manager.boto_client = MagicMock()
        storage.connection_manager = mock_connection_manager

        # Mock the load method at class level to avoid Pydantic delattr issues
        with patch.object(BaseS3Storage, 'load', side_effect=S3NotFoundError("Revision not found")):
            # The load_revision method should raise S3NotFoundError for missing data
            with pytest.raises(S3NotFoundError):
                storage.load_revision(12345)