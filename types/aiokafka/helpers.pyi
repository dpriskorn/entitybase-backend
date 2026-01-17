from _typeshed import Incomplete
from collections.abc import Callable as Callable
from os import PathLike
from ssl import SSLContext
from typing_extensions import Buffer

log: Incomplete

def create_ssl_context(
    *,
    cafile: str | bytes | PathLike[str] | PathLike[bytes] | None = None,
    capath: str | bytes | PathLike[str] | PathLike[bytes] | None = None,
    cadata: str | Buffer | None = None,
    certfile: str | bytes | PathLike[str] | PathLike[bytes] | None = None,
    keyfile: str | bytes | PathLike[str] | PathLike[bytes] | None = None,
    password: Callable[[], str | bytes | bytearray]
    | str
    | bytes
    | bytearray
    | None = None,
) -> SSLContext: ...
