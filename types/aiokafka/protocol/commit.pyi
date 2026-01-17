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
    Schema as Schema,
    String as String,
)
from _typeshed import Incomplete
from aiokafka.errors import IncompatibleBrokerVersion as IncompatibleBrokerVersion
from typing import TypeAlias

class OffsetCommitResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetCommitResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetCommitResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetCommitResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetCommitRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetCommitResponse_v0
    SCHEMA: Incomplete

class OffsetCommitRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetCommitResponse_v1
    SCHEMA: Incomplete

class OffsetCommitRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetCommitResponse_v2
    SCHEMA: Incomplete

class OffsetCommitRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetCommitResponse_v3
    SCHEMA: Incomplete

OffsetCommitRequestStruct: TypeAlias = OffsetCommitRequest_v2 | OffsetCommitRequest_v3

class OffsetCommitRequest(Request[OffsetCommitRequestStruct]):
    API_KEY: int
    DEFAULT_GENERATION_ID: int
    DEFAULT_RETENTION_TIME: int
    def __init__(
        self,
        consumer_group: str,
        consumer_group_generation_id: int,
        consumer_id: str,
        retention_time: int,
        topics: list[tuple[str, list[tuple[int, int, str]]]],
    ) -> None: ...
    def build(
        self, request_struct_class: type[OffsetCommitRequestStruct]
    ) -> OffsetCommitRequestStruct: ...

class OffsetFetchResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetFetchResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetFetchResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetFetchResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class OffsetFetchRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetFetchResponse_v0
    SCHEMA: Incomplete

class OffsetFetchRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetFetchResponse_v1
    SCHEMA: Incomplete

class OffsetFetchRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetFetchResponse_v2
    SCHEMA: Incomplete

class OffsetFetchRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = OffsetFetchResponse_v3
    SCHEMA: Incomplete

OffsetFetchRequestStruct: TypeAlias = (
    OffsetFetchRequest_v1 | OffsetFetchRequest_v2 | OffsetFetchRequest_v3
)

class OffsetFetchRequest(Request[OffsetFetchRequestStruct]):
    API_KEY: int
    def __init__(
        self, consumer_group: str, partitions: list[tuple[str, list[int]]] | None
    ) -> None: ...
    def build(
        self, request_struct_class: type[OffsetFetchRequestStruct]
    ) -> OffsetFetchRequestStruct: ...
