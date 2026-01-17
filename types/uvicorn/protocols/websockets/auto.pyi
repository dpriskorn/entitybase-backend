import asyncio
from collections.abc import Callable as Callable
from uvicorn.protocols.websockets.websockets_impl import (
    WebSocketProtocol as WebSocketProtocol,
)
from uvicorn.protocols.websockets.wsproto_impl import WSProtocol as WSProtocol

AutoWebSocketsProtocol: Callable[..., asyncio.Protocol] | None
AutoWebSocketsProtocol = WSProtocol
AutoWebSocketsProtocol = WebSocketProtocol
