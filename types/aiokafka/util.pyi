import asyncio
from _typeshed import Incomplete
from asyncio import AbstractEventLoop
from collections.abc import Coroutine
from typing import Any, TypeVar

__all__ = [
    "INTEGER_MAX_VALUE",
    "INTEGER_MIN_VALUE",
    "NO_EXTENSIONS",
    "create_future",
    "create_task",
]

T = TypeVar("T")

def create_task(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]: ...
def create_future(loop: AbstractEventLoop | None = None) -> asyncio.Future[T]: ...

NO_EXTENSIONS: Incomplete
INTEGER_MAX_VALUE: Incomplete
INTEGER_MIN_VALUE: Incomplete
