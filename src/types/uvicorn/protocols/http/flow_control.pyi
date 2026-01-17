import asyncio
from _typeshed import Incomplete
from uvicorn._types import (
    ASGIReceiveCallable as ASGIReceiveCallable,
    ASGISendCallable as ASGISendCallable,
    Scope as Scope,
)

CLOSE_HEADER: Incomplete
HIGH_WATER_LIMIT: int

class FlowControl:
    read_paused: bool
    write_paused: bool
    def __init__(self, transport: asyncio.Transport) -> None: ...
    async def drain(self) -> None: ...
    def pause_reading(self) -> None: ...
    def resume_reading(self) -> None: ...
    def pause_writing(self) -> None: ...
    def resume_writing(self) -> None: ...

async def service_unavailable(
    scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
) -> None: ...
