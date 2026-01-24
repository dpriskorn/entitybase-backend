"""REST API request models."""

# Request models

from .endorsements import EndorsementListRequest
from .enums import UserActivityType
from .entity import (
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityInsertDataRequest,
    EntityJsonImportRequest,
    EntityRedirectRequest,
    EntityRevertRequest,
    EntityUpdateRequest,
    RedirectRevertRequest,
)
from .entity.add_property import AddPropertyRequest
from .entity.patch import (
    AliasPatchRequest,
    BasePatchRequest,
    ClaimPatchRequest,
    DescriptionPatchRequest,
    LabelPatchRequest,
    SitelinkPatchRequest,
    StatePatchRequest,
)
from .entity.patch_statement import PatchStatementRequest
from .entity.remove_statement import RemoveStatementRequest
from .misc import CleanupOrphanedRequest
from .snak import SnakRequest
from .statement import (
    MostUsedStatementsRequest,
    StatementBatchRequest,
)
from .thanks import ThanksListRequest
from .user import (
    MarkCheckedRequest,
    UserCreateRequest,
    WatchlistAddRequest,
    WatchlistRemoveRequest,
    WatchlistToggleRequest,
)
from .user_activity import UserActivityRequest
from .user_preferences import UserPreferencesRequest

__all__ = [
    "AddPropertyRequest",
    "AliasPatchRequest",
    "BasePatchRequest",
    "ClaimPatchRequest",
    "CleanupOrphanedRequest",
    "DescriptionPatchRequest",
    "EndorsementListRequest",
    "EntityCreateRequest",
    "EntityDeleteRequest",
    "EntityInsertDataRequest",
    "EntityJsonImportRequest",
    "EntityRedirectRequest",
    "EntityRevertRequest",
    "EntityUpdateRequest",
    "LabelPatchRequest",
    "MarkCheckedRequest",
    "MostUsedStatementsRequest",
    "PatchStatementRequest",
    "RedirectRevertRequest",
    "RemoveStatementRequest",
    "SitelinkPatchRequest",
    "SnakRequest",
    "StatePatchRequest",
    "StatementBatchRequest",
    "ThanksListRequest",
    "UserActivityRequest",
    "UserCreateRequest",
    "UserPreferencesRequest",
    "WatchlistAddRequest",
    "WatchlistRemoveRequest",
    "WatchlistToggleRequest",
]
