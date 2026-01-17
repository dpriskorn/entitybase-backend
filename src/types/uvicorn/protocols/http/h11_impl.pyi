import asyncio
import h11
import http
import logging
from _typeshed import Incomplete
from collections.abc import Callable as Callable
from typing import Any, Literal
from uvicorn._types import (
    ASGI3Application as ASGI3Application,
    ASGIReceiveEvent as ASGIReceiveEvent,
    ASGISendEvent as ASGISendEvent,
    HTTPRequestEvent as HTTPRequestEvent,
    HTTPResponseBodyEvent as HTTPResponseBodyEvent,
    HTTPResponseStartEvent as HTTPResponseStartEvent,
    HTTPScope as HTTPScope,
)
from uvicorn.config import Config as Config
from uvicorn.logging import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL
from uvicorn.protocols.http.flow_control import (
    CLOSE_HEADER as CLOSE_HEADER,
    FlowControl as FlowControl,
    HIGH_WATER_LIMIT as HIGH_WATER_LIMIT,
    service_unavailable as service_unavailable,
)
from uvicorn.protocols.utils import (
    get_client_addr as get_client_addr,
    get_local_addr as get_local_addr,
    get_path_with_query_string as get_path_with_query_string,
    get_remote_addr as get_remote_addr,
    is_ssl as is_ssl,
)
from uvicorn.server import ServerState as ServerState

STATUS_PHRASES: Incomplete

class H11Protocol(asyncio.Protocol):
    config: Incomplete
    app: Incomplete
    loop: Incomplete
    logger: Incomplete
    access_logger: Incomplete
    access_log: Incomplete
    conn: Incomplete
    ws_protocol_class: Incomplete
    root_path: Incomplete
    limit_concurrency: Incomplete
    app_state: Incomplete
    timeout_keep_alive_task: asyncio.TimerHandle | None
    timeout_keep_alive: Incomplete
    server_state: Incomplete
    connections: Incomplete
    tasks: Incomplete
    transport: asyncio.Transport
    flow: FlowControl
    server: tuple[str, int] | None
    client: tuple[str, int] | None
    scheme: Literal["http", "https"] | None
    scope: HTTPScope
    headers: list[tuple[bytes, bytes]]
    cycle: RequestResponseCycle
    def __init__(
        self,
        config: Config,
        server_state: ServerState,
        app_state: dict[str, Any],
        _loop: asyncio.AbstractEventLoop | None = None,
    ) -> None: ...
    def connection_made(self, transport: asyncio.Transport) -> None: ...
    def connection_lost(self, exc: Exception | None) -> None: ...
    def eof_received(self) -> None: ...
    def data_received(self, data: bytes) -> None: ...
    def handle_events(self) -> None: ...
    def handle_websocket_upgrade(self, event: h11.Request) -> None: ...
    def send_400_response(self, msg: str) -> None: ...
    def on_response_complete(self) -> None: ...
    def shutdown(self) -> None: ...
    def pause_writing(self) -> None: ...
    def resume_writing(self) -> None: ...
    def timeout_keep_alive_handler(self) -> None: ...

class RequestResponseCycle:
    scope: Incomplete
    conn: Incomplete
    transport: Incomplete
    flow: Incomplete
    logger: Incomplete
    access_logger: Incomplete
    access_log: Incomplete
    default_headers: Incomplete
    message_event: Incomplete
    on_response: Incomplete
    disconnected: bool
    keep_alive: bool
    waiting_for_100_continue: Incomplete
    body: bytes
    more_body: bool
    response_started: bool
    response_complete: bool
    def __init__(
        self,
        scope: HTTPScope,
        conn: h11.Connection,
        transport: asyncio.Transport,
        flow: FlowControl,
        logger: logging.Logger,
        access_logger: logging.Logger,
        access_log: bool,
        default_headers: list[tuple[bytes, bytes]],
        message_event: asyncio.Event,
        on_response: Callable[..., None],
    ) -> None: ...
    async def run_asgi(self, app: ASGI3Application) -> None: ...
    async def send_500_response(self) -> None: ...
    async def send(self, message: ASGISendEvent) -> None: ...
    async def receive(self) -> ASGIReceiveEvent: ...
