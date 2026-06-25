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

    def test_vitess_config_property(self):
        """Test vitess_config property returns settings config."""
        with (
            patch("models.workers.create.create_tables.CreateTables.model_post_init"),
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            worker = CreateTables()

            config = worker.vitess_config

            assert config.host == "localhost"

    @pytest.mark.asyncio
    async def test_ensure_database_exists_success(self):
        """Test ensure_database_exists creates database successfully."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect",
                return_value=mock_conn,
            ),
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"

            worker.ensure_database_exists()

            mock_cursor.execute.assert_called_once_with(
                "CREATE DATABASE IF NOT EXISTS entitybase"
            )
            mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_database_exists_failure(self):
        """Test ensure_database_exists raises on connection error."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect",
                side_effect=Exception("DB down"),
            ),
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"

            with pytest.raises(Exception, match="DB down"):
                worker.ensure_database_exists()

    @pytest.mark.asyncio
    async def test_ensure_tables_exist_success(self):
        """Test ensure_tables_exist creates tables successfully."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect"
            ) as mock_connect,
            patch("models.workers.create.create_tables.settings") as mock_settings,
            patch("models.infrastructure.vitess.client.VitessClient"),
            patch("models.infrastructure.vitess.repositories.schema.SchemaRepository"),
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"
            mock_settings.get_vitess_config.database = "entitybase"

            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

            results = await worker.ensure_tables_exist()

            for table in worker.required_tables:
                assert results[table] == "created"

    @pytest.mark.asyncio
    async def test_ensure_tables_exist_schema_error(self):
        """Test ensure_tables_exist raises ConnectionError on SchemaRepository failure."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect"
            ) as mock_connect,
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"
            mock_settings.get_vitess_config.database = "entitybase"

            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

            with (
                patch(
                    "models.infrastructure.vitess.repositories.schema.SchemaRepository",
                    side_effect=Exception("Schema error"),
                ),
                patch("models.infrastructure.vitess.client.VitessClient"),
                pytest.raises(ConnectionError),
            ):
                await worker.ensure_tables_exist()

    @pytest.mark.asyncio
    async def test_table_health_check_all_healthy(self):
        """Test table_health_check returns healthy when all tables exist."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [("entity_id_mapping",)] * len(
            worker.required_tables
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect",
                return_value=mock_conn,
            ),
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"
            mock_settings.get_vitess_config.database = "entitybase"

            result = await worker.table_health_check()

            assert result["overall_status"] == "healthy"
            assert result["healthy_tables"] == len(worker.required_tables)
            assert result["issues"] == []

    @pytest.mark.asyncio
    async def test_table_health_check_missing_table(self):
        """Test table_health_check detects missing tables."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            None,
            ("entity_revisions",),
            ("entity_head",),
            ("entity_redirects",),
            ("statement_content",),
            ("entity_backlinks",),
            ("backlink_statistics",),
            ("metadata_content",),
            ("user_daily_stats",),
            ("general_daily_stats",),
            ("users",),
            ("watchlist",),
            ("user_notifications",),
            ("user_activity",),
            ("user_thanks",),
            ("user_statement_endorsements",),
            ("entity_terms",),
            ("id_ranges",),
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect",
                return_value=mock_conn,
            ),
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"
            mock_settings.get_vitess_config.database = "entitybase"

            result = await worker.table_health_check()

            assert result["overall_status"] == "unhealthy"
            assert result["healthy_tables"] == len(worker.required_tables) - 1
            assert "Table 'entity_id_mapping' does not exist" in result["issues"]

    @pytest.mark.asyncio
    async def test_table_health_check_table_check_error(self):
        """Test table_health_check handles per-table check errors."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Check error")
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect",
                return_value=mock_conn,
            ),
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"
            mock_settings.get_vitess_config.database = "entitybase"

            result = await worker.table_health_check()

            assert result["overall_status"] == "unhealthy"
            assert result["healthy_tables"] == 0
            assert len(result["issues"]) == len(worker.required_tables)

    @pytest.mark.asyncio
    async def test_table_health_check_connection_error(self):
        """Test table_health_check handles database connection failure."""
        with patch("models.workers.create.create_tables.CreateTables.model_post_init"):
            worker = CreateTables()

        with (
            patch(
                "models.workers.create.create_tables.pymysql.connect",
                side_effect=Exception("Connection refused"),
            ),
            patch("models.workers.create.create_tables.settings") as mock_settings,
        ):
            mock_settings.get_vitess_config.host = "localhost"
            mock_settings.get_vitess_config.port = 3306
            mock_settings.get_vitess_config.user = "root"
            mock_settings.get_vitess_config.password = "pass"
            mock_settings.get_vitess_config.database = "entitybase"

            result = await worker.table_health_check()

            assert result["overall_status"] == "unhealthy"
            assert result["healthy_tables"] == 0
            assert "Database connection failed" in result["issues"][0]

    @pytest.mark.asyncio
    async def test_run_setup_completed(self):
        """Test run_setup returns completed status when health check passes."""
        with (
            patch("models.workers.create.create_tables.CreateTables.model_post_init"),
            patch.object(
                CreateTables,
                "ensure_tables_exist",
                return_value={"entity_id_mapping": "created"},
            ),
            patch.object(
                CreateTables,
                "table_health_check",
                return_value={
                    "overall_status": "healthy",
                    "healthy_tables": 17,
                    "total_tables": 17,
                    "issues": [],
                },
            ),
        ):
            worker = CreateTables()

            result = await worker.run_setup()

            assert result["setup_status"] == "completed"
            assert result["tables_created"] == {"entity_id_mapping": "created"}
            assert result["health_check"]["overall_status"] == "healthy"

    @pytest.mark.asyncio
    async def test_run_setup_failed(self):
        """Test run_setup returns failed status when health check fails."""
        with (
            patch("models.workers.create.create_tables.CreateTables.model_post_init"),
            patch.object(
                CreateTables,
                "ensure_tables_exist",
                return_value={"entity_id_mapping": "created"},
            ),
            patch.object(
                CreateTables,
                "table_health_check",
                return_value={
                    "overall_status": "unhealthy",
                    "healthy_tables": 0,
                    "total_tables": 17,
                    "issues": ["Table 'entity_id_mapping' does not exist"],
                },
            ),
        ):
            worker = CreateTables()

            result = await worker.run_setup()

            assert result["setup_status"] == "failed"
            assert result["health_check"]["overall_status"] == "unhealthy"


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
