from _typeshed import Incomplete
from collections.abc import Callable as Callable, Iterator
from pathlib import Path
from socket import socket
from uvicorn.config import Config as Config
from uvicorn.supervisors.basereload import BaseReload as BaseReload

logger: Incomplete

class StatReload(BaseReload):
    reloader_name: str
    mtimes: dict[Path, float]
    def __init__(
        self,
        config: Config,
        target: Callable[[list[socket] | None], None],
        sockets: list[socket],
    ) -> None: ...
    def should_restart(self) -> list[Path] | None: ...
    def restart(self) -> None: ...
    def iter_py_files(self) -> Iterator[Path]: ...
