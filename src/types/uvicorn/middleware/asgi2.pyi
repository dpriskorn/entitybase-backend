from _typeshed import Incomplete
from uvicorn._types import (
    ASGI2Application as ASGI2Application,
    ASGIReceiveCallable as ASGIReceiveCallable,
    ASGISendCallable as ASGISendCallable,
    Scope as Scope,
)

class ASGI2Middleware:
    app: Incomplete
    def __init__(self, app: ASGI2Application) -> None: ...
    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None: ...
