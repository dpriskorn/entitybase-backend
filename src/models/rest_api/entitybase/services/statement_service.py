"""Statement processing service."""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from models.common import OperationResult
from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.vitess_client import VitessClient
from models.internal_representation.statement_extractor import StatementExtractor
from models.internal_representation.statement_hasher import StatementHasher
from models.rest_api.entitybase.response import StatementHashResult
from models.infrastructure.s3.s3_client import StoredStatement
from models.validation.json_schema_validator import JsonSchemaValidator

logger = logging.getLogger(__name__)


def hash_entity_statements(
    entity_data: dict[str, Any],
) -> OperationResult:
    """Extract and hash statements from entity data.

    Returns:
        OperationResult with StatementHashResult in data
    """
    try:
        statements = []
        full_statements = []

        claims = entity_data.get("claims", {})
        logger.debug(f"Entity claims: {claims}")

        if not claims:
            logger.debug("No claims found in entity data")
            return OperationResult(success=True, data=StatementHashResult())

        properties = StatementExtractor.extract_properties_from_claims(claims)
        property_counts = StatementExtractor.compute_property_counts_from_claims(claims)

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

            count = len(claim_list)

            for idx, statement in enumerate(claim_list):
                logger.debug(
                    f"Processing statement {idx + 1}/{len(claim_list)} for property {property_id}"
                )
                statement_hash = StatementHasher.compute_hash(statement)
                logger.debug(
                    f"Generated hash {statement_hash} for statement {idx + 1} in property {property_id}"
                )

                statements.append(statement_hash)
                full_statements.append(statement)

            logger.debug(f"Property {property_id}: processed {count} statements")

        logger.debug(f"Generated {len(statements)} hashes, properties: {properties}")
        logger.debug(f"Property counts: {property_counts}")

        result = StatementHashResult(
            statements=statements,
            properties=properties,
            property_counts=property_counts,
            full_statements=full_statements,
        )
        return OperationResult(success=True, data=result)
    except Exception as e:
        logger.error(f"Failed to hash entity statements: {e}", exc_info=True)
        return OperationResult(success=False, error=str(e))


def deduplicate_and_store_statements(
    hash_result: StatementHashResult,
    vitess_client: VitessClient,
    s3_client: MyS3Client,
    validator: JsonSchemaValidator | None = None,
    schema_version: str = "latest",
) -> OperationResult:
    """Deduplicate and store statements in Vitess and S3 (S3-first approach).

    For each statement:
    1. Validate statement against schema (if validator provided)
    2. Check if S3 object exists
    3. If not exists: write to S3 (with verification)
    4. Insert into statement_content (idempotent) or increment ref_count

    S3-first approach prevents DB/S3 sync issues from failed writes.

    Args:
        hash_result: StatementHashResult with hashes and full statements
        vitess_client: Vitess client for statement_content operations
        s3_client: S3 client for statement storage
        validator: Optional JSON schema validator for statement validation
        schema_version: Version
    """
    logger.debug(
        f"Deduplicating and storing {len(hash_result.statements)} statements (S3-first)"
    )

    for idx, (statement_hash, statement_data) in enumerate(
        zip(hash_result.statements, hash_result.full_statements)
    ):
        logger.debug(
            f"Processing statement {idx + 1}/{len(hash_result.statements)} with hash {statement_hash}"
        )
        try:
            statement_with_hash = StoredStatement(
                schema=schema_version,
                hash=statement_hash,
                statement=statement_data,
                created_at=datetime.now(timezone.utc).isoformat() + "Z",
            )
            s3_key = f"statements/{statement_hash}.json"

            import time
            import traceback

            # Step 1: Check if S3 object exists
            # noinspection PyUnusedLocal
            s3_exists = False
            try:
                s3_client.read_statement(statement_hash)
                s3_exists = True
                logger.debug(f"Statement {statement_hash} already exists in S3")
            except Exception:
                logger.debug(
                    f"Statement {statement_hash} not found in S3, will write new object"
                )
                s3_exists = False

            # Step 2: Validate statement before storing
            if validator is not None:
                validator.validate_statement(statement_with_hash.model_dump())

            # Step 3: Write to S3 if not exists
            if not s3_exists:
                try:
                    write_start_time = time.time()
                    s3_client.write_statement(
                        statement_hash,
                        statement_with_hash.model_dump(),
                        schema_version=schema_version,
                    )
                    write_duration = time.time() - write_start_time

                    logger.info(
                        f"Successfully wrote statement {statement_hash} to S3 at key: {s3_key}",
                        extra={
                            "statement_hash": statement_hash,
                            "s3_key": s3_key,
                            "write_duration_seconds": write_duration,
                            "statement_data_size": len(
                                json.dumps(statement_with_hash.model_dump())
                            ),
                        },
                    )
                except Exception as write_error:
                    # noinspection PyProtectedMember
                    logger.error(
                        f"Failed to write statement {statement_hash} to S3",
                        extra={
                            "statement_hash": statement_hash,
                            "s3_key": s3_key,
                            "error_type": type(write_error).__name__,
                            "error_message": str(write_error),
                            "statement_data": statement_data,
                            "s3_bucket": s3_client.config.bucket,
                            "s3_endpoint": s3_client.conn.meta.endpoint_url,
                            "stack_trace": traceback.format_exc()
                            if hasattr(write_error, "__traceback__")
                            else None,
                        },
                    )
                    raise

            # Step 4: Insert into DB or increment ref_count
            # Note: We skip the DB existence check and insert directly to be more efficient
            # The insert is idempotent, so it handles concurrent inserts gracefully
            inserted = vitess_client.insert_statement_content(statement_hash)
            if inserted:
                logger.debug(
                    f"Inserted new statement {statement_hash} into statement_content"
                )
            else:
                logger.debug(
                    f"Statement {statement_hash} already in DB, incrementing ref_count"
                )
                vitess_client.increment_ref_count(statement_hash)

            # Step 5: Next statement

        except Exception as e:
            logger.error(
                f"Statement storage failed for hash {statement_hash}: {type(e).__name__}: {e}",
                extra={
                    "statement_hash": statement_hash,
                    "statement_index": idx + 1,
                    "total_statements": len(hash_result.statements),
                    "statement_data": statement_data,
                },
                exc_info=True,
            )
            return OperationResult(
                success=False, error=f"Failed to store statement {statement_hash}: {e}"
            )

    logger.info(
        f"Successfully stored all {len(hash_result.statements)} statements (new + existing)"
    )
    logger.info(f"Final statement hashes: {hash_result.statements}")
    return OperationResult(success=True)
