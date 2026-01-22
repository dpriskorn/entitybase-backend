"""Unit tests for SchemaRepository."""

from unittest.mock import MagicMock

import pytest

from models.infrastructure.vitess.repositories.schema import SchemaRepository


class TestSchemaRepository:
    """Unit tests for SchemaRepository."""

    def test_create_tables_success(self):
        """Test successful table creation."""
        mock_vitess_client = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_vitess_client.connection_manager.connection = mock_connection
        mock_vitess_client.cursor = mock_cursor

        repo = SchemaRepository(vitess_client=mock_vitess_client)

        repo.create_tables()

        # Should execute 16 CREATE TABLE statements (count the cursor.execute calls)
        assert mock_cursor.execute.call_count == 16

    def test_create_tables_no_vitess_client(self):
        """Test create_tables with no vitess client."""
        repo = SchemaRepository(vitess_client=None)

        with pytest.raises(Exception):  # raise_validation_error raises ValueError
            repo.create_tables()

    def test_create_tables_no_connection(self):
        """Test create_tables with no database connection."""
        mock_vitess_client = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = None

        mock_vitess_client.connection_manager = mock_connection_manager

        repo = SchemaRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):
            repo.create_tables()

    def test_create_tables_database_error(self):
        """Test create_tables with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = SchemaRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):
            repo.create_tables()
