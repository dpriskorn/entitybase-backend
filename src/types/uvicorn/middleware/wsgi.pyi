import asyncio
import concurrent.futures
import io
from _typeshed import Incomplete
from collections import deque
from collections.abc import Iterable
from uvicorn._types import (
    ASGIReceiveCallable as ASGIReceiveCallable,
    ASGIReceiveEvent as ASGIReceiveEvent,
    ASGISendCallable as ASGISendCallable,
    ASGISendEvent as ASGISendEvent,
    Environ as Environ,
    ExcInfo as ExcInfo,
    HTTPRequestEvent as HTTPRequestEvent,
    HTTPResponseBodyEvent as HTTPResponseBodyEvent,
    HTTPResponseStartEvent as HTTPResponseStartEvent,
    HTTPScope as HTTPScope,
    StartResponse as StartResponse,
    WSGIApp as WSGIApp,
)

def build_environ(
    scope: HTTPScope, message: ASGIReceiveEvent, body: io.BytesIO
) -> Environ: ...

class _WSGIMiddleware:
    app: Incomplete
    executor: Incomplete
    def __init__(self, app: WSGIApp, workers: int = 10) -> None: ...
    async def __call__(
        self, scope: HTTPScope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None: ...

class WSGIResponder:
    app: Incomplete
    executor: Incomplete
    scope: Incomplete
    status: Incomplete
    response_headers: Incomplete
    send_event: Incomplete
    send_queue: deque[ASGISendEvent | None]
    loop: asyncio.AbstractEventLoop
    response_started: bool
    exc_info: ExcInfo | None
    def __init__(
        self,
        app: WSGIApp,
        executor: concurrent.futures.ThreadPoolExecutor,
        scope: HTTPScope,
    ) -> None: ...
    async def __call__(
        self, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None: ...
    async def sender(self, send: ASGISendCallable) -> None: ...
    def start_response(
        self,
        status: str,
        response_headers: Iterable[tuple[str, str]],
        exc_info: ExcInfo | None = None,
    ) -> None: ...
    def wsgi(self, environ: Environ, start_response: StartResponse) -> None: ...
