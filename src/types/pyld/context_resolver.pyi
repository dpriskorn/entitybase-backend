from .resolved_context import ResolvedContext as ResolvedContext
from _typeshed import Incomplete
from pyld import jsonld as jsonld

MAX_CONTEXT_URLS: int

class ContextResolver:
    per_op_cache: Incomplete
    shared_cache: Incomplete
    document_loader: Incomplete
    def __init__(self, shared_cache, document_loader) -> None: ...
    def resolve(self, active_ctx, context, base, cycles=None): ...
