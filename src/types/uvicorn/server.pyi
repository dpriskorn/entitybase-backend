import asyncio
import contextlib
import socket
from _typeshed import Incomplete
from collections.abc import Generator
from types import FrameType
from typing import TypeAlias
from uvicorn._compat import asyncio_run as asyncio_run
from uvicorn.config import Config as Config
from uvicorn.protocols.http.h11_impl import H11Protocol as H11Protocol
from uvicorn.protocols.http.httptools_impl import HttpToolsProtocol as HttpToolsProtocol
from uvicorn.protocols.websockets.websockets_impl import (
    WebSocketProtocol as WebSocketProtocol,
)
from uvicorn.protocols.websockets.websockets_sansio_impl import (
    WebSocketsSansIOProtocol as WebSocketsSansIOProtocol,
)
from uvicorn.protocols.websockets.wsproto_impl import WSProtocol as WSProtocol

Protocols: TypeAlias = (
    H11Protocol
    | HttpToolsProtocol
    | WSProtocol
    | WebSocketProtocol
    | WebSocketsSansIOProtocol
)
HANDLED_SIGNALS: Incomplete
logger: Incomplete

class ServerState:
    total_requests: int
    connections: set[Protocols]
    tasks: set[asyncio.Task[None]]
    default_headers: list[tuple[bytes, bytes]]
    def __init__(self) -> None: ...

class Server:
    config: Incomplete
    server_state: Incomplete
    started: bool
    should_exit: bool
    force_exit: bool
    last_notified: float
    def __init__(self, config: Config) -> None: ...
    def run(self, sockets: list[socket.socket] | None = None) -> None: ...
    async def serve(self, sockets: list[socket.socket] | None = None) -> None: ...
    servers: list[asyncio.base_events.Server]
    async def startup(self, sockets: list[socket.socket] | None = None) -> None: ...
    async def main_loop(self) -> None: ...
    async def on_tick(self, counter: int) -> bool: ...
    async def shutdown(self, sockets: list[socket.socket] | None = None) -> None: ...
    @contextlib.contextmanager
    def capture_signals(self) -> Generator[None, None, None]: ...
    def handle_exit(self, sig: int, frame: FrameType | None) -> None: ...
