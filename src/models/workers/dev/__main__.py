#!/usr/bin/env python3
"""CLI interface for the development worker."""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# noinspection PyPep8
from models.config.settings import settings

# noinspection PyPep8
from models.workers.dev.create_buckets import CreateBuckets

# noinspection PyPep8
from models.workers.dev.create_tables import CreateTables


def setup_logging() -> None:
    """Setup logging for CLI usage."""
    logging.basicConfig(
        level=settings.get_log_level(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Development worker for MinIO bucket management"
    )
    parser.add_argument(
        "--endpoint",
        default=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        help="MinIO endpoint URL",
    )
    parser.add_argument(
        "--access-key",
        default=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        help="MinIO access key",
    )
    parser.add_argument(
        "--secret-key",
        default=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        help="MinIO secret key",
    )

    subparsers = parser.add_subparsers(dest="component", help="Component to manage")

    # Buckets component
    buckets_parser = subparsers.add_parser("buckets", help="Manage MinIO buckets")
    buckets_subparsers = buckets_parser.add_subparsers(
        dest="operation", help="Bucket operations"
    )

    # Bucket operations
    buckets_setup_parser = buckets_subparsers.add_parser(
        "setup", help="Create and setup MinIO buckets"
    )
    buckets_setup_parser.set_defaults(func=run_buckets_setup)

    buckets_health_parser = buckets_subparsers.add_parser(
        "health", help="Check bucket health"
    )
    buckets_health_parser.set_defaults(func=run_buckets_health)

    # Tables component
    tables_parser = subparsers.add_parser("tables", help="Manage database tables")
    tables_subparsers = tables_parser.add_subparsers(
        dest="operation", help="Table operations"
    )

    # Table operations
    tables_setup_parser = tables_subparsers.add_parser(
        "setup", help="Create and setup database tables"
    )
    tables_setup_parser.set_defaults(func=run_tables_setup)

    tables_health_parser = tables_subparsers.add_parser(
        "health", help="Check table health"
    )
    tables_health_parser.set_defaults(func=run_tables_health)

    args = parser.parse_args()

    if not hasattr(args, "component") or not args.component:
        parser.print_help()
        return 1

    if not hasattr(args, "operation") or not args.operation:
        parser.print_help()
        return 1

    setup_logging()

    try:
        success = asyncio.run(args.func(args))
        return 0 if success else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


async def run_buckets_setup(args: argparse.Namespace) -> bool:
    """Run bucket setup operation."""
    create_buckets = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )
    results = await create_buckets.run_setup()
    print(f"Buckets setup completed: {results['setup_status']}")
    return results["setup_status"] == "completed"


async def run_buckets_health(args: argparse.Namespace) -> bool:
    """Run bucket health check operation."""
    create_buckets = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )
    health_status = await create_buckets.bucket_health_check()
    print(f"Bucket health status: {health_status['overall_status']}")
    return health_status["overall_status"] == "healthy"


async def run_tables_setup(args: argparse.Namespace) -> bool:
    """Run table setup operation."""
    create_tables = CreateTables()
    results = await create_tables.run_setup()
    print(f"Tables setup completed: {results['setup_status']}")
    return results["setup_status"] == "completed"


async def run_tables_health(args: argparse.Namespace) -> bool:
    """Run table health check operation."""
    create_tables = CreateTables()
    health_status = await create_tables.table_health_check()
    print(f"Table health status: {health_status['overall_status']}")
    print(
        f"Healthy tables: {health_status['healthy_tables']}/{health_status['total_tables']}"
    )
    return health_status["overall_status"] == "healthy"


if __name__ == "__main__":
    sys.exit(main())
