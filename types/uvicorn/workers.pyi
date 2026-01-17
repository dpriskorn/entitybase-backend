from _typeshed import Incomplete
from gunicorn.workers.base import Worker
from typing import Any
from uvicorn._compat import asyncio_run as asyncio_run
from uvicorn.config import Config as Config
from uvicorn.server import Server as Server

class UvicornWorker(Worker):
    CONFIG_KWARGS: dict[str, Any]
    config: Incomplete
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def init_signals(self) -> None: ...
    def run(self) -> None: ...
    async def callback_notify(self) -> None: ...

class UvicornH11Worker(UvicornWorker):
    CONFIG_KWARGS: Incomplete
