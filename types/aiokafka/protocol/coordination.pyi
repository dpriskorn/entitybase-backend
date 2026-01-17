# type: ignore[misc]
from .api import (
    Request as Request,
    RequestStruct as RequestStruct,
    Response as Response,
)
from .types import (
    Int16 as Int16,
    Int32 as Int32,
    Int8 as Int8,
    Schema as Schema,
    String as String,
)
from _typeshed import Incomplete
from aiokafka.errors import IncompatibleBrokerVersion as IncompatibleBrokerVersion
from typing import TypeAlias

class FindCoordinatorResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FindCoordinatorResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class FindCoordinatorRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FindCoordinatorResponse_v0
    SCHEMA: Incomplete

class FindCoordinatorRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = FindCoordinatorResponse_v1
    SCHEMA: Incomplete

FindCoordinatorRequestStruct: TypeAlias = (
    FindCoordinatorRequest_v0 | FindCoordinatorRequest_v1
)

class FindCoordinatorRequest(Request[FindCoordinatorRequestStruct]):
    API_KEY: int
    def __init__(self, coordinator_key: str, coordinator_type: int) -> None: ...
    def build(
        self, request_struct_class: type[FindCoordinatorRequestStruct]
    ) -> FindCoordinatorRequestStruct: ...
