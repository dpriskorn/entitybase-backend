import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from rapidhash import rapidhash

from models.entity import StatementHashResult
from models.infrastructure.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient

logger = logging.getLogger(__name__)


def hash_entity_statements(
    entity_data: dict[str, Any],
) -> StatementHashResult:
    """Extract and hash statements from entity data.

    Returns:
        StatementHashResult with hashes, properties, and full statements
    """
    statements = []
    full_statements = []
    properties_set = set()
    property_counts = {}

    claims = entity_data.get("claims", {})
    logger.debug(f"Entity claims: {claims}")

    if not claims:
        logger.debug("No claims found in entity data")
        return StatementHashResult()

    claims_count = sum(len(claim_list) for claim_list in claims.values())
    logger.debug(
        f"Hashing statements for entity with {len(claims)} properties, {claims_count} total statements"
    )

    for property_id, claim_list in claims.items():
        logger.debug(
            f"Processing property {property_id} with {len(claim_list)} statements"
        )

        if not claim_list:
            logger.debug(f"Empty claim list for property {property_id}")
            continue

        properties_set.add(property_id)
        count = 0

        for idx, statement in enumerate(claim_list):
            logger.debug(
                f"Processing statement {idx + 1}/{len(claim_list)} for property {property_id}"
            )
            try:
                statement_for_hash = {k: v for k, v in statement.items() if k != "id"}
                statement_json = json.dumps(statement_for_hash, sort_keys=True)
                statement_hash = rapidhash(statement_json.encode())
                logger.debug(
                    f"Generated hash {statement_hash} for statement {idx + 1} in property {property_id}"
                )

                statements.append(statement_hash)
                full_statements.append(statement)
                count += 1
            except Exception as e:
                logger.error(
                    f"Failed to hash statement {idx + 1} for property {property_id}: {e}"
                )
                logger.error(f"Statement data: {statement}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to hash statement: {e}",
                )

        property_counts[property_id] = count
        logger.debug(f"Property {property_id}: processed {count} statements")

    logger.debug(
        f"Generated {len(statements)} hashes, properties: {sorted(properties_set)}"
    )
    logger.debug(f"Property counts: {property_counts}")

    return StatementHashResult(
        statements=statements,
        properties=sorted(properties_set),
        property_counts=property_counts,
        full_statements=full_statements,
    )


def deduplicate_and_store_statements(
    hash_result: StatementHashResult,
    vitess_client: VitessClient,
    s3_client: S3Client,
) -> None:
    """Deduplicate and store statements in Vitess and S3.

    For each statement:
    - Check if hash exists in statement_content table
    - If not exists: write to S3 and insert into statement_content
    - If exists: increment ref_count

    Args:
        hash_result: StatementHashResult with hashes and full statements
        vitess_client: Vitess client for statement_content operations
        s3_client: S3 client for statement storage
    """
    logger.debug(f"Deduplicating and storing {len(hash_result.statements)} statements")

    for idx, (statement_hash, statement_data) in enumerate(
        zip(hash_result.statements, hash_result.full_statements)
    ):
        logger.debug(
            f"Processing statement {idx + 1}/{len(hash_result.statements)} with hash {statement_hash}"
        )
        try:
            is_new = vitess_client.insert_statement_content(statement_hash)
            logger.debug(f"Statement {statement_hash} is_new: {is_new}")

            if is_new:
                statement_with_hash = {
                    **statement_data,
                    "content_hash": statement_hash,
                    "created_at": datetime.now(timezone.utc).isoformat() + "Z",
                }
                s3_key = f"statements/{statement_hash}.json"

                # High Priority: Enhanced Statement Data Logging
                logger.debug(
                    f"Writing new statement {statement_hash} to S3 at key: {s3_key}"
                )
                logger.debug(
                    f"Full statement data: {json.dumps(statement_data, indent=2)}"
                )
                logger.debug(
                    f"Enhanced statement data with hash: {json.dumps(statement_with_hash, indent=2)}"
                )
                logger.debug(
                    f"Statement data size: {len(json.dumps(statement_with_hash))} bytes"
                )
                logger.debug(f"S3 client type: {type(s3_client)}")
                logger.debug(f"S3 client endpoint: {s3_client.client._endpoint.host}")

                import time
                import traceback

                try:
                    write_start_time = time.time()
                    s3_client.write_statement(statement_hash, statement_with_hash)
                    write_duration = time.time() - write_start_time

                    logger.info(
                        f"Successfully wrote statement {statement_hash} to S3 at key: {s3_key}",
                        extra={
                            "statement_hash": statement_hash,
                            "s3_key": s3_key,
                            "write_duration_seconds": write_duration,
                            "statement_data_size": len(json.dumps(statement_with_hash)),
                        },
                    )

                    # High Priority: Immediate verification by reading back
                    try:
                        s3_client.read_statement(statement_hash)
                        logger.debug(
                            f"Statement {statement_hash} verification successful: can read back from S3"
                        )
                    except Exception as verify_error:
                        logger.error(
                            f"Statement {statement_hash} verification failed: {verify_error}"
                        )
                        raise

                except Exception as write_error:
                    logger.error(
                        f"Failed to write statement {statement_hash} to S3",
                        extra={
                            "statement_hash": statement_hash,
                            "s3_key": s3_key,
                            "error_type": type(write_error).__name__,
                            "error_message": str(write_error),
                            "statement_data": statement_data,
                            "s3_bucket": s3_client.config.bucket,
                            "s3_endpoint": s3_client.client._endpoint.host,
                            "stack_trace": traceback.format_exc()
                            if hasattr(write_error, "__traceback__")
                            else None,
                        },
                    )
                    raise
            else:
                logger.debug(
                    f"Incrementing ref_count for existing statement {statement_hash}"
                )
                vitess_client.increment_ref_count(statement_hash)
                logger.debug(
                    f"Successfully incremented ref_count for statement {statement_hash}"
                )
        except Exception as e:
            logger.error(
                f"Statement storage failed for hash {statement_hash}",
                extra={
                    "statement_hash": statement_hash,
                    "statement_index": idx + 1,
                    "total_statements": len(hash_result.statements),
                    "statement_data": statement_data,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "stack_trace": str(e.__traceback__) if e.__traceback__ else None,
                },
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store statement {statement_hash}: {e}",
            )

    logger.info(
        f"Successfully stored all {len(hash_result.statements)} statements (new + existing)"
    )
    logger.info(f"Final statement hashes: {hash_result.statements}")
