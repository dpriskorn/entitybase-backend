# type: ignore[misc]
# type: ignore[misc]
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
    Schema as Schema,
    String as String,
)
from _typeshed import Incomplete
from aiokafka.errors import IncompatibleBrokerVersion as IncompatibleBrokerVersion
from typing import TypeAlias

class ProduceResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v4(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v5(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v6(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v7(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceResponse_v8(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ProduceRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v0
    SCHEMA: Incomplete

class ProduceRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v1
    SCHEMA: Incomplete

class ProduceRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v2
    SCHEMA: Incomplete

class ProduceRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v3
    SCHEMA: Incomplete

class ProduceRequest_v4(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v4
    SCHEMA: Incomplete

class ProduceRequest_v5(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v5
    SCHEMA: Incomplete

class ProduceRequest_v6(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v6
    SCHEMA: Incomplete

class ProduceRequest_v7(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v7
    SCHEMA: Incomplete

class ProduceRequest_v8(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ProduceResponse_v8
    SCHEMA: Incomplete

ProduceRequestStruct: TypeAlias = (
    ProduceRequest_v0
    | ProduceRequest_v1
    | ProduceRequest_v2
    | ProduceRequest_v3
    | ProduceRequest_v4
    | ProduceRequest_v5
    | ProduceRequest_v6
    | ProduceRequest_v7
)

class ProduceRequest(Request[ProduceRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        transactional_id: str | None,
        required_acks: int,
        timeout: int,
        topics: list[tuple[str, list[tuple[int, bytes]]]],
    ) -> None: ...
    @property
    def required_acks(self) -> int: ...
    def build(
        self, request_struct_class: type[ProduceRequestStruct]
    ) -> ProduceRequestStruct: ...
