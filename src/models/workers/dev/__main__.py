#!/usr/bin/env python3
"""CLI interface for the development worker."""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# noinspection PyPep8
from models.workers.dev.create_buckets import CreateBuckets
# noinspection PyPep8
from models.workers.dev.create_tables import CreateTables


def setup_logging() -> None:
    """Setup logging for CLI usage."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


async def run_buckets_setup(args: Any) -> bool:
    """Run bucket setup."""
    worker = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )

    print("Running bucket setup...")
    results = await worker.run_setup()

    print(f"Setup status: {results['setup_status']}")

    print("\nBucket results:")
    for bucket, status in results["buckets_created"].items():
        print(f"  {bucket}: {status}")

    healthy = results['health_check']['overall_status'] == 'healthy'
    if healthy:
        print("\nHealth check: healthy")
    else:
        print("\nHealth check: unhealthy")
        print("Bucket issues:")
        for issue in results["health_check"]["issues"]:
            print(f"  - {issue}")

    return results["setup_status"] == "completed"


async def run_buckets_health(args: Any) -> bool:
    """Run bucket health check."""
    worker = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )

    print("Running bucket health check...")
    health = await worker.bucket_health_check()

    print(f"Overall status: {health['overall_status']}")
    print("\nBucket status:")
    for bucket, status in health["buckets"].items():
        print(f"  {bucket}: {status['status']}")

    if health["issues"]:
        print("\nIssues:")
        for issue in health["issues"]:
            print(f"  - {issue}")

    return health["overall_status"] == "healthy"


async def run_buckets_cleanup(args: Any) -> bool:
    """Run bucket cleanup."""
    if not args.force:
        print("WARNING: This will delete all buckets and their contents!")
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response != "yes":
            print("Cleanup cancelled.")
            return False

    worker = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )

    print("Running bucket cleanup...")
    results = await worker.cleanup_buckets()

    print("Cleanup results:")
    for bucket, status in results.items():
        print(f"  {bucket}: {status}")

    return True


async def run_tables_setup(args: Any) -> bool:
    """Run table setup."""
    worker = CreateTables()

    print("Running database table setup...")
    results = await worker.run_setup()

    print(f"Setup status: {results['setup_status']}")

    print("\nTable results:")
    for table, status in results["tables_created"].items():
        print(f"  {table}: {status}")

    healthy = results['health_check']['overall_status'] == 'healthy'
    if healthy:
        print("\nHealth check: healthy")
    else:
        print("\nHealth check: unhealthy")
        print("Table issues:")
        for issue in results["health_check"]["issues"]:
            print(f"  - {issue}")

    return results["setup_status"] == "completed"


async def run_tables_health(args: Any) -> bool:
    """Run table health check."""
    worker = CreateTables()

    print("Running table health check...")
    health = await worker.table_health_check()

    print(f"Overall status: {health['overall_status']}")
    print(f"Healthy tables: {health['healthy_tables']}/{health['total_tables']}")

    if health["issues"]:
        print("\nIssues:")
        for issue in health["issues"]:
            print(f"  - {issue}")

    return health["overall_status"] == "healthy"


async def run_health_check(args: Any) -> Any:
    """Run the health check command."""
    worker = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )

    print("Running bucket health check...")
    health = await worker.bucket_health_check()

    print(f"Overall status: {health['overall_status']}")
    print("\nBucket status:")
    for bucket, status in health["buckets"].items():
        print(f"  {bucket}: {status['status']}")

    if health["issues"]:
        print("\nIssues:")
        for issue in health["issues"]:
            print(f"  - {issue}")

    return health["overall_status"] == "healthy"


async def run_cleanup(args: Any) -> bool:
    """Run the cleanup command."""
    if not args.force:
        print("WARNING: This will delete all buckets and their contents!")
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response != "yes":
            print("Cleanup cancelled.")
            return False

    worker = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )

    print("Running bucket cleanup...")
    results = await worker.cleanup_buckets()

    print("Cleanup results:")
    for bucket, status in results.items():
        print(f"  {bucket}: {status}")

    return True


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
    buckets_subparsers = buckets_parser.add_subparsers(dest="operation", help="Bucket operations")

    # Bucket operations
    buckets_setup_parser = buckets_subparsers.add_parser("setup", help="Create and setup MinIO buckets")
    buckets_setup_parser.set_defaults(func=run_buckets_setup)

    buckets_health_parser = buckets_subparsers.add_parser("health", help="Check bucket health")
    buckets_health_parser.set_defaults(func=run_buckets_health)

    buckets_cleanup_parser = buckets_subparsers.add_parser("cleanup", help="Clean up buckets (dangerous)")
    buckets_cleanup_parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt"
    )
    buckets_cleanup_parser.set_defaults(func=run_buckets_cleanup)

    # Tables component
    tables_parser = subparsers.add_parser("tables", help="Manage database tables")
    tables_subparsers = tables_parser.add_subparsers(dest="operation", help="Table operations")

    # Table operations
    tables_setup_parser = tables_subparsers.add_parser("setup", help="Create and setup database tables")
    tables_setup_parser.set_defaults(func=run_tables_setup)

    tables_health_parser = tables_subparsers.add_parser("health", help="Check table health")
    tables_health_parser.set_defaults(func=run_tables_health)

    args = parser.parse_args()

    if not hasattr(args, 'component') or not args.component:
        parser.print_help()
        return 1

    if not hasattr(args, 'operation') or not args.operation:
        parser.print_help()
        return 1

    setup_logging()

    try:
        success = asyncio.run(args.func(args))
        return 0 if success else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
