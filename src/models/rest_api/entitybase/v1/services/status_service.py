"""Service for entity status operations (lock, archive, semi-protect)."""

import json
import logging
from datetime import datetime, timezone
from enum import Enum

from models.config.settings import settings
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import (
    EditData,
    EditType,
    EntityType,
)
from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.data.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.entity_status import (
    EntityStatusRequest,
)
from models.data.rest_api.v1.entitybase.response.entity.entity_status import (
    EntityStatusResponse,
)
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.internal_representation.metadata_extractor import MetadataExtractor
from models.rest_api.entitybase.v1.service import Service
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)

from dataclasses import dataclass


@dataclass
class RevisionParams:
    """Parameters for building a revision."""

    entity_id: str
    current_revision: S3RevisionData
    new_revision_id: int
    operation: StatusOperation


class StatusOperation(str, Enum):
    """Enum for status operations."""

    LOCK = "lock"
    UNLOCK = "unlock"
    ARCHIVE = "archive"
    UNARCHIVE = "unarchive"
    SEMI_PROTECT = "semi_protect"
    UNSEMI_PROTECT = "unsemi_protect"
    MASS_EDIT_PROTECT = "mass_edit_protect"
    MASS_EDIT_UNPROTECT = "mass_edit_unprotect"


_STATUS_TARGET_MAP: dict[StatusOperation, tuple[str, bool]] = {
    StatusOperation.LOCK: ("locked", True),
    StatusOperation.UNLOCK: ("locked", False),
    StatusOperation.ARCHIVE: ("archived", True),
    StatusOperation.UNARCHIVE: ("archived", False),
    StatusOperation.SEMI_PROTECT: ("sp", True),
    StatusOperation.UNSEMI_PROTECT: ("sp", False),
    StatusOperation.MASS_EDIT_PROTECT: ("mep", True),
    StatusOperation.MASS_EDIT_UNPROTECT: ("mep", False),
}

_EDIT_TYPE_MAP: dict[StatusOperation, EditType] = {
    StatusOperation.LOCK: EditType.LOCK_ADDED,
    StatusOperation.UNLOCK: EditType.LOCK_REMOVED,
    StatusOperation.ARCHIVE: EditType.ARCHIVE_ADDED,
    StatusOperation.UNARCHIVE: EditType.ARCHIVE_REMOVED,
    StatusOperation.SEMI_PROTECT: EditType.SEMI_PROTECT_ADDED,
    StatusOperation.UNSEMI_PROTECT: EditType.SEMI_PROTECT_REMOVED,
    StatusOperation.MASS_EDIT_PROTECT: EditType.MASS_EDIT_PROTECT_ADDED,
    StatusOperation.MASS_EDIT_UNPROTECT: EditType.MASS_EDIT_PROTECT_REMOVED,
}

_STATUS_STRING_MAP: dict[StatusOperation, str] = {
    StatusOperation.LOCK: "locked",
    StatusOperation.UNLOCK: "unlocked",
    StatusOperation.ARCHIVE: "archived",
    StatusOperation.UNARCHIVE: "unarchived",
    StatusOperation.SEMI_PROTECT: "semi_protected",
    StatusOperation.UNSEMI_PROTECT: "unprotected",
    StatusOperation.MASS_EDIT_PROTECT: "mass_edit_protected",
    StatusOperation.MASS_EDIT_UNPROTECT: "mass_edit_unprotected",
}


# noinspection PyArgumentList
class StatusService(Service):
    """Service for handling entity status changes (lock, archive, semi-protect)."""

    def validate_preconditions(self) -> None:
        """Validate that required services are initialized."""
        if self.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

    def validate_entity_exists(self, entity_id: str) -> int:
        """Validate entity exists and retrieve current head revision.

        Args:
            entity_id: The entity ID to validate

        Returns:
            The current head revision ID

        Raises:
            HTTPException: If entity doesn't exist
        """
        if not self.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        if self.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error(
                f"Entity {entity_id} has been deleted", status_code=410
            )

        head_revision_id = self.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity not found", status_code=404)

        logger.debug(f"Current head revision for {entity_id}: {head_revision_id}")
        return int(head_revision_id)

    def change_status(
        self,
        entity_id: str,
        operation: StatusOperation,
        request: EntityStatusRequest,
    ) -> EntityStatusResponse:
        """Change entity status (lock, archive, semi-protect, or their opposites).

        Args:
            entity_id: The entity ID
            operation: The status operation to perform
            request: The status change request

        Returns:
            EntityStatusResponse with the result
        """
        self.validate_preconditions()
        head_revision_id = self.validate_entity_exists(entity_id)

        try:
            current_revision = self.state.s3_client.read_revision(
                entity_id, head_revision_id
            )
        except Exception:
            raise_validation_error(
                f"Entity revision not found: {entity_id}", status_code=404
            )

        current_state = current_revision.revision.get("state", {})
        if current_state is None:
            current_state = {}

        idempotent = False
        new_revision_id = head_revision_id

        target_status = self._get_target_state(operation, current_state)

        is_already_in_target_state = self._check_is_in_target_state(
            operation, current_state
        )

        if is_already_in_target_state:
            idempotent = True
            logger.info(
                f"Entity {entity_id} is already in target state for {operation.value}, returning idempotent response"
            )
            return EntityStatusResponse(
                id=entity_id,
                rev_id=head_revision_id,
                status=self._get_status_string(operation),
                idempotent=idempotent,
            )

        new_revision_id = head_revision_id + 1

        edit_type = self._get_edit_type(operation)
        edit_context = EditContext(
            user_id=0,
            edit_summary=request.edit_summary or f"{operation.value} entity",
        )

        revision_data = self._build_status_revision(
            params=RevisionParams(
                entity_id=entity_id,
                current_revision=current_revision,
                new_revision_id=new_revision_id,
                operation=operation,
            ),
            edit_context=edit_context,
            edit_type=edit_type,
        )

        content_hash, s3_revision_data = self._store_revision(revision_data)

        self.state.vitess_client.create_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            entity_data=revision_data,
            expected_revision_id=head_revision_id,
            content_hash=content_hash,
        )

        logger.info(
            f"Entity {entity_id}: Successfully changed status to {operation.value}, "
            f"revision {new_revision_id}"
        )

        return EntityStatusResponse(
            id=entity_id,
            rev_id=new_revision_id,
            status=self._get_status_string(operation),
            idempotent=idempotent,
        )

    def _get_target_state(
        self, operation: StatusOperation, current_state: dict
    ) -> EntityState:
        """Get the target EntityState based on the operation."""
        return EntityState(
            sp=current_state.get("sp", False),
            locked=current_state.get("locked", False),
            archived=current_state.get("archived", False),
            dangling=current_state.get("dangling", False),
            mep=current_state.get("mep", False),
            deleted=current_state.get("deleted", False),
        )

    def _check_is_in_target_state(
        self, operation: StatusOperation, current_state: dict
    ) -> bool:
        """Check if entity is already in the target state (idempotent case)."""
        state = current_state if current_state else {}
        target_key, target_value = self._get_target_state_key_value(operation)
        return state.get(target_key, False) is target_value

    def _get_target_state_key_value(
        self, operation: StatusOperation
    ) -> tuple[str, bool]:
        """Get the state key and target value for an operation."""
        return _STATUS_TARGET_MAP.get(operation, ("locked", False))

    def _get_edit_type(self, operation: StatusOperation) -> EditType:
        """Get the EditType for the operation."""
        return _EDIT_TYPE_MAP.get(operation, EditType.MANUAL_UPDATE)

    def _get_status_string(self, operation: StatusOperation) -> str:
        """Get the status string for the response."""
        return _STATUS_STRING_MAP.get(operation, "unspecified")

    def _build_status_revision(
        self,
        params: RevisionParams,
        edit_context: EditContext,
        edit_type: EditType,
    ) -> RevisionData:
        """Build the status change revision data."""
        entity_id = params.entity_id
        current_revision = params.current_revision
        new_revision_id = params.new_revision_id
        operation = params.operation

        current_state = current_revision.revision.get("state", {})
        if current_state is None:
            current_state = {}

        new_sp = current_state.get("sp", False)
        new_locked = current_state.get("locked", False)
        new_archived = current_state.get("archived", False)
        new_dangling = current_state.get("dangling", False)
        new_mep = current_state.get("mep", False)

        match operation:
            case StatusOperation.LOCK:
                new_locked = True
            case StatusOperation.UNLOCK:
                new_locked = False
            case StatusOperation.ARCHIVE:
                new_archived = True
            case StatusOperation.UNARCHIVE:
                new_archived = False
            case StatusOperation.SEMI_PROTECT:
                new_sp = True
            case StatusOperation.UNSEMI_PROTECT:
                new_sp = False
            case StatusOperation.MASS_EDIT_PROTECT:
                new_mep = True
            case StatusOperation.MASS_EDIT_UNPROTECT:
                new_mep = False

        logger.debug(
            f"Status flags updated: sp={new_sp}, locked={new_locked}, "
            f"archived={new_archived}, dangling={new_dangling}, mep={new_mep}"
        )

        logger.debug(
            f"Building status revision for {entity_id}, revision {new_revision_id}, "
            f"operation={operation.value}, edit_type={edit_type.value}"
        )

        revision = RevisionData(
            schema_version=settings.s3_schema_revision_version,
            revision_id=new_revision_id,
            entity_type=EntityType(
                current_revision.revision.get("entity_type", "item")
            ),
            properties=current_revision.revision.get("properties", {}),
            property_counts=current_revision.revision.get("property_counts", {}),
            hashes=HashMaps(
                statements=StatementsHashes(
                    root=current_revision.revision.get("statements", [])
                ),
                sitelinks=SitelinkHashes(
                    root=current_revision.revision.get("sitelinks", {})
                ),
                labels=LabelsHashes(
                    root=current_revision.revision.get("labels_hashes", {})
                ),
                descriptions=DescriptionsHashes(
                    root=current_revision.revision.get("descriptions_hashes", {})
                ),
                aliases=AliasesHashes(
                    root=current_revision.revision.get("aliases_hashes", {})
                ),
            ),
            edit=EditData(
                mass=False,
                type=edit_type,
                user_id=edit_context.user_id,
                summary=edit_context.edit_summary,
                at=datetime.now(timezone.utc).isoformat(),
            ),
            state=EntityState(
                sp=new_sp,
                locked=new_locked,
                archived=new_archived,
                dangling=new_dangling,
                mep=new_mep,
                deleted=current_state.get("deleted", False),
            ),
        )

        logger.debug(
            f"Status revision built for {entity_id}, revision {new_revision_id}"
        )

        return revision

    def _store_revision(
        self, revision_data: RevisionData
    ) -> tuple[int, S3RevisionData]:
        """Store the revision to S3."""
        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self.state.s3_client.store_revision(content_hash, s3_revision_data)
        return content_hash, s3_revision_data
