"""Entity request models."""

from .crud import (
    EntityCreateRequest,
    EntityDeleteRequest,
    EntityInsertDataRequest,
    LexemeUpdateRequest,
    PreparedRequestData,
)
from .misc import EntityJsonImportRequest, EntityRedirectRequest
from .revert import EntityRevertRequest, RedirectRevertRequest

# Keep EntityUpdateRequest internal-only for lexeme compatibility
from .crud import EntityUpdateRequest
