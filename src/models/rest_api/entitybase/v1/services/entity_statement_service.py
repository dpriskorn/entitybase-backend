"""Entity statement modification service."""

import logging
from datetime import datetime, timezone
from typing import Any

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.common import OperationResult
from models.data.infrastructure.s3.enums import EditType
from models.data.raw_entity import RawEntityData
from models.data.rest_api.v1.entitybase.request import AddPropertyRequest
from models.data.rest_api.v1.entitybase.request import AddStatementRequest
from models.data.rest_api.v1.entitybase.request import PatchStatementRequest
from models.data.rest_api.v1.entitybase.response import (
    EntityResponse,
    PropertyRecalculationResult,
    RevisionIdResult,
)
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.infrastructure.vitess.repositories.statement import StatementRepository
from models.internal_representation.statement_hasher import StatementHasher
from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler
from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.v1.service import Service
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class _PropertyCountHelper:
    """Utility class for property count recalculation."""

    @staticmethod
    def recalculate_property_counts(
        revision_data: RevisionData, index: int
    ) -> PropertyRecalculationResult:
        """Recalculate properties and property_counts after statement removal.

        Args:
            revision_data: Revision data object with properties and property_counts
            index: Index of the removed statement

        Returns:
            PropertyRecalculationResult with updated properties and counts
        """
        from models.data.infrastructure.s3.property_counts import PropertyCounts

        start = 0
        new_properties = []
        new_property_counts_dict = {}

        for prop in revision_data.properties:
            count = revision_data.property_counts.get(prop, 0)
            if start <= index < start + count:
                count -= 1
            if count > 0:
                new_properties.append(prop)
                new_property_counts_dict[prop] = count
            start += count

        # noinspection PyArgumentList
        return PropertyRecalculationResult(
            properties=new_properties,
            property_counts=PropertyCounts(root=new_property_counts_dict),
        )


class EntityStatementService(Service):
    """Service for entity statement modification operations."""

    async def add_property(
        self,
        entity_id: str,
        property_id: str,
        request: AddPropertyRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> OperationResult[RevisionIdResult]:
        """Add claims for a single property to an existing entity."""
        logger.info(
            f"Entity {entity_id}: Adding property {property_id} with {len(request.claims)} claims"
        )
        self._validate_property_id(property_id)
        self._validate_property_exists(property_id)
        current_data = self._fetch_current_entity_data(entity_id)
        self._merge_claims(current_data.data, property_id, request.claims)
        entity_response = await self._process_entity_update(
            entity_id,
            current_data.data,
            edit_headers,
            validator,
        )
        return OperationResult(
            success=True,
            data=RevisionIdResult(revision_id=entity_response.rev_id),
        )

    async def remove_statement(
        self,
        entity_id: str,
        statement_hash: str,
        edit_headers: EditHeaders,
    ) -> OperationResult[RevisionIdResult]:
        """Remove a statement by hash from an entity."""
        logger.info(f"Entity {entity_id}: Removing statement {statement_hash}")
        head_revision_id = self.state.vitess_client.get_head(entity_id)
        revision_data = self._fetch_revision_data(entity_id, head_revision_id)
        result = self._remove_statement_from_revision(revision_data, statement_hash)
        if not result.success:
            return result
        self._decrement_statement_ref_count(statement_hash)
        new_revision_id = await self._store_updated_revision(
            revision_data, entity_id, head_revision_id, edit_headers
        )
        return OperationResult(
            success=True,
            data=RevisionIdResult(revision_id=entity_response.rev_id),
        )

    async def add_statement(
        self,
        entity_id: str,
        request: AddStatementRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> OperationResult[RevisionIdResult]:
        """Add a single statement to an entity."""
        logger.info(f"Entity {entity_id}: Adding single statement")
        claim = request.claim
        property_id = claim.get("property", {}).get("id") or claim.get(
            "mainsnak", {}
        ).get("property")
        if not property_id:
            raise_validation_error("Statement must have a property ID", status_code=400)

        self._validate_property_id(property_id)
        self._validate_property_exists(property_id)

        add_property_request = AddPropertyRequest(claims=[claim])
        return await self.add_property(
            entity_id, property_id, add_property_request, edit_headers, validator
        )

    async def patch_statement(
        self,
        entity_id: str,
        statement_hash: str,
        request: PatchStatementRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
    ) -> OperationResult[RevisionIdResult]:
        """Replace a statement by hash with new claim data."""
        logger.info(f"Entity {entity_id}: Patching statement {statement_hash}")
        current_data = self._fetch_current_entity_data(entity_id)
        replaced = self._find_and_replace_statement(
            current_data.data, statement_hash, request.claim
        )
        if not replaced:
            return OperationResult(success=False, error="Statement not found in entity")
        entity_response = await self._process_entity_update(
            entity_id,
            current_data.data,
            edit_headers,
            validator,
        )
        return OperationResult(
            success=True,
            data=RevisionIdResult(revision_id=entity_response.rev_id),
        )

    # Private validation methods
    @staticmethod
    def _validate_property_id(property_id: str) -> None:
        """Validate property ID format."""
        if not property_id.startswith("P") or not property_id[1:].isdigit():
            raise_validation_error("Invalid property ID format", status_code=400)

    def _validate_property_exists(self, property_id: str) -> None:
        """Validate that property exists and is a property type."""
        try:
            read_handler = EntityReadHandler(state=self.state)
            property_response = read_handler.get_entity(property_id)
            entity_type = property_response.entity_data.revision.get("entity_type")
            if entity_type != "property":
                raise_validation_error("Entity is not a property", status_code=400)
        except Exception:
            raise_validation_error("Property does not exist", status_code=400)

    # Private data fetching methods
    def _fetch_current_entity_data(self, entity_id: str) -> RawEntityData:
        """Fetch current entity data."""
        try:
            read_handler = EntityReadHandler(state=self.state)
            entity_response = read_handler.get_entity(entity_id)
            return RawEntityData(data=entity_response.entity_data.revision)
        except Exception as e:
            raise_validation_error(f"Failed to fetch entity: {e}", status_code=400)

    def _fetch_current_entity(self, entity_id: str) -> EntityResponse:
        """Fetch current entity response."""
        try:
            read_handler = EntityReadHandler(state=self.state)
            return read_handler.get_entity(entity_id)
        except S3NotFoundError:
            raise_validation_error(f"Entity not found: {entity_id}", status_code=404)
        except Exception as e:
            raise_validation_error(f"Failed to fetch entity: {e}", status_code=400)

    def _fetch_revision_data(self, entity_id: str, revision_id: int) -> RevisionData:
        """Fetch revision data from S3."""
        try:
            s3_revision_data = self.state.s3_client.read_revision(
                entity_id, revision_id
            )
            from models.data.infrastructure.s3.revision_data import S3RevisionData

            if not isinstance(s3_revision_data, S3RevisionData):
                raise_validation_error("Invalid revision data type", status_code=500)
            return RevisionData.model_validate(s3_revision_data.revision)  # type: ignore[no-any-return]
        except S3NotFoundError:
            raise_validation_error(
                f"Revision not found: {entity_id} revision {revision_id}",
                status_code=404,
            )
        except Exception as e:
            raise_validation_error(f"Failed to fetch revision: {e}", status_code=400)

    # Private data manipulation methods
    @staticmethod
    def _merge_claims(
        current_data: dict[str, Any], property_id: str, claims: list
    ) -> None:
        """Merge claims into current entity data."""
        if "claims" not in current_data:
            current_data["claims"] = {}
        if property_id not in current_data["claims"]:
            current_data["claims"][property_id] = []
        current_data["claims"][property_id].extend(claims)

    @staticmethod
    def _remove_statement_from_revision(
        revision_data: RevisionData, statement_hash: str
    ) -> OperationResult:
        """Remove statement hash from revision data and recalculate property counts."""
        if (
            not hasattr(revision_data.hashes, "statements")
            or not revision_data.hashes.statements
        ):
            return OperationResult(
                success=False, error="No statements found in revision"
            )
        try:
            hash_int = int(statement_hash)
            if hash_int in revision_data.hashes.statements.root:
                index = revision_data.hashes.statements.root.index(hash_int)
                revision_data.hashes.statements.root.pop(index)
                recalc_result = _PropertyCountHelper.recalculate_property_counts(
                    revision_data, index
                )
                revision_data.properties = recalc_result.properties
                revision_data.property_counts = recalc_result.property_counts
            else:
                return OperationResult(success=False, error="Statement hash not found")
        except ValueError:
            return OperationResult(success=False, error="Invalid statement hash format")
        return OperationResult(success=True)

    def _decrement_statement_ref_count(self, statement_hash: str) -> None:
        """Decrement ref_count for a statement."""
        stmt_repo = StatementRepository(vitess_client=self.state.vitess_client)
        result = stmt_repo.decrement_ref_count(int(statement_hash))
        if not result.success:
            raise_validation_error(
                f"Failed to decrement ref_count for statement {statement_hash}: {result.error}",
                status_code=500,
            )

    async def _store_updated_revision(
        self,
        revision_data: RevisionData,
        entity_id: str,
        head_revision_id: int,
        edit_headers: EditHeaders,
    ) -> int:
        """Store updated revision and return new revision ID."""
        logger.debug(f"Storing updated revision for entity {entity_id}")
        new_revision_id = revision_data.revision_id + 1
        logger.debug(f"New revision ID: {new_revision_id}")
        revision_data.revision_id = new_revision_id
        revision_data.edit.summary = edit_headers.x_edit_summary
        revision_data.edit.at = datetime.now(timezone.utc).isoformat()
        revision_data.edit.user_id = edit_headers.x_user_id
        try:
            from models.data.infrastructure.s3.revision_data import S3RevisionData

            logger.debug("Converting revision data to dict")
            revision_dict = revision_data.model_dump(mode="json")
            from rapidhash import rapidhash

            logger.debug("Computing content hash")
            content_hash = rapidhash(str(revision_dict).encode())
            logger.debug(f"Content hash: {content_hash}")
            s3_revision_data = S3RevisionData(
                schema=revision_data.schema_version,
                revision=revision_dict,
                hash=content_hash,
                created_at=revision_data.created_at,
            )
            logger.debug("Storing revision to S3")
            self.state.s3_client.store_revision(content_hash, s3_revision_data)
            logger.debug("Updating head revision in Vitess")
            self.state.vitess_client.update_head_revision(entity_id, new_revision_id)
        except Exception as e:
            logger.error(f"Failed to store updated revision: {e}")
            raise_validation_error(
                f"Failed to store updated revision: {e}", status_code=400
            )
        return new_revision_id

    @staticmethod
    def _find_and_replace_statement(
        current_data: dict[str, Any],
        statement_hash: str,
        claim: dict,
    ) -> bool:
        """Find and replace statement by hash."""
        replaced = False
        if "claims" in current_data:
            for property_id, claim_list in current_data["claims"].items():
                for i, stmt in enumerate(claim_list):
                    stmt_hash = StatementHasher.compute_hash(stmt)
                    if str(stmt_hash) == statement_hash:
                        claim_list[i] = claim
                        replaced = True
                        break
                if replaced:
                    break
        return replaced

    async def _process_entity_update(
        self,
        entity_id: str,
        current_data: dict[str, Any],
        edit_headers: EditHeaders,
        validator: Any | None,
    ) -> EntityResponse:
        """Process entity update using new architecture."""
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            ProcessEntityRevisionContext,
        )

        read_handler = EntityReadHandler(state=self.state)
        entity_response = read_handler.get_entity(entity_id)
        handler = EntityHandler(state=self.state)
        ctx = ProcessEntityRevisionContext(
            entity_id=entity_id,
            request_data=current_data,
            entity_type=entity_response.entity_data.revision.get("entity_type"),
            edit_type=EditType.UNSPECIFIED,
            edit_headers=edit_headers,
            is_creation=False,
            validator=validator,
        )
        return await handler.process_entity_revision_new(ctx)  # type: ignore
