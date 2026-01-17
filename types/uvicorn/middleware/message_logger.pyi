from _typeshed import Incomplete
from typing import Any
from uvicorn._types import (
    ASGI3Application as ASGI3Application,
    ASGIReceiveCallable as ASGIReceiveCallable,
    ASGIReceiveEvent as ASGIReceiveEvent,
    ASGISendCallable as ASGISendCallable,
    ASGISendEvent as ASGISendEvent,
    WWWScope as WWWScope,
)
from uvicorn.logging import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL

PLACEHOLDER_FORMAT: Incomplete

def message_with_placeholders(message: Any) -> Any: ...

class MessageLoggerMiddleware:
    task_counter: int
    app: Incomplete
    logger: Incomplete
    def __init__(self, app: ASGI3Application) -> None: ...
    async def __call__(
        self, scope: WWWScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None: ...
