from _typeshed import Incomplete

MAX_ACTIVE_CONTEXTS: int

class ResolvedContext:
    document: Incomplete
    cache: Incomplete
    def __init__(self, document) -> None: ...
    def get_processed(self, active_ctx): ...
    def set_processed(self, active_ctx, processed_ctx) -> None: ...
