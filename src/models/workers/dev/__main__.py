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

from models.workers.dev.create_buckets import CreateBuckets
from models.workers.dev.create_tables import CreateTables


def setup_logging() -> None:
    """Setup logging for CLI usage."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


async def run_setup(args: Any) -> bool:
    """Run the setup command."""
    buckets_worker = CreateBuckets(
        minio_endpoint=args.endpoint,
        minio_access_key=args.access_key,
        minio_secret_key=args.secret_key,
    )

    tables_worker = CreateTables()

    print("Running development environment setup...")
    buckets_results = await buckets_worker.run_setup()
    tables_results = await tables_worker.run_setup()

    # Combine results
    overall_status = "completed"
    if buckets_results["setup_status"] != "completed" or tables_results["setup_status"] != "completed":
        overall_status = "failed"

    print(f"Setup status: {overall_status}")

    print("\nBucket results:")
    for bucket, status in buckets_results["buckets_created"].items():
        print(f"  {bucket}: {status}")

    print("\nTable results:")
    for table, status in tables_results["tables_created"].items():
        print(f"  {table}: {status}")

    # Show health status for both
    buckets_healthy = buckets_results['health_check']['overall_status'] == 'healthy'
    tables_healthy = tables_results['health_check']['overall_status'] == 'healthy'

    if buckets_healthy and tables_healthy:
        print("\nHealth check: healthy")
    else:
        print("\nHealth check: unhealthy")
        if not buckets_healthy:
            print("Bucket issues:")
            for issue in buckets_results["health_check"]["issues"]:
                print(f"  - {issue}")
        if not tables_healthy:
            print("Table issues:")
            for issue in tables_results["health_check"]["issues"]:
                print(f"  - {issue}")

    return overall_status == "completed"


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

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup development environment")
    setup_parser.set_defaults(func=run_setup)

    # Health check command
    health_parser = subparsers.add_parser("health", help="Check bucket health")
    health_parser.set_defaults(func=run_health_check)

    # Cleanup command
    cleanup_parser = subparsers.add_parser(
        "cleanup", help="Clean up buckets (dangerous)"
    )
    cleanup_parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt"
    )
    cleanup_parser.set_defaults(func=run_cleanup)

    args = parser.parse_args()

    if not args.command:
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
