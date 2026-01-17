from _typeshed import Incomplete
from asyncio import Queue
from typing import Any
from uvicorn import Config as Config
from uvicorn._types import (
    LifespanScope as LifespanScope,
    LifespanShutdownCompleteEvent as LifespanShutdownCompleteEvent,
    LifespanShutdownEvent as LifespanShutdownEvent,
    LifespanShutdownFailedEvent as LifespanShutdownFailedEvent,
    LifespanStartupCompleteEvent as LifespanStartupCompleteEvent,
    LifespanStartupEvent as LifespanStartupEvent,
    LifespanStartupFailedEvent as LifespanStartupFailedEvent,
)

LifespanReceiveMessage = LifespanStartupEvent | LifespanShutdownEvent
LifespanSendMessage = (
    LifespanStartupFailedEvent
    | LifespanShutdownFailedEvent
    | LifespanStartupCompleteEvent
    | LifespanShutdownCompleteEvent
)
STATE_TRANSITION_ERROR: str

class LifespanOn:
    config: Incomplete
    logger: Incomplete
    startup_event: Incomplete
    shutdown_event: Incomplete
    receive_queue: Queue[LifespanReceiveMessage]
    error_occured: bool
    startup_failed: bool
    shutdown_failed: bool
    should_exit: bool
    state: dict[str, Any]
    def __init__(self, config: Config) -> None: ...
    async def startup(self) -> None: ...
    async def shutdown(self) -> None: ...
    asgi: Incomplete
    async def main(self) -> None: ...
    async def send(self, message: LifespanSendMessage) -> None: ...
    async def receive(self) -> LifespanReceiveMessage: ...
