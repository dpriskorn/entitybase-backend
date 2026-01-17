from .api import (
    Request as Request,
    RequestStruct as RequestStruct,
    Response as Response,
)
from .types import (
    Array as Array,
    Boolean as Boolean,
    Int16 as Int16,
    Int32 as Int32,
    Schema as Schema,
    String as String,
)
from _typeshed import Incomplete
from typing import TypeAlias

class MetadataResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class MetadataResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class MetadataResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class MetadataResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class MetadataResponse_v4(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class MetadataResponse_v5(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class MetadataRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = MetadataResponse_v0
    SCHEMA: Incomplete

class MetadataRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = MetadataResponse_v1
    SCHEMA: Incomplete

class MetadataRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = MetadataResponse_v2
    SCHEMA: Incomplete

class MetadataRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = MetadataResponse_v3
    SCHEMA: Incomplete

class MetadataRequest_v4(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = MetadataResponse_v4
    SCHEMA: Incomplete

class MetadataRequest_v5(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = MetadataResponse_v5
    SCHEMA: Incomplete

MetadataRequestStruct: TypeAlias = (
    MetadataRequest_v0
    | MetadataRequest_v1
    | MetadataRequest_v2
    | MetadataRequest_v3
    | MetadataRequest_v4
    | MetadataRequest_v5
)

class MetadataRequest(Request[MetadataRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        topics: list[str] | None = None,
        allow_auto_topic_creation: bool | None = None,
    ) -> None: ...
    def build(
        self, request_struct_class: type[MetadataRequestStruct]
    ) -> MetadataRequestStruct: ...
