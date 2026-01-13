"""Entity request models."""

from .crud import (
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityUpdateRequest,
    RevisionInsertDataRequest,
)
from .misc import EntityJsonImportRequest, EntityRedirectRequest
from .revert import EntityRevertRequest, RedirectRevertRequest
