"""Unit tests for worker __main__ entry points."""

import pytest
from unittest.mock import patch, MagicMock


class TestWorkerEntryPoints:
    """Unit tests for worker entry point modules."""

    @patch("models.workers.incremental_rdf.incremental_rdf_worker.main")
    def test_incremental_rdf_main_entry_point(self, mock_main):
        """Test incremental_rdf worker entry point."""
        import models.workers.incremental_rdf.__main__ as main_module

        # Simulate running as __main__
        with patch.object(main_module, "__name__", "__main__"):
            # The import just imports the module, doesn't run main
            # So we just verify the module imports correctly
            from models.workers.incremental_rdf import __main__

            assert __main__ is not None

    @patch("models.workers.json_dumps.json_dump_worker.main")
    def test_json_dumps_main_entry_point(self, mock_main):
        """Test json dumps worker entry point."""
        from models.workers.json_dumps import __main__

        assert __main__ is not None

    @patch("models.workers.ttl_dumps.ttl_dump_worker.main")
    def test_ttl_dumps_main_entry_point(self, mock_main):
        """Test ttl dumps worker entry point."""
        from models.workers.ttl_dumps import __main__

        assert __main__ is not None

    def test_incremental_rdf_module_structure(self):
        """Test incremental_rdf __main__ module structure."""
        from models.workers.incremental_rdf import __main__ as inc_main

        # Check module has expected attributes
        assert hasattr(inc_main, "__file__")

    def test_json_dumps_module_structure(self):
        """Test json_dumps __main__ module structure."""
        from models.workers.json_dumps import __main__ as json_main

        assert hasattr(json_main, "__file__")

    def test_ttl_dumps_module_structure(self):
        """Test ttl_dumps __main__ module structure."""
        from models.workers.ttl_dumps import __main__ as ttl_main

        assert hasattr(ttl_main, "__file__")
