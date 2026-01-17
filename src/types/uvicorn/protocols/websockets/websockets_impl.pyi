import asyncio
import logging
from _typeshed import Incomplete
from collections.abc import Sequence
from typing import Any, Literal
from uvicorn._types import (
    ASGI3Application as ASGI3Application,
    ASGISendEvent as ASGISendEvent,
    WebSocketAcceptEvent as WebSocketAcceptEvent,
    WebSocketCloseEvent as WebSocketCloseEvent,
    WebSocketConnectEvent as WebSocketConnectEvent,
    WebSocketDisconnectEvent as WebSocketDisconnectEvent,
    WebSocketReceiveEvent as WebSocketReceiveEvent,
    WebSocketResponseBodyEvent as WebSocketResponseBodyEvent,
    WebSocketResponseStartEvent as WebSocketResponseStartEvent,
    WebSocketScope as WebSocketScope,
    WebSocketSendEvent as WebSocketSendEvent,
)
from uvicorn.config import Config as Config
from uvicorn.logging import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL
from uvicorn.protocols.utils import (
    ClientDisconnected as ClientDisconnected,
    get_client_addr as get_client_addr,
    get_local_addr as get_local_addr,
    get_path_with_query_string as get_path_with_query_string,
    get_remote_addr as get_remote_addr,
    is_ssl as is_ssl,
)
from uvicorn.server import ServerState as ServerState
from websockets.datastructures import Headers as Headers
from websockets.extensions.base import ServerExtensionFactory as ServerExtensionFactory
from websockets.legacy.server import HTTPResponse as HTTPResponse
from websockets.server import WebSocketServerProtocol
from websockets.typing import Subprotocol

class Server:
    closing: bool
    def register(self, ws: WebSocketServerProtocol) -> None: ...
    def unregister(self, ws: WebSocketServerProtocol) -> None: ...
    def is_serving(self) -> bool: ...

class WebSocketProtocol(WebSocketServerProtocol):
    extra_headers: list[tuple[str, str]]
    logger: logging.Logger | logging.LoggerAdapter[Any]
    config: Incomplete
    app: Incomplete
    loop: Incomplete
    root_path: Incomplete
    app_state: Incomplete
    connections: Incomplete
    tasks: Incomplete
    transport: asyncio.Transport
    server: tuple[str, int] | None
    client: tuple[str, int] | None
    scheme: Literal["wss", "ws"]
    scope: WebSocketScope
    handshake_started_event: Incomplete
    handshake_completed_event: Incomplete
    closed_event: Incomplete
    initial_response: HTTPResponse | None
    connect_sent: bool
    lost_connection_before_handshake: bool
    accepted_subprotocol: Subprotocol | None
    ws_server: Server
    server_header: Incomplete
    def __init__(
        self,
        config: Config,
        server_state: ServerState,
        app_state: dict[str, Any],
        _loop: asyncio.AbstractEventLoop | None = None,
    ) -> None: ...
    def connection_made(self, transport: asyncio.Transport) -> None: ...
    def connection_lost(self, exc: Exception | None) -> None: ...
    def shutdown(self) -> None: ...
    def on_task_complete(self, task: asyncio.Task[None]) -> None: ...
    async def process_request(
        self, path: str, request_headers: Headers
    ) -> HTTPResponse | None: ...
    def process_subprotocol(
        self, headers: Headers, available_subprotocols: Sequence[Subprotocol] | None
    ) -> Subprotocol | None: ...
    def send_500_response(self) -> None: ...
    async def ws_handler(self, protocol: WebSocketServerProtocol, path: str) -> Any: ...
    async def run_asgi(self) -> None: ...
    async def asgi_send(self, message: ASGISendEvent) -> None: ...
    async def asgi_receive(
        self,
    ) -> WebSocketDisconnectEvent | WebSocketConnectEvent | WebSocketReceiveEvent: ...
