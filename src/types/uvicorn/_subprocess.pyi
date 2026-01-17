from _typeshed import Incomplete
from collections.abc import Callable as Callable
from multiprocessing.context import SpawnProcess
from socket import socket
from uvicorn.config import Config as Config

spawn: Incomplete

def get_subprocess(
    config: Config, target: Callable[..., None], sockets: list[socket]
) -> SpawnProcess: ...
def subprocess_started(
    config: Config,
    target: Callable[..., None],
    sockets: list[socket],
    stdin_fileno: int | None,
) -> None: ...
