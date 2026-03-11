"""Unit tests for EntityJsonImportHandler methods."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from models.rest_api.entitybase.v1.handlers.entity.wikidata_import import (
    EntityJsonImportHandler,
)


class TestEntityJsonImportHandler:
    """Unit tests for EntityJsonImportHandler helper methods."""

    def test_create_error_log_path_with_worker_id(self):
        """Test error log path creation with worker ID."""
        with patch("models.rest_api.entitybase.v1.handlers.entity.wikidata_import.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
            
            state = MagicMock()
            handler = EntityJsonImportHandler(state=state)
            
            result = handler._create_error_log_path("worker-001")
            
            assert isinstance(result, Path)
            assert "worker-001" in str(result)
            assert "20240101_120000" in str(result)

    def test_create_error_log_path_without_worker_id(self):
        """Test error log path creation without worker ID."""
        with patch("models.rest_api.entitybase.v1.handlers.entity.wikidata_import.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
            
            state = MagicMock()
            handler = EntityJsonImportHandler(state=state)
            
            result = handler._create_error_log_path(None)
            
            assert isinstance(result, Path)
            assert "wikidata_import_errors" in str(result)

    def test_should_process_line_before_start(self):
        """Test that lines before start_line are skipped."""
        state = MagicMock()
        handler = EntityJsonImportHandler(state=state)
        
        # start=5, end=10
        # line 3 should be skipped
        assert handler._should_process_line(3, 5, 10) is False

    def test_should_process_line_after_end(self):
        """Test that lines after end_line are skipped."""
        state = MagicMock()
        handler = EntityJsonImportHandler(state=state)
        
        # start=5, end=10
        # line 15 should be skipped
        assert handler._should_process_line(15, 5, 10) is False

    def test_should_process_line_within_range(self):
        """Test that lines within range are processed."""
        state = MagicMock()
        handler = EntityJsonImportHandler(state=state)
        
        # start=5, end=10
        # line 7 should be processed
        assert handler._should_process_line(7, 5, 10) is True

    def test_should_process_line_at_start(self):
        """Test that line at start_line is processed."""
        state = MagicMock()
        handler = EntityJsonImportHandler(state=state)
        
        assert handler._should_process_line(5, 5, 10) is True

    def test_should_process_line_at_end(self):
        """Test that line at end_line is processed."""
        state = MagicMock()
        handler = EntityJsonImportHandler(state=state)
        
        assert handler._should_process_line(10, 5, 10) is True

    def test_should_process_line_zero_end_means_unlimited(self):
        """Test that end_line=0 means process to end of file."""
        state = MagicMock()
        handler = EntityJsonImportHandler(state=state)
        
        # With end_line=0, line 1000 should still be processed
        assert handler._should_process_line(1000, 5, 0) is True

    def test_should_process_line_start_1(self):
        """Test with start_line=1."""
        state = MagicMock()
        handler = EntityJsonImportHandler(state=state)
        
        assert handler._should_process_line(1, 1, 10) is True
        assert handler._should_process_line(0, 1, 10) is False
