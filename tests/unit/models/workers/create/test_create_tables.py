"""Unit tests for create_tables."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.workers.create.create_tables import (
    CreateTables,
)


class TestCreateTables:
    """Unit tests for CreateTables."""

    def test_required_tables_list(self):
        """Test that required_tables contains expected tables."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

            assert "entity_id_mapping" in worker.required_tables
            assert "entity_revisions" in worker.required_tables
            assert "entity_head" in worker.required_tables
            assert "users" in worker.required_tables
            assert "id_ranges" in worker.required_tables
            assert len(worker.required_tables) > 10

    def test_required_tables_count(self):
        """Test count of required tables."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()
            # Should have 17 required tables based on the source
            assert len(worker.required_tables) >= 15

    def test_model_dump(self):
        """Test model_dump includes expected fields."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

            dumped = worker.model_dump()
            assert "required_tables" in dumped


class TestTableHealthCheckResult:
    """Unit tests for TableHealthCheckResult."""

    def test_table_health_check_result_creation(self):
        """Test TableHealthCheckResult creation."""
        from models.workers.create.create_tables import TableHealthCheckResult

        result: TableHealthCheckResult = {
            "overall_status": "healthy",
            "healthy_tables": 10,
            "total_tables": 17,
            "issues": [],
        }

        assert result["overall_status"] == "healthy"
        assert result["healthy_tables"] == 10


class TestTableSetupResult:
    """Unit tests for TableSetupResult."""

    def test_table_setup_result_creation(self):
        """Test TableSetupResult creation."""
        from models.workers.create.create_tables import (
            TableSetupResult,
            TableHealthCheckResult,
        )

        health_check: TableHealthCheckResult = {
            "overall_status": "healthy",
            "healthy_tables": 17,
            "total_tables": 17,
            "issues": [],
        }

        result: TableSetupResult = {
            "tables_created": {"entity_id_mapping": "created"},
            "health_check": health_check,
            "setup_status": "completed",
        }

        assert result["setup_status"] == "completed"
        assert result["tables_created"]["entity_id_mapping"] == "created"
