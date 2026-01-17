from .api import (
    Request as Request,
    RequestStruct as RequestStruct,
    Response as Response,
)
from .types import (
    Array as Array,
    Bytes as Bytes,
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

class FetchResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete
    topics: list[tuple[str, list[tuple[int, int, int, bytes]]]] | None

class FetchResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v4(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v5(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v6(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v7(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v8(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v9(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v10(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchResponse_v11(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FetchRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v0
    SCHEMA: Incomplete
    min_bytes: int | None

class FetchRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v1
    SCHEMA: Incomplete

class FetchRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v2
    SCHEMA: Incomplete

class FetchRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v3
    SCHEMA: Incomplete

class FetchRequest_v4(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v4
    SCHEMA: Incomplete

class FetchRequest_v5(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v5
    SCHEMA: Incomplete

class FetchRequest_v6(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v6
    SCHEMA: Incomplete

class FetchRequest_v7(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v7
    SCHEMA: Incomplete

class FetchRequest_v8(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v8
    SCHEMA: Incomplete

class FetchRequest_v9(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v9
    SCHEMA: Incomplete

class FetchRequest_v10(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v10
    SCHEMA: Incomplete

class FetchRequest_v11(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FetchResponse_v11
    SCHEMA: Incomplete

FetchRequestStruct: TypeAlias = (
    FetchRequest_v1 | FetchRequest_v2 | FetchRequest_v3 | FetchRequest_v4
)

class FetchRequest(Request[FetchRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        max_wait_time: int,
        min_bytes: int,
        max_bytes: int,
        isolation_level: int,
        topics: list[tuple[str, list[tuple[int, int, int]]]],
    ) -> None: ...
    @property
    def topics(self) -> list[tuple[str, list[tuple[int, int, int]]]]: ...
    def build(
        self, request_struct_class: type[FetchRequestStruct]
    ) -> FetchRequestStruct: ...
