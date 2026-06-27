"""Unit tests for SchemaRepository."""

from unittest.mock import MagicMock

import pytest

from models.infrastructure.mysql.repositories.schema import SchemaRepository


class TestSchemaRepository:
    """Unit tests for SchemaRepository."""

    def test_create_tables_no_mysql_client(self):
        """Test create_tables with no mysql client."""
        repo = SchemaRepository(mysql_client=None)

        from fastapi import HTTPException

        with pytest.raises(HTTPException, match="Sql not initialized"):
            repo.create_tables()

    def test_create_tables_no_connection(self):
        """Test create_tables with no database connection."""
        mock_mysql_client = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = None

        mock_mysql_client.connection_manager = mock_connection_manager

        repo = SchemaRepository(mysql_client=mock_mysql_client)

        with pytest.raises(Exception):
            repo.create_tables()

    def test_create_tables_database_error(self):
        """Test create_tables with database error."""
        mock_mysql_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_mysql_client.cursor = mock_cursor

        repo = SchemaRepository(mysql_client=mock_mysql_client)

        with pytest.raises(Exception):
            repo.create_tables()
