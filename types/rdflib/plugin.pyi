from _typeshed import Incomplete
from importlib.metadata import EntryPoint
from rdflib.exceptions import Error
from typing import Any, Generic, Iterator, TypeVar, overload

__all__ = [
    "register",
    "get",
    "plugins",
    "PluginException",
    "Plugin",
    "PluginT",
    "PKGPlugin",
]

class PluginException(Error): ...

PluginT = TypeVar("PluginT")

class Plugin(Generic[PluginT]):
    name: Incomplete
    kind: Incomplete
    module_path: Incomplete
    class_name: Incomplete
    def __init__(
        self, name: str, kind: type[PluginT], module_path: str, class_name: str
    ) -> None: ...
    def getClass(self) -> type[PluginT]: ...

class PKGPlugin(Plugin[PluginT]):
    name: Incomplete
    kind: Incomplete
    ep: Incomplete
    def __init__(self, name: str, kind: type[PluginT], ep: EntryPoint) -> None: ...
    def getClass(self) -> type[PluginT]: ...

def register(name: str, kind: type[Any], module_path: str, class_name: str) -> None: ...
def get(name: str, kind: type[PluginT]) -> type[PluginT]: ...
@overload
def plugins(
    name: str | None = ..., kind: type[PluginT] = ...
) -> Iterator[Plugin[PluginT]]: ...
@overload
def plugins(name: str | None = ..., kind: None = ...) -> Iterator[Plugin]: ...
