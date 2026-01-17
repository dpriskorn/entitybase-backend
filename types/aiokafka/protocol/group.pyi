from .api import (
    Request as Request,
    RequestStruct as RequestStruct,
    Response as Response,
)
from .struct import Struct as Struct
from .types import (
    Array as Array,
    Bytes as Bytes,
    Int16 as Int16,
    Int32 as Int32,
    Schema as Schema,
    String as String,
)
from _typeshed import Incomplete
from typing import TypeAlias

class JoinGroupResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class JoinGroupResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class JoinGroupResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class JoinGroupResponse_v5(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class JoinGroupRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = JoinGroupResponse_v0
    SCHEMA: Incomplete

class JoinGroupRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = JoinGroupResponse_v1
    SCHEMA: Incomplete

class JoinGroupRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = JoinGroupResponse_v2
    SCHEMA: Incomplete

class JoinGroupRequest_v5(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = JoinGroupResponse_v5
    SCHEMA: Incomplete

JoinGroupRequestStruct: TypeAlias = (
    JoinGroupRequest_v0
    | JoinGroupRequest_v1
    | JoinGroupRequest_v2
    | JoinGroupRequest_v5
)

class JoinGroupRequest(Request[JoinGroupRequestStruct]):
    API_KEY: int
    UNKNOWN_MEMBER_ID: str
    def __init__(
        self,
        group: str,
        session_timeout: int,
        rebalance_timeout: int,
        member_id: str,
        group_instance_id: str,
        protocol_type: str,
        group_protocols: list[tuple[str, bytes]],
    ) -> None: ...
    def build(
        self, request_struct_class: type[JoinGroupRequestStruct]
    ) -> JoinGroupRequestStruct: ...

class ProtocolMetadata(Struct):
    SCHEMA: Incomplete

class SyncGroupResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class SyncGroupResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class SyncGroupResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class SyncGroupRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = SyncGroupResponse_v0
    SCHEMA: Incomplete

class SyncGroupRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = SyncGroupResponse_v1
    SCHEMA: Incomplete

class SyncGroupRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = SyncGroupResponse_v3
    SCHEMA: Incomplete

SyncGroupRequestStruct: TypeAlias = (
    SyncGroupRequest_v0 | SyncGroupRequest_v1 | SyncGroupRequest_v3
)

class SyncGroupRequest(Request[SyncGroupRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        group: str,
        generation_id: int,
        member_id: str,
        group_instance_id: str,
        group_assignment: list[tuple[str, bytes]],
    ) -> None: ...
    def build(
        self, request_struct_class: type[SyncGroupRequestStruct]
    ) -> SyncGroupRequestStruct: ...

class MemberAssignment(Struct):
    SCHEMA: Incomplete

class HeartbeatResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class HeartbeatResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class HeartbeatRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = HeartbeatResponse_v0
    SCHEMA: Incomplete

class HeartbeatRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = HeartbeatResponse_v1
    SCHEMA: Incomplete

HeartbeatRequestStruct: TypeAlias = HeartbeatRequest_v0 | HeartbeatRequest_v1

class HeartbeatRequest(Request[HeartbeatRequestStruct]):
    API_KEY: int
    def __init__(self, group: str, generation_id: int, member_id: str) -> None: ...
    def build(
        self, request_struct_class: type[HeartbeatRequestStruct]
    ) -> HeartbeatRequestStruct: ...

class LeaveGroupResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class LeaveGroupResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class LeaveGroupRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = LeaveGroupResponse_v0
    SCHEMA: Incomplete

class LeaveGroupRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = LeaveGroupResponse_v1
    SCHEMA: Incomplete

LeaveGroupRequestStruct: TypeAlias = LeaveGroupRequest_v0 | LeaveGroupRequest_v1

class LeaveGroupRequest(Request[LeaveGroupRequestStruct]):
    API_KEY: int
    def __init__(self, group: str, member_id: str) -> None: ...
    def build(
        self, request_struct_class: type[LeaveGroupRequestStruct]
    ) -> LeaveGroupRequestStruct: ...
