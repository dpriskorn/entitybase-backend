"""Unit tests for meilisearch_indexer __main__."""


class TestMeilisearchIndexerMain:
    """Tests for meilisearch_indexer __main__ entry point."""

    def test_main_module_imports(self):
        """Test that __main__ imports correctly."""
        from models.workers.meilisearch_indexer import __main__ as main_module

        assert main_module is not None

    def test_main_function_imported(self):
        """Test that main function is imported from worker."""
        from models.workers.meilisearch_indexer.__main__ import main

        assert callable(main)
