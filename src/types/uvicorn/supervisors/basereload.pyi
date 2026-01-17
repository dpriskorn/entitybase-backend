from _typeshed import Incomplete
from collections.abc import Callable as Callable, Iterator
from pathlib import Path
from socket import socket
from types import FrameType
from uvicorn._subprocess import get_subprocess as get_subprocess
from uvicorn.config import Config as Config

HANDLED_SIGNALS: Incomplete
logger: Incomplete

class BaseReload:
    config: Incomplete
    target: Incomplete
    sockets: Incomplete
    should_exit: Incomplete
    pid: Incomplete
    is_restarting: bool
    reloader_name: str | None
    def __init__(
        self,
        config: Config,
        target: Callable[[list[socket] | None], None],
        sockets: list[socket],
    ) -> None: ...
    def signal_handler(self, sig: int, frame: FrameType | None) -> None: ...
    def run(self) -> None: ...
    def pause(self) -> None: ...
    def __iter__(self) -> Iterator[list[Path] | None]: ...
    def __next__(self) -> list[Path] | None: ...
    process: Incomplete
    def startup(self) -> None: ...
    def restart(self) -> None: ...
    def shutdown(self) -> None: ...
    def should_restart(self) -> list[Path] | None: ...
