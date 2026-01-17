import asyncio
from _typeshed import Incomplete
from asyncio.transports import BaseTransport
from typing import Any, Literal
from uvicorn._types import (
    ASGIReceiveEvent as ASGIReceiveEvent,
    ASGISendEvent as ASGISendEvent,
    WebSocketAcceptEvent as WebSocketAcceptEvent,
    WebSocketCloseEvent as WebSocketCloseEvent,
    WebSocketResponseBodyEvent as WebSocketResponseBodyEvent,
    WebSocketResponseStartEvent as WebSocketResponseStartEvent,
    WebSocketScope as WebSocketScope,
    WebSocketSendEvent as WebSocketSendEvent,
)
from uvicorn.config import Config as Config
from uvicorn.logging import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL
from uvicorn.protocols.utils import (
    ClientDisconnected as ClientDisconnected,
    get_local_addr as get_local_addr,
    get_path_with_query_string as get_path_with_query_string,
    get_remote_addr as get_remote_addr,
    is_ssl as is_ssl,
)
from uvicorn.server import ServerState as ServerState
from websockets.frames import Frame
from websockets.http11 import Request

class WebSocketsSansIOProtocol(asyncio.Protocol):
    config: Incomplete
    app: Incomplete
    loop: Incomplete
    logger: Incomplete
    root_path: Incomplete
    app_state: Incomplete
    connections: Incomplete
    tasks: Incomplete
    default_headers: Incomplete
    transport: asyncio.Transport
    server: tuple[str, int] | None
    client: tuple[str, int] | None
    scheme: Literal["wss", "ws"]
    queue: asyncio.Queue[ASGIReceiveEvent]
    handshake_initiated: bool
    handshake_complete: bool
    close_sent: bool
    initial_response: tuple[int, list[tuple[str, str]], bytes] | None
    conn: Incomplete
    read_paused: bool
    writable: Incomplete
    bytes: bytes
    def __init__(
        self,
        config: Config,
        server_state: ServerState,
        app_state: dict[str, Any],
        _loop: asyncio.AbstractEventLoop | None = None,
    ) -> None: ...
    def connection_made(self, transport: BaseTransport) -> None: ...
    def connection_lost(self, exc: Exception | None) -> None: ...
    def eof_received(self) -> None: ...
    def shutdown(self) -> None: ...
    def data_received(self, data: bytes) -> None: ...
    def handle_events(self) -> None: ...
    request: Incomplete
    response: Incomplete
    scope: WebSocketScope
    def handle_connect(self, event: Request) -> None: ...
    def handle_cont(self, event: Frame) -> None: ...
    curr_msg_data_type: Literal["text", "bytes"]
    def handle_text(self, event: Frame) -> None: ...
    def handle_bytes(self, event: Frame) -> None: ...
    def send_receive_event_to_app(self) -> None: ...
    def handle_ping(self) -> None: ...
    def handle_close(self, event: Frame) -> None: ...
    def handle_parser_exception(self) -> None: ...
    def on_task_complete(self, task: asyncio.Task[None]) -> None: ...
    async def run_asgi(self) -> None: ...
    def send_500_response(self) -> None: ...
    async def send(self, message: ASGISendEvent) -> None: ...
    async def receive(self) -> ASGIReceiveEvent: ...
