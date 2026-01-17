# type: ignore[misc]
from .api import (
    Request as Request,
    RequestStruct as RequestStruct,
    Response as Response,
)
from .types import (
    Array as Array,
    Int16 as Int16,
    Int32 as Int32,
    Int64 as Int64,
    Int8 as Int8,
    Schema as Schema,
    String as String,
)
from _typeshed import Incomplete
from aiokafka.errors import IncompatibleBrokerVersion as IncompatibleBrokerVersion
from typing import TypeAlias

class OffsetResetStrategy:
    LATEST: int
    EARLIEST: int
    NONE: int

class OffsetResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetResponse_v4(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetResponse_v5(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetResponse_v0
    SCHEMA: Incomplete
    DEFAULTS: Incomplete

class OffsetRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetResponse_v1
    SCHEMA: Incomplete
    DEFAULTS: Incomplete

class OffsetRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetResponse_v2
    SCHEMA: Incomplete
    DEFAULTS: Incomplete

class OffsetRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetResponse_v3
    SCHEMA: Incomplete
    DEFAULTS: Incomplete

class OffsetRequest_v4(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetResponse_v4
    SCHEMA: Incomplete
    DEFAULTS: Incomplete

class OffsetRequest_v5(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetResponse_v5
    SCHEMA: Incomplete
    DEFAULTS: Incomplete

OffsetRequestStruct: TypeAlias = (
    OffsetRequest_v0 | OffsetRequest_v1 | OffsetRequest_v2 | OffsetRequest_v3
)

class OffsetRequest(Request[OffsetRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        replica_id: int,
        isolation_level: int,
        topics: list[tuple[str, list[tuple[int, int]]]],
    ) -> None: ...
    def build(
        self, request_struct_class: type[OffsetRequestStruct]
    ) -> OffsetRequestStruct: ...
