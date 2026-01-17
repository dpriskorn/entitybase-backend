import ipaddress
from _typeshed import Incomplete
from uvicorn._types import (
    ASGI3Application as ASGI3Application,
    ASGIReceiveCallable as ASGIReceiveCallable,
    ASGISendCallable as ASGISendCallable,
    Scope as Scope,
)

class ProxyHeadersMiddleware:
    app: Incomplete
    trusted_hosts: Incomplete
    def __init__(
        self, app: ASGI3Application, trusted_hosts: list[str] | str = "127.0.0.1"
    ) -> None: ...
    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None: ...

class _TrustedHosts:
    always_trust: bool
    trusted_literals: set[str]
    trusted_hosts: set[ipaddress.IPv4Address | ipaddress.IPv6Address]
    trusted_networks: set[ipaddress.IPv4Network | ipaddress.IPv6Network]
    def __init__(self, trusted_hosts: list[str] | str) -> None: ...
    def __contains__(self, host: str | None) -> bool: ...
    def get_trusted_client_host(self, x_forwarded_for: str) -> str: ...
