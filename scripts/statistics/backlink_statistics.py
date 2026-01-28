#!/usr/bin/env python3
"""Backlink statistics computation script.

This script computes daily backlink statistics for Wikibase entities by scanning
all statements and counting incoming references. Results are stored in the
entity_backlinks table for analytics and reporting.

Usage:
    python scripts/statistics/backlink_statistics.py

Environment Variables:
    VITESS_HOST, VITESS_PORT, VITESS_DATABASE, VITESS_USER, VITESS_PASSWORD:
    Database connection parameters.
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY: S3 connection parameters.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from models.infrastructure.s3.s3_client import MyS3Client  # type: ignore
from models.infrastructure.vitess.vitess_client import VitessClient  # type: ignore
from models.infrastructure.vitess.vitess_config import VitessConfig  # type: ignore
from models.infrastructure.s3.s3_config import S3Config  # type: ignore

logger = logging.getLogger(__name__)


def extract_entity_references(statement_content: dict) -> list[str]:
    """Extract entity IDs referenced in a statement.

    Parses the statement JSON to find entity references in mainsnak, qualifiers, and references.

    Args:
        statement_content: Parsed statement JSON from S3

    Returns:
        List of entity IDs (e.g., ['Q42', 'P31']) referenced in the statement
    """
    referenced = []

    # Check mainsnak
    if "mainsnak" in statement_content:
        mainsnak = statement_content["mainsnak"]
        if mainsnak.get("snaktype") == "value":
            datatype = mainsnak.get("datatype")
            if datatype in ["wikibase-item", "wikibase-property", "wikibase-lexeme"]:
                datavalue = mainsnak.get("datavalue", {})
                if datavalue.get("type") == "wikibase-entityid":
                    entity_id = datavalue.get("value", {}).get("id")
                    if entity_id:
                        referenced.append(entity_id)

    # Check qualifiers
    if "qualifiers" in statement_content:
        for qualifier in statement_content["qualifiers"].values():
            for snak in qualifier:
                if snak.get("snaktype") == "value":
                    datatype = snak.get("datatype")
                    if datatype in [
                        "wikibase-item",
                        "wikibase-property",
                        "wikibase-lexeme",
                    ]:
                        datavalue = snak.get("datavalue", {})
                        if datavalue.get("type") == "wikibase-entityid":
                            entity_id = datavalue.get("value", {}).get("id")
                            if entity_id:
                                referenced.append(entity_id)

    # Check references
    if "references" in statement_content:
        for ref in statement_content["references"]:
            if "snaks" in ref:
                for snak_list in ref["snaks"].values():
                    for snak in snak_list:
                        if snak.get("snaktype") == "value":
                            datatype = snak.get("datatype")
                            if datatype in [
                                "wikibase-item",
                                "wikibase-property",
                                "wikibase-lexeme",
                            ]:
                                datavalue = snak.get("datavalue", {})
                                if datavalue.get("type") == "wikibase-entityid":
                                    entity_id = datavalue.get("value", {}).get("id")
                                    if entity_id:
                                        referenced.append(entity_id)

    return referenced


async def compute_backlinks(vitess_client: Any, s3_client: Any) -> None:
    """Compute backlink statistics for all entities.

    Scans all statement hashes, retrieves statement content from S3,
    parses entity references, and aggregates backlink counts.
    Stores daily global statistics in the backlink_statistics table.

    Args:
        vitess_client: Initialized Vitess client
        s3_client: Initialized S3 client
    """
    logger.info("Starting backlink computation")

    # Get all statement hashes from statement_content table
    statement_hashes = vitess_client.statement_repository.get_all_statement_hashes(
        vitess_client.connection
    )

    logger.info(f"Found {len(statement_hashes)} statements to process")

    backlink_counts: dict[str, int] = {}

    # Process statements in batches
    batch_size = 100
    total_processed = 0

    for i in range(0, len(statement_hashes), batch_size):
        batch_hashes = statement_hashes[i : i + batch_size]
        batch_content = await s3_client.batch_get_statements(batch_hashes)

        for hash_val, content in batch_content.items():
            if content:
                # Parse statement and extract entity references
                referenced_entities = extract_entity_references(content)
                for entity_id in referenced_entities:
                    backlink_counts[entity_id] = backlink_counts.get(entity_id, 0) + 1

        total_processed += len(batch_content)
        if total_processed % 1000 == 0:
            logger.info(
                f"Processed {total_processed} statements, found {len(backlink_counts)} entities with backlinks"
            )

    logger.info(f"Computed backlinks for {len(backlink_counts)} entities")

    # Compute global statistics
    total_backlinks = sum(backlink_counts.values())
    unique_entities_with_backlinks = len(backlink_counts)

    # Top 10 entities by backlink count
    top_entities = sorted(backlink_counts.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]
    top_entities_by_backlinks = [
        {"entity_id": entity_id, "backlinks": count}
        for entity_id, count in top_entities
    ]

    # Store results in backlink_statistics table
    today = datetime.now(timezone.utc).date().isoformat()
    vitess_client.backlink_repository.insert_backlink_statistics(
        vitess_client.connection,
        today,
        total_backlinks,
        unique_entities_with_backlinks,
        top_entities_by_backlinks,
    )

    logger.info("Backlink computation completed")


async def main() -> None:
    """Main entry point for the backlink statistics script."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting backlink statistics computation")

    try:
        # Initialize Vitess client
        vitess_config = VitessConfig(
            host=os.getenv("VITESS_HOST", "vitess"),
            port=int(os.getenv("VITESS_PORT", "15309")),
            database=os.getenv("VITESS_DATABASE", "page"),
            user=os.getenv("VITESS_USER", "root"),
            password=os.getenv("VITESS_PASSWORD", ""),
        )
        vitess_client = VitessClient(config=vitess_config)

        # Initialize S3 client
        s3_config = S3Config(
            endpoint=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            region="us-east-1",
        )
        s3_client = MyS3Client(config=s3_config)

        # Run computation
        await compute_backlinks(vitess_client, s3_client)

        logger.info("Backlink statistics computation finished successfully")

    except Exception as e:
        logger.error(f"Backlink computation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
