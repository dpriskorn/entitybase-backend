from _typeshed import Incomplete

MAX_ACTIVE_CONTEXTS: int

class ResolvedContext:
    document: Incomplete
    cache: Incomplete
    def __init__(self, document: Any) -> None: ...
    def get_processed(self, active_ctx: Any) -> Any: ...
    def set_processed(self, active_ctx: Any, processed_ctx: Any) -> None: ...
