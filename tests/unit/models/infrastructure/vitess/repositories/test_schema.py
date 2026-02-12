"""Unit tests for SchemaRepository."""

from unittest.mock import MagicMock

import pytest

from models.infrastructure.vitess.repositories.schema import SchemaRepository


class TestSchemaRepository:
    """Unit tests for SchemaRepository."""

    def test_create_tables_no_vitess_client(self):
        """Test create_tables with no vitess client."""
        repo = SchemaRepository(vitess_client=None)

        from fastapi import HTTPException
        with pytest.raises(HTTPException, match="Vitess not initialized"):
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
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = SchemaRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):
            repo.create_tables()
