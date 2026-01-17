from _typeshed import Incomplete
from collections.abc import Callable as Callable
from pathlib import Path
from socket import socket
from uvicorn.config import Config as Config
from uvicorn.supervisors.basereload import BaseReload as BaseReload

class FileFilter:
    includes: Incomplete
    excludes: Incomplete
    exclude_dirs: Incomplete
    def __init__(self, config: Config) -> None: ...
    def __call__(self, path: Path) -> bool: ...

class WatchFilesReload(BaseReload):
    reloader_name: str
    reload_dirs: Incomplete
    watch_filter: Incomplete
    watcher: Incomplete
    def __init__(
        self,
        config: Config,
        target: Callable[[list[socket] | None], None],
        sockets: list[socket],
    ) -> None: ...
    def should_restart(self) -> list[Path] | None: ...
