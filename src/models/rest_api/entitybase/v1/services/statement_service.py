"""Statement processing service."""

import logging
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, cast

from models.data.common import OperationResult
from models.config.settings import settings
from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.data.infrastructure.s3.reference_data import S3ReferenceData
from models.data.infrastructure.s3.statement import S3Statement
from models.data.rest_api.v1.entitybase.request import SnakRequest
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.internal_representation.qualifier_hasher import QualifierHasher
from models.internal_representation.reference_hasher import ReferenceHasher
from models.internal_representation.statement_extractor import StatementExtractor
from models.internal_representation.statement_hasher import StatementHasher
from models.rest_api.entitybase.v1.service import Service
from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler
from models.validation.json_schema_validator import JsonSchemaValidator

logger = logging.getLogger(__name__)


@dataclass
class StatementProcessingContext:
    """Context for processing a single statement."""

    statement_hash: int
    statement_data: dict[str, Any]
    validator: JsonSchemaValidator | None
    schema_version: str
    idx: int
    total_statements: int


class StatementService(Service):
    @staticmethod
    def hash_entity_statements(
            entity_data: PreparedRequestData,
    ) -> OperationResult:
        """Extract and hash statements from entity data.

        Returns:
            OperationResult with StatementHashResult in data
        """
        try:
            statements = []
            full_statements = []

            claims = entity_data.claims
            logger.debug(f"Entity claims: {claims}")

            if not claims:
                logger.debug("No claims found in entity data")
                return OperationResult(success=True, data=StatementHashResult())

            properties = StatementExtractor.extract_properties_from_claims(claims)
            property_counts = StatementExtractor.compute_property_counts_from_claims(
                claims
            )

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

            logger.debug(
                f"Generated {len(statements)} hashes, properties: {properties}"
            )
            logger.debug(f"Property counts: {property_counts}")

            result = StatementHashResult(
                statements=statements,
                properties=properties,
                full_statements=full_statements,
            )
            return OperationResult(success=True, data=result)
        except Exception as e:
            logger.error(f"Failed to hash entity statements: {e}", exc_info=True)
            return OperationResult(success=False, error=str(e))

    def _process_single_statement(
        self,
        context: StatementProcessingContext,
    ) -> OperationResult:
        """Process a single statement: extract mainsnak, check S3, write, insert DB.

        Args:
            context: StatementProcessingContext containing all processing data

        Returns:
            OperationResult indicating success/failure
        """
        logger.debug(
            f"Processing statement {context.idx + 1}/{context.total_statements} with hash {context.statement_hash}"
        )

        # Extract and store mainsnak via SnakHandler
        mainsnak = context.statement_data.get("mainsnak")
        # noinspection PyUnusedLocal
        snak_hash = None
        if mainsnak:
            snak_request = SnakRequest(
                property=mainsnak.get("property"),
                datavalue=mainsnak.get("datavalue", {})
            )
            snak_handler = SnakHandler(state=self.state)
            snak_hash = snak_handler.store_snak(snak_request)
            context.statement_data = context.statement_data.copy()
            context.statement_data["mainsnak"] = {"hash": snak_hash}
            logger.debug(f"Stored mainsnak with hash {snak_hash} for statement {context.statement_hash}")

        statement_with_hash = S3Statement(
            schema=context.schema_version,
            hash=context.statement_hash,
            statement=context.statement_data,
            created_at=datetime.now(timezone.utc).isoformat() + "Z",
        )
        s3_key = f"statements/{context.statement_hash}.json"

        # Step 1: Check if S3 object exists
        # noinspection PyUnusedLocal
        s3_exists = False
        try:
            self.state.s3_client.read_statement(context.statement_hash)
            s3_exists = True
            logger.debug(f"Statement {context.statement_hash} already exists in S3")
        except Exception:
            logger.debug(
                f"Statement {context.statement_hash} not found in S3, will write new object"
            )
            s3_exists = False

        # Step 2: Validate statement before storing
        if context.validator is not None:
            context.validator.validate_statement(statement_with_hash.model_dump())

        # Step 3: Write to S3 if not exists
        if not s3_exists:
            try:
                write_start_time = time.time()
                self.state.s3_client.write_statement(
                    context.statement_hash,
                    statement_with_hash.model_dump(),
                    schema_version=context.schema_version,
                )
                write_duration = time.time() - write_start_time

                logger.info(
                    f"Successfully wrote statement {context.statement_hash} to S3 at key: {s3_key}",
                    extra={
                        "statement_hash": context.statement_hash,
                        "s3_key": s3_key,
                        "write_duration_seconds": write_duration,
                        "statement_data_size": len(
                            statement_with_hash.model_dump_json()
                        ),
                    },
                )
            except Exception as write_error:
                logger.error(
                    f"Failed to write statement {context.statement_hash} to S3",
                    extra={
                        "statement_hash": context.statement_hash,
                        "s3_key": s3_key,
                        "error_type": type(write_error).__name__,
                        "error_message": str(write_error),
                        "statement_data": context.statement_data,
                        "s3_bucket": self.state.s3_client.config.bucket,
                        "s3_endpoint": self.state.s3_client.conn.meta.endpoint_url,
                        "stack_trace": traceback.format_exc()
                        if hasattr(write_error, "__traceback__")
                        else None,
                    },
                )
                raise

        # Step 4: Insert into DB or increment ref_count
        inserted = self.state.vitess_client.insert_statement_content(
            context.statement_hash
        )
        if inserted:
            logger.debug(
                f"Inserted new statement {context.statement_hash} into statement_content"
            )
        else:
            logger.debug(
                f"Statement {context.statement_hash} already in DB, incrementing ref_count"
            )
            self.state.vitess_client.increment_ref_count(context.statement_hash)

        return OperationResult(success=True)

    def deduplicate_and_store_statements(
        self,
        hash_result: StatementHashResult,
        validator: JsonSchemaValidator | None = None,
        schema_version: str | None = None,
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
            validator: Optional JSON schema validator for statement validation
            schema_version: Version
        """
        if schema_version is None:
            schema_version = settings.s3_statement_version or "2.0.0"
        logger.debug(
            f"Deduplicating and storing {len(hash_result.statements)} statements (S3-first)"
        )

        for idx, (statement_hash, statement_data) in enumerate(
            zip(hash_result.statements, hash_result.full_statements)
        ):
            try:
                context = StatementProcessingContext(
                    statement_hash=statement_hash,
                    statement_data=statement_data,
                    validator=validator,
                    schema_version=schema_version,
                    idx=idx,
                    total_statements=len(hash_result.statements),
                )
                result = self._process_single_statement(context)
                if not result.success:
                    return result
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
                    success=False,
                    error=f"Failed to store statement {statement_hash}: {e}",
                )

        # Deduplicate references in statements
        ref_result = self.deduplicate_references_in_statements(hash_result)
        if not ref_result.success:
            return ref_result

        # Deduplicate qualifiers in statements
        qual_result = self.deduplicate_qualifiers_in_statements(hash_result)
        if not qual_result.success:
            return qual_result

        logger.info(
            f"Successfully stored all {len(hash_result.statements)} statements (new + existing)"
        )
        logger.info(f"Final statement hashes: {hash_result.statements}")
        return OperationResult(success=True)

    @staticmethod
    def _process_snak_item(item: Any, snak_handler: SnakHandler) -> int | str | dict[str, Any] | list[Any] | float | None | Any:
        """Process a single snak item.

        Returns snak hash if item is a dict with "property", otherwise original item.
        """
        if isinstance(item, dict) and "property" in item:
            snak_request = SnakRequest(
                property=item["property"],
                datavalue=item.get("datavalue", {})
            )
            return snak_handler.store_snak(snak_request)
        return item

    def _process_snak_list_value(
        self,
        snak_key: str,
        snak_list: list,
        snak_handler: SnakHandler
    ) -> tuple[str, list[Any]]:
        """Process snaks when value is a list."""
        new_snak_values = []
        for snak_item in snak_list:
            processed = self._process_snak_item(snak_item, snak_handler)
            new_snak_values.append(processed)
        return snak_key, new_snak_values

    def _process_reference_snaks(
        self,
        ref: S3ReferenceData,
        snak_handler: SnakHandler
    ) -> dict[str, Any]:
        """Process all snaks within a reference.

        Returns:
            dict[str, Any]: Modified reference data with hash-referenced snaks,
            ready to be used with S3ReferenceData.
        """
        ref_dict = ref.model_dump()
        if "snaks" in ref_dict:
            new_snaks = []
            for snak_key, snak_value in ref_dict["snaks"].items():
                if isinstance(snak_value, list):
                    new_snaks.append(
                        self._process_snak_list_value(snak_key, snak_value, snak_handler)
                    )
                elif isinstance(snak_value, dict) and "property" in snak_value:
                    snak_request = SnakRequest(
                        property=snak_value["property"],
                        datavalue=snak_value.get("datavalue", {})
                    )
                    snak_hash = snak_handler.store_snak(snak_request)
                    new_snaks.append((snak_key, [snak_hash]))
                else:
                    new_snaks.append((snak_key, snak_value))
            ref_dict["snaks"] = dict(new_snaks)
        return cast(dict[str, Any], ref_dict)

    def _process_single_reference(
        self,
        ref: S3ReferenceData | int,
        snak_handler: SnakHandler
    ) -> int:
        """Process one reference (S3ReferenceData or hash).

        Args:
            ref: S3ReferenceData instance or hash integer
            snak_handler: SnakHandler for processing snaks within reference

        Returns:
            Reference hash as integer
        """
        if isinstance(ref, S3ReferenceData):
            ref_hash = ReferenceHasher.compute_hash(ref)
            ref_dict = self._process_reference_snaks(ref, snak_handler)
            ref_data = S3ReferenceData(
                hash=ref_hash,
                reference=ref_dict,
                created_at=datetime.now(timezone.utc).isoformat() + "Z"
            )
            self.state.s3_client.store_reference(ref_hash, ref_data)
            return ref_hash
        return ref

    def _process_statement_references(
        self,
        statement_data: dict,
        snak_handler: SnakHandler
    ) -> None:
        """Process all references in a statement.

        Mutates statement_data's references in-place.
        """
        if "references" in statement_data and isinstance(
            statement_data["references"], list
        ):
            new_references = []
            for ref in statement_data["references"]:
                processed_ref = self._process_single_reference(ref, snak_handler)
                new_references.append(processed_ref)
            statement_data["references"] = new_references

    def deduplicate_references_in_statements(
        self,
        hash_result: StatementHashResult,
    ) -> OperationResult:
        """Deduplicate references in statements by storing unique references in S3.

        For each statement, extract references, compute rapidhash, store in S3 if new,
        and replace reference objects with hashes.

        Args:
            hash_result: StatementHashResult with statements to process.

        Returns:
            OperationResult indicating success/failure.
        """
        logger.debug(
            f"Deduplicating references in {len(hash_result.full_statements)} statements"
        )

        snak_handler = SnakHandler(state=self.state)

        for statement_data in hash_result.full_statements:
            self._process_statement_references(statement_data, snak_handler)

        logger.info(
            f"Reference deduplication completed for {len(hash_result.full_statements)} statements"
        )
        return OperationResult(success=True)

    def deduplicate_qualifiers_in_statements(
        self,
        hash_result: StatementHashResult,
    ) -> OperationResult:
        """Deduplicate qualifiers in statements by storing unique qualifiers in S3.

        For each statement, extract qualifiers, compute rapidhash, store in S3 if new,
        and replace qualifiers object with hash.

        Args:
            hash_result: StatementHashResult with statements to process.

        Returns:
            OperationResult indicating success/failure.
        """
        logger.debug(
            f"Deduplicating qualifiers in {len(hash_result.full_statements)} statements"
        )

        snak_handler = SnakHandler(state=self.state)
        
        for idx, statement_data in enumerate(hash_result.full_statements):
            if "qualifiers" in statement_data and isinstance(
                statement_data["qualifiers"], dict
            ):
                qualifiers_dict = statement_data["qualifiers"]
                new_qualifiers = {}
                
                # Process qualifiers and extract snaks
                for prop_key, qual_values in qualifiers_dict.items():
                    if isinstance(qual_values, list):
                        new_qual_values = []
                        for qual_item in qual_values:
                            if isinstance(qual_item, dict) and "property" in qual_item:
                                snak_request = SnakRequest(
                                    property=qual_item["property"],
                                    datavalue=qual_item.get("datavalue", {})
                                )
                                snak_hash = snak_handler.store_snak(snak_request)
                                new_qual_values.append(snak_hash)
                            else:
                                new_qual_values.append(qual_item)
                        new_qualifiers[prop_key] = new_qual_values
                    elif isinstance(qual_values, dict) and "property" in qual_values:
                        snak_request = SnakRequest(
                            property=qual_values["property"],
                            datavalue=qual_values.get("datavalue", {})
                        )
                        snak_hash = snak_handler.store_snak(snak_request)
                        new_qualifiers[prop_key] = [snak_hash]
                    else:
                        new_qualifiers[prop_key] = qual_values
                
                # Compute rapidhash
                qual_hash = QualifierHasher.compute_hash(new_qualifiers)
                # Store in S3 (idempotent)
                try:
                    qual_data = S3QualifierData(
                        qualifier=new_qualifiers,
                        hash=qual_hash,
                        created_at=datetime.now(timezone.utc).isoformat() + "Z",
                    )
                    self.state.s3_client.store_qualifier(qual_hash, qual_data)
                except Exception as e:
                    logger.warning(f"Failed to store qualifiers {qual_hash}: {e}")
                    # Continue, perhaps already exists
                # Replace with hash
                statement_data["qualifiers"] = qual_hash

        logger.info(
            f"Qualifier deduplication completed for {len(hash_result.full_statements)} statements"
        )
        return OperationResult(success=True)
