"""Unit tests for SchemaRepository."""

from unittest.mock import MagicMock

import pytest

from models.infrastructure.db.repositories.schema import SchemaRepository


class TestSchemaRepository:
    """Unit tests for SchemaRepository."""

    def test_create_tables_no_db_client(self):
        """Test create_tables with no vitess client."""
        repo = SchemaRepository(db_client=None)

        from fastapi import HTTPException

        with pytest.raises(HTTPException, match="Database not initialized"):
            repo.create_tables()

    def test_create_tables_no_connection(self):
        """Test create_tables with no database connection."""
        mock_db_client = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection_manager.conn = None

        mock_db_client.connection_manager = mock_connection_manager

        repo = SchemaRepository(db_client=mock_db_client)

        with pytest.raises(Exception):
            repo.create_tables()

    def test_create_tables_database_error(self):
        """Test create_tables with database error."""
        mock_db_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_db_client.cursor = mock_cursor

        repo = SchemaRepository(db_client=mock_db_client)

        with pytest.raises(Exception):
            repo.create_tables()
