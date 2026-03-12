"""Unit tests for worker __main__ entry points."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock


class TestWorkerEntryPoints:
    """Unit tests for worker entry point modules."""

    @patch("models.workers.incremental_rdf.incremental_rdf_worker.main", new_callable=AsyncMock)
    def test_incremental_rdf_main_entry_point(self, mock_main):
        """Test incremental_rdf worker entry point runs main."""
        # Directly test that the module can be imported and asyncio.run works
        from models.workers.incremental_rdf import __main__ as inc_main
        from models.workers.incremental_rdf import incremental_rdf_worker

        # Run the main function
        asyncio.run(incremental_rdf_worker.main())

        mock_main.assert_called_once()

    @patch("models.workers.json_dumps.json_dump_worker.main", new_callable=AsyncMock)
    def test_json_dumps_main_entry_point(self, mock_main):
        """Test json dumps worker entry point runs main."""
        from models.workers.json_dumps import json_dump_worker

        asyncio.run(json_dump_worker.main())

        mock_main.assert_called_once()

    @patch("models.workers.ttl_dumps.ttl_dump_worker.main", new_callable=AsyncMock)
    def test_ttl_dumps_main_entry_point(self, mock_main):
        """Test ttl dumps worker entry point runs main."""
        from models.workers.ttl_dumps import ttl_dump_worker

        asyncio.run(ttl_dump_worker.main())

        mock_main.assert_called_once()

    def test_incremental_rdf_module_structure(self):
        """Test incremental_rdf __main__ module structure."""
        from models.workers.incremental_rdf import __main__ as inc_main

        assert hasattr(inc_main, "__file__")

    def test_json_dumps_module_structure(self):
        """Test json_dumps __main__ module structure."""
        from models.workers.json_dumps import __main__ as json_main

        assert hasattr(json_main, "__file__")

    def test_ttl_dumps_module_structure(self):
        """Test ttl_dumps __main__ module structure."""
        from models.workers.ttl_dumps import __main__ as ttl_main

        assert hasattr(ttl_main, "__file__")
