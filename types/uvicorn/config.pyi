import asyncio
import os
import socket
import ssl
from _typeshed import Incomplete
from collections.abc import Awaitable, Callable as Callable
from configparser import RawConfigParser
from pathlib import Path
from typing import Any, IO, Literal
from uvicorn._compat import iscoroutinefunction as iscoroutinefunction
from uvicorn._types import ASGIApplication as ASGIApplication
from uvicorn.importer import (
    ImportFromStringError as ImportFromStringError,
    import_from_string as import_from_string,
)
from uvicorn.logging import TRACE_LOG_LEVEL as TRACE_LOG_LEVEL
from uvicorn.middleware.asgi2 import ASGI2Middleware as ASGI2Middleware
from uvicorn.middleware.message_logger import (
    MessageLoggerMiddleware as MessageLoggerMiddleware,
)
from uvicorn.middleware.proxy_headers import (
    ProxyHeadersMiddleware as ProxyHeadersMiddleware,
)
from uvicorn.middleware.wsgi import WSGIMiddleware as WSGIMiddleware

HTTPProtocolType: Incomplete
WSProtocolType: Incomplete
LifespanType: Incomplete
LoopFactoryType: Incomplete
InterfaceType: Incomplete
LOG_LEVELS: dict[str, int]
HTTP_PROTOCOLS: dict[str, str]
WS_PROTOCOLS: dict[str, str | None]
LIFESPAN: dict[str, str]
LOOP_FACTORIES: dict[str, str | None]
INTERFACES: list[InterfaceType]
SSL_PROTOCOL_VERSION: int
LOGGING_CONFIG: dict[str, Any]
logger: Incomplete

def create_ssl_context(
    certfile: str | os.PathLike[str],
    keyfile: str | os.PathLike[str] | None,
    password: str | None,
    ssl_version: int,
    cert_reqs: int,
    ca_certs: str | os.PathLike[str] | None,
    ciphers: str | None,
) -> ssl.SSLContext: ...
def is_dir(path: Path) -> bool: ...
def resolve_reload_patterns(
    patterns_list: list[str], directories_list: list[str]
) -> tuple[list[str], list[Path]]: ...

class Config:
    app: Incomplete
    host: Incomplete
    port: Incomplete
    uds: Incomplete
    fd: Incomplete
    loop: Incomplete
    http: Incomplete
    ws: Incomplete
    ws_max_size: Incomplete
    ws_max_queue: Incomplete
    ws_ping_interval: Incomplete
    ws_ping_timeout: Incomplete
    ws_per_message_deflate: Incomplete
    lifespan: Incomplete
    log_config: Incomplete
    log_level: Incomplete
    access_log: Incomplete
    use_colors: Incomplete
    interface: Incomplete
    reload: Incomplete
    reload_delay: Incomplete
    workers: Incomplete
    proxy_headers: Incomplete
    server_header: Incomplete
    date_header: Incomplete
    root_path: Incomplete
    limit_concurrency: Incomplete
    limit_max_requests: Incomplete
    backlog: Incomplete
    timeout_keep_alive: Incomplete
    timeout_notify: Incomplete
    timeout_graceful_shutdown: Incomplete
    timeout_worker_healthcheck: Incomplete
    callback_notify: Incomplete
    ssl_keyfile: Incomplete
    ssl_certfile: Incomplete
    ssl_keyfile_password: Incomplete
    ssl_version: Incomplete
    ssl_cert_reqs: Incomplete
    ssl_ca_certs: Incomplete
    ssl_ciphers: Incomplete
    headers: list[tuple[str, str]]
    encoded_headers: list[tuple[bytes, bytes]]
    factory: Incomplete
    h11_max_incomplete_event_size: Incomplete
    loaded: bool
    reload_dirs: list[Path]
    reload_dirs_excludes: list[Path]
    reload_includes: list[str]
    reload_excludes: list[str]
    forwarded_allow_ips: list[str] | str
    def __init__(
        self,
        app: ASGIApplication | Callable[..., Any] | str,
        host: str = "127.0.0.1",
        port: int = 8000,
        uds: str | None = None,
        fd: int | None = None,
        loop: LoopFactoryType | str = "auto",
        http: type[asyncio.Protocol] | HTTPProtocolType | str = "auto",
        ws: type[asyncio.Protocol] | WSProtocolType | str = "auto",
        ws_max_size: int = ...,
        ws_max_queue: int = 32,
        ws_ping_interval: float | None = 20.0,
        ws_ping_timeout: float | None = 20.0,
        ws_per_message_deflate: bool = True,
        lifespan: LifespanType = "auto",
        env_file: str | os.PathLike[str] | None = None,
        log_config: dict[str, Any] | str | RawConfigParser | IO[Any] | None = ...,
        log_level: str | int | None = None,
        access_log: bool = True,
        use_colors: bool | None = None,
        interface: InterfaceType = "auto",
        reload: bool = False,
        reload_dirs: list[str] | str | None = None,
        reload_delay: float = 0.25,
        reload_includes: list[str] | str | None = None,
        reload_excludes: list[str] | str | None = None,
        workers: int | None = None,
        proxy_headers: bool = True,
        server_header: bool = True,
        date_header: bool = True,
        forwarded_allow_ips: list[str] | str | None = None,
        root_path: str = "",
        limit_concurrency: int | None = None,
        limit_max_requests: int | None = None,
        backlog: int = 2048,
        timeout_keep_alive: int = 5,
        timeout_notify: int = 30,
        timeout_graceful_shutdown: int | None = None,
        timeout_worker_healthcheck: int = 5,
        callback_notify: Callable[..., Awaitable[None]] | None = None,
        ssl_keyfile: str | os.PathLike[str] | None = None,
        ssl_certfile: str | os.PathLike[str] | None = None,
        ssl_keyfile_password: str | None = None,
        ssl_version: int = ...,
        ssl_cert_reqs: int = ...,
        ssl_ca_certs: str | os.PathLike[str] | None = None,
        ssl_ciphers: str = "TLSv1",
        headers: list[tuple[str, str]] | None = None,
        factory: bool = False,
        h11_max_incomplete_event_size: int | None = None,
    ) -> None: ...
    @property
    def asgi_version(self) -> Literal["2.0", "3.0"]: ...
    @property
    def is_ssl(self) -> bool: ...
    @property
    def use_subprocess(self) -> bool: ...
    def configure_logging(self) -> None: ...
    ssl: ssl.SSLContext | None
    http_protocol_class: type[asyncio.Protocol]
    ws_protocol_class: type[asyncio.Protocol] | None
    lifespan_class: Incomplete
    loaded_app: Incomplete
    def load(self) -> None: ...
    def setup_event_loop(self) -> None: ...
    def get_loop_factory(self) -> Callable[[], asyncio.AbstractEventLoop] | None: ...
    def bind_socket(self) -> socket.socket: ...
    @property
    def should_reload(self) -> bool: ...
