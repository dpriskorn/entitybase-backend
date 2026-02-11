"""REST API request models."""

# Request models

from .endorsements import EndorsementListRequest
from .entity_filter import EntityFilterRequest
from .enums import UserActivityType
from .edit_context import EditContext
from .entity import (
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityInsertDataRequest,
    EntityJsonImportRequest,
    EventPublishContext,
    EntityRedirectRequest,
    EntityRevertRequest,
    LexemeUpdateRequest,
    RedirectRevertRequest,
)
from .entity.term_update import (
    DescriptionUpdateRequest,
    LabelUpdateRequest,
    TermUpdateRequest,
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
    "DescriptionUpdateRequest",
    "EditContext",
    "EndorsementListRequest",
    "EntityCreateRequest",
    "EntityDeleteRequest",
    "EntityFilterRequest",
    "EntityInsertDataRequest",
    "EntityJsonImportRequest",
    "EntityRedirectRequest",
    "EntityRevertRequest",
    "EventPublishContext",
    "LabelPatchRequest",
    "LabelUpdateRequest",
    "LexemeUpdateRequest",
    "MarkCheckedRequest",
    "MostUsedStatementsRequest",
    "PatchStatementRequest",
    "RedirectRevertRequest",
    "RemoveStatementRequest",
    "SitelinkPatchRequest",
    "SnakRequest",
    "StatePatchRequest",
    "StatementBatchRequest",
    "TermUpdateRequest",
    "ThanksListRequest",
    "UserActivityRequest",
    "UserCreateRequest",
    "UserPreferencesRequest",
    "WatchlistAddRequest",
    "WatchlistRemoveRequest",
    "WatchlistToggleRequest",
]
