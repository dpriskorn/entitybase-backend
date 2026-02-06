#!/usr/bin/env python3
"""Development worker for database table creation and management."""

import logging
import os
import sys
from typing import Any, Dict, List, TypedDict

import pymysql
from pydantic import BaseModel


class TableHealthCheckResult(TypedDict):
    """Result of table health check."""
    overall_status: str
    healthy_tables: int
    total_tables: int
    issues: List[str]


class TableSetupResult(TypedDict):
    """Result of table setup operation."""
    tables_created: Dict[str, str]
    health_check: TableHealthCheckResult
    setup_status: str

logger = logging.getLogger(__name__)

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, src_path)

# noinspection PyPep8
from models.config.settings import settings


class CreateTables(BaseModel):
    """Development worker for database table creation and management."""

    # Essential tables required for the application
    required_tables: List[str] = [
        "entity_id_mapping",
        "entity_revisions",
        "entity_head",
        "entity_redirects",
        "statement_content",
        "entity_backlinks",
        "backlink_statistics",
        "metadata_content",
        "user_daily_stats",
        "general_daily_stats",
        "users",
        "watchlist",
        "user_notifications",
        "user_activity",
        "user_thanks",
        "user_statement_endorsements",
        "entity_terms",
        "id_ranges",
    ]



    @property
    def vitess_config(self) -> Any:
        """Get Vitess configuration."""
        config = settings.get_vitess_config
        logger.debug(f"VitessConfig loaded: host='{config.host}', port={config.port}, database='{config.database}', user='{config.user}', password_length={len(config.password)}")
        return config

    async def ensure_tables_exist(self) -> Dict[str, str]:
        """Ensure all required tables exist using SchemaRepository."""
        results = {}

        try:
            from models.infrastructure.vitess.repositories.schema import SchemaRepository
            from models.infrastructure.vitess.client import VitessClient

            logger.info("Creating database tables using SchemaRepository...")
            logger.debug(f"Creating VitessClient with config: host='{self.vitess_config.host}', port={self.vitess_config.port}, database='{self.vitess_config.database}'")
            vitess_client = VitessClient(config=self.vitess_config)
            schema_repository = SchemaRepository(vitess_client=vitess_client)
            schema_repository.create_tables()

            # Assume all tables were created successfully
            for table in self.required_tables:
                results[table] = "created"

            logger.info("Database tables created successfully")
            return results

        except Exception as e:
            logger.warning(f"SchemaRepository approach failed: {e}")
            raise ConnectionError()

    async def table_health_check(self) -> TableHealthCheckResult:
        """Check if all required tables exist and are accessible."""
        issues: List[str] = []
        healthy_tables = 0

        try:
            conn = pymysql.connect(
                host=self.vitess_config.host,
                port=self.vitess_config.port,
                user=self.vitess_config.user,
                password=self.vitess_config.password,
                database=self.vitess_config.database,
            )

            with conn.cursor() as cursor:
                # Check each required table
                for table in self.required_tables:
                    try:
                        cursor.execute(f"SHOW TABLES LIKE '{table}'")
                        if not cursor.fetchone():
                            issues.append(f"Table '{table}' does not exist")
                        else:
                            healthy_tables += 1
                    except Exception as e:
                        issues.append(f"Error checking table '{table}': {e}")

            conn.close()

        except Exception as e:
            issues.append(f"Database connection failed: {e}")

        overall_status = "healthy" if len(issues) == 0 else "unhealthy"

        return TableHealthCheckResult(
            overall_status=overall_status,
            healthy_tables=healthy_tables,
            total_tables=len(self.required_tables),
            issues=issues,
        )

    async def run_setup(self) -> TableSetupResult:
        """Run complete table setup process for development environment."""
        logger.info("Starting database table setup")

        # Ensure tables exist
        table_results = await self.ensure_tables_exist()

        # Perform health check
        health_status = await self.table_health_check()

        setup_results: TableSetupResult = {
            "tables_created": table_results,
            "health_check": health_status,
            "setup_status": "completed"
            if health_status["overall_status"] == "healthy"
            else "failed",
        }

        logger.info(
            f"Database table setup completed with status: {setup_results['setup_status']}"
        )
        return setup_results
