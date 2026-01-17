from .api import (
    Request as Request,
    RequestStruct as RequestStruct,
    Response as Response,
)
from .types import (
    Array as Array,
    Boolean as Boolean,
    Bytes as Bytes,
    CompactArray as CompactArray,
    CompactString as CompactString,
    Float64 as Float64,
    Int16 as Int16,
    Int32 as Int32,
    Int64 as Int64,
    Int8 as Int8,
    Schema as Schema,
    String as String,
    TaggedFields as TaggedFields,
)
from _typeshed import Incomplete
from aiokafka.errors import IncompatibleBrokerVersion as IncompatibleBrokerVersion
from collections.abc import Iterable
from typing import Any, TypeAlias

class ApiVersionResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ApiVersionResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ApiVersionResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ApiVersionRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ApiVersionResponse_v0
    SCHEMA: Incomplete

class ApiVersionRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ApiVersionResponse_v1
    SCHEMA: Incomplete

class ApiVersionRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ApiVersionResponse_v1
    SCHEMA: Incomplete

ApiVersionRequestStruct: TypeAlias = (
    ApiVersionRequest_v0 | ApiVersionRequest_v1 | ApiVersionRequest_v2
)

class ApiVersionRequest(Request[ApiVersionRequestStruct]):
    API_KEY: int
    ALLOW_UNKNOWN_API_VERSION: bool
    def build(
        self, request_struct_class: type[ApiVersionRequestStruct]
    ) -> ApiVersionRequestStruct: ...

class CreateTopicsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreateTopicsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreateTopicsResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreateTopicsResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreateTopicsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = CreateTopicsResponse_v0
    SCHEMA: Incomplete

class CreateTopicsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = CreateTopicsResponse_v1
    SCHEMA: Incomplete

class CreateTopicsRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = CreateTopicsResponse_v2
    SCHEMA: Incomplete

class CreateTopicsRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = CreateTopicsResponse_v3
    SCHEMA: Incomplete

CreateTopicsRequestStruct: TypeAlias = (
    CreateTopicsRequest_v0
    | CreateTopicsRequest_v1
    | CreateTopicsRequest_v2
    | CreateTopicsRequest_v3
)

class CreateTopicsRequest(Request[CreateTopicsRequestStruct]):
    API_KEY: int
    create_topic_requests: Incomplete
    timeout: Incomplete
    validate_only: Incomplete
    def __init__(
        self,
        create_topic_requests: list[tuple[Any]],
        timeout: int | None,
        validate_only: bool,
    ) -> None: ...
    def build(
        self, request_struct_class: type[CreateTopicsRequestStruct]
    ) -> CreateTopicsRequestStruct: ...

class DeleteTopicsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteTopicsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteTopicsResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteTopicsResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteTopicsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteTopicsResponse_v0
    SCHEMA: Incomplete

class DeleteTopicsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteTopicsResponse_v1
    SCHEMA: Incomplete

class DeleteTopicsRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteTopicsResponse_v2
    SCHEMA: Incomplete

class DeleteTopicsRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteTopicsResponse_v3
    SCHEMA: Incomplete

DeleteTopicsRequestStruct: TypeAlias = (
    DeleteTopicsRequest_v0
    | DeleteTopicsRequest_v1
    | DeleteTopicsRequest_v2
    | DeleteTopicsRequest_v3
)

class DeleteTopicsRequest(Request[DeleteTopicsRequestStruct]):
    API_KEY: int
    def __init__(self, topics: list[str], timeout: int) -> None: ...
    def build(
        self, request_struct_class: type[DeleteTopicsRequestStruct]
    ) -> DeleteTopicsRequestStruct: ...

class ListGroupsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ListGroupsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ListGroupsResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ListGroupsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ListGroupsResponse_v0
    SCHEMA: Incomplete

class ListGroupsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ListGroupsResponse_v1
    SCHEMA: Incomplete

class ListGroupsRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ListGroupsResponse_v2
    SCHEMA: Incomplete

ListGroupsRequestStruct: TypeAlias = (
    ListGroupsRequest_v0 | ListGroupsRequest_v1 | ListGroupsRequest_v2
)

class ListGroupsRequest(Request[ListGroupsRequestStruct]):
    API_KEY: int
    def build(
        self, request_struct_class: type[ListGroupsRequestStruct]
    ) -> ListGroupsRequestStruct: ...

class DescribeGroupsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeGroupsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeGroupsResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeGroupsResponse_v3(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeGroupsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeGroupsResponse_v0
    SCHEMA: Incomplete

class DescribeGroupsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeGroupsResponse_v1
    SCHEMA: Incomplete

class DescribeGroupsRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeGroupsResponse_v2
    SCHEMA: Incomplete

class DescribeGroupsRequest_v3(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeGroupsResponse_v2
    SCHEMA: Incomplete

DescribeGroupsRequestStruct: TypeAlias = (
    DescribeGroupsRequest_v0
    | DescribeGroupsRequest_v1
    | DescribeGroupsRequest_v2
    | DescribeGroupsRequest_v3
)

class DescribeGroupsRequest(Request[DescribeGroupsRequestStruct]):
    API_KEY: int
    def __init__(
        self, groups: list[str], include_authorized_operations: bool = False
    ) -> None: ...
    def build(
        self, request_struct_class: type[DescribeGroupsRequestStruct]
    ) -> DescribeGroupsRequestStruct: ...

class SaslHandShakeResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class SaslHandShakeResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class SaslHandShakeRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = SaslHandShakeResponse_v0
    SCHEMA: Incomplete

class SaslHandShakeRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = SaslHandShakeResponse_v1
    SCHEMA: Incomplete

SaslHandShakeRequestStruct: TypeAlias = (
    SaslHandShakeRequest_v0 | SaslHandShakeRequest_v1
)

class SaslHandShakeRequest(Request[SaslHandShakeRequestStruct]):
    API_KEY: int
    def __init__(self, mechanism: str) -> None: ...
    def build(
        self, request_struct_class: type[SaslHandShakeRequestStruct]
    ) -> SaslHandShakeRequestStruct: ...

class DescribeAclsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeAclsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeAclsResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeAclsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeAclsResponse_v0
    SCHEMA: Incomplete

class DescribeAclsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeAclsResponse_v1
    SCHEMA: Incomplete

class DescribeAclsRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeAclsResponse_v2
    SCHEMA: Incomplete

DescribeAclsRequestStruct: TypeAlias = DescribeAclsRequest_v0 | DescribeAclsRequest_v1

class DescribeAclsRequest(Request[DescribeAclsRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        resource_type: int,
        resource_name: str,
        resource_pattern_type_filter: int,
        principal: str,
        host: str,
        operation: int,
        permission_type: int,
    ) -> None: ...
    def build(
        self, request_struct_class: type[DescribeAclsRequestStruct]
    ) -> DescribeAclsRequestStruct: ...

class CreateAclsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreateAclsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreateAclsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = CreateAclsResponse_v0
    SCHEMA: Incomplete

class CreateAclsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = CreateAclsResponse_v1
    SCHEMA: Incomplete

CreateAclsRequestStruct: TypeAlias = CreateAclsRequest_v0 | CreateAclsRequest_v1

class CreateAclsRequest(Request[CreateAclsRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        resource_type: int,
        resource_name: str,
        resource_pattern_type_filter: int,
        principal: str,
        host: str,
        operation: int,
        permission_type: int,
    ) -> None: ...
    def build(
        self, request_struct_class: type[CreateAclsRequestStruct]
    ) -> CreateAclsRequestStruct: ...

class DeleteAclsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteAclsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteAclsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteAclsResponse_v0
    SCHEMA: Incomplete

class DeleteAclsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteAclsResponse_v1
    SCHEMA: Incomplete

DeleteAclsRequestStruct: TypeAlias = DeleteAclsRequest_v0 | DeleteAclsRequest_v1

class DeleteAclsRequest(Request[DeleteAclsRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        resource_type: int,
        resource_name: str,
        resource_pattern_type_filter: int,
        principal: str,
        host: str,
        operation: int,
        permission_type: int,
    ) -> None: ...
    def build(
        self, request_struct_class: type[DeleteAclsRequestStruct]
    ) -> DeleteAclsRequestStruct: ...

class AlterConfigsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class AlterConfigsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class AlterConfigsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = AlterConfigsResponse_v0
    SCHEMA: Incomplete

class AlterConfigsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = AlterConfigsResponse_v1
    SCHEMA: Incomplete

AlterConfigsRequestStruct: TypeAlias = AlterConfigsRequest_v0 | AlterConfigsRequest_v1

class AlterConfigsRequest(Request[AlterConfigsRequestStruct]):
    API_KEY: int
    def __init__(
        self, resources: dict[int, Any] | list[Any], validate_only: bool = False
    ) -> None: ...
    def build(
        self, request_struct_class: type[AlterConfigsRequestStruct]
    ) -> AlterConfigsRequestStruct: ...

class DescribeConfigsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeConfigsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeConfigsResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeConfigsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeConfigsResponse_v0
    SCHEMA: Incomplete

class DescribeConfigsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeConfigsResponse_v1
    SCHEMA: Incomplete

class DescribeConfigsRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeConfigsResponse_v2
    SCHEMA: Incomplete

DescribeConfigsRequestStruct: TypeAlias = (
    DescribeConfigsRequest_v0 | DescribeConfigsRequest_v1 | DescribeConfigsRequest_v2
)

class DescribeConfigsRequest(Request[DescribeConfigsRequestStruct]):
    API_KEY: int
    def __init__(
        self, resources: dict[int, Any] | list[Any], include_synonyms: bool = False
    ) -> None: ...
    def build(
        self, request_struct_class: type[DescribeConfigsRequestStruct]
    ) -> DescribeConfigsRequestStruct: ...

class SaslAuthenticateResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class SaslAuthenticateResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class SaslAuthenticateRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = SaslAuthenticateResponse_v0
    SCHEMA: Incomplete

class SaslAuthenticateRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = SaslAuthenticateResponse_v1
    SCHEMA: Incomplete

SaslAuthenticateRequestStruct: TypeAlias = (
    SaslAuthenticateRequest_v0 | SaslAuthenticateRequest_v1
)

class SaslAuthenticateRequest(Request[SaslAuthenticateRequestStruct]):
    API_KEY: int
    def __init__(self, payload: Any) -> None: ...
    def build(
        self, request_struct_class: type[SaslAuthenticateRequestStruct]
    ) -> SaslAuthenticateRequestStruct: ...

class CreatePartitionsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreatePartitionsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class CreatePartitionsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = CreatePartitionsResponse_v0
    SCHEMA: Incomplete

class CreatePartitionsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete
    RESPONSE_TYPE = CreatePartitionsResponse_v1

CreatePartitionsRequestStruct: TypeAlias = (
    CreatePartitionsRequest_v0 | CreatePartitionsRequest_v1
)

class CreatePartitionsRequest(Request[CreatePartitionsRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        topic_partitions: list[tuple[str, tuple[int, list[int]]]],
        timeout: int,
        validate_only: bool,
    ) -> None: ...
    def build(
        self, request_struct_class: type[CreatePartitionsRequestStruct]
    ) -> CreatePartitionsRequestStruct: ...

class DeleteGroupsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteGroupsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteGroupsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteGroupsResponse_v0
    SCHEMA: Incomplete

class DeleteGroupsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteGroupsResponse_v1
    SCHEMA: Incomplete

DeleteGroupsRequestStruct: TypeAlias = DeleteGroupsRequest_v0 | DeleteGroupsRequest_v1

class DeleteGroupsRequest(Request[DeleteGroupsRequestStruct]):
    API_KEY: int
    def __init__(self, group_names: list[str]) -> None: ...
    def build(
        self, request_struct_class: type[DeleteGroupsRequestStruct]
    ) -> DeleteGroupsRequestStruct: ...

class DescribeClientQuotasResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DescribeClientQuotasRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DescribeClientQuotasResponse_v0
    SCHEMA: Incomplete

DescribeClientQuotasRequestStruct: TypeAlias = DescribeClientQuotasRequest_v0

class DescribeClientQuotasRequest(Request[DescribeClientQuotasRequestStruct]):
    API_KEY: int
    def __init__(
        self, components: list[tuple[str, int, str]], strict: bool
    ) -> None: ...
    def build(
        self, request_struct_class: type[DescribeClientQuotasRequestStruct]
    ) -> DescribeClientQuotasRequestStruct: ...

class AlterPartitionReassignmentsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class AlterPartitionReassignmentsRequest_v0(RequestStruct):
    FLEXIBLE_VERSION: bool
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = AlterPartitionReassignmentsResponse_v0
    SCHEMA: Incomplete

AlterPartitionReassignmentsRequestStruct: TypeAlias = (
    AlterPartitionReassignmentsRequest_v0
)

class AlterPartitionReassignmentsRequest(
    Request[AlterPartitionReassignmentsRequestStruct]
):
    API_KEY: int
    def __init__(
        self,
        timeout_ms: int,
        topics: list[tuple[str, tuple[int, list[int], TaggedFields], TaggedFields]],
        tags: TaggedFields,
    ) -> None: ...
    def build(
        self, request_struct_class: type[AlterPartitionReassignmentsRequestStruct]
    ) -> AlterPartitionReassignmentsRequestStruct: ...

class ListPartitionReassignmentsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class ListPartitionReassignmentsRequest_v0(RequestStruct):
    FLEXIBLE_VERSION: bool
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = ListPartitionReassignmentsResponse_v0
    SCHEMA: Incomplete

ListPartitionReassignmentsRequestStruct: TypeAlias = (
    ListPartitionReassignmentsRequest_v0
)

class ListPartitionReassignmentsRequest(
    Request[ListPartitionReassignmentsRequestStruct]
):
    API_KEY: int
    def __init__(
        self,
        timeout_ms: int,
        topics: list[tuple[str, tuple[int, list[int], TaggedFields], TaggedFields]],
        tags: TaggedFields,
    ) -> None: ...
    def build(
        self, request_struct_class: type[ListPartitionReassignmentsRequestStruct]
    ) -> ListPartitionReassignmentsRequestStruct: ...

class DeleteRecordsResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteRecordsResponse_v1(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteRecordsResponse_v2(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class DeleteRecordsRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteRecordsResponse_v0
    SCHEMA: Incomplete

class DeleteRecordsRequest_v1(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = DeleteRecordsResponse_v1
    SCHEMA: Incomplete

class DeleteRecordsRequest_v2(RequestStruct):
    API_KEY: int
    API_VERSION: int
    FLEXIBLE_VERSION: bool
    RESPONSE_TYPE = DeleteRecordsResponse_v2
    SCHEMA: Incomplete

DeleteRecordsRequestStruct: TypeAlias = (
    DeleteRecordsRequest_v0 | DeleteRecordsRequest_v1 | DeleteRecordsRequest_v2
)

class DeleteRecordsRequest(Request[DeleteRecordsRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        topics: Iterable[tuple[str, Iterable[tuple[int, int]]]],
        timeout_ms: int,
        tags: dict[int, bytes] | None = None,
    ) -> None: ...
    def build(
        self, request_struct_class: type[DeleteRecordsRequestStruct]
    ) -> DeleteRecordsRequestStruct: ...
