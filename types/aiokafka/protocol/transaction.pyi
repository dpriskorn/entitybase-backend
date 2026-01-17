# type: ignore[misc]
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
    Int64 as Int64,
    Schema as Schema,
    String as String,
)
from _typeshed import Incomplete
from typing import TypeAlias

class InitProducerIdResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class InitProducerIdRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = InitProducerIdResponse_v0
    SCHEMA: Incomplete

InitProducerIdRequestStruct: TypeAlias = InitProducerIdRequest_v0

class InitProducerIdRequest(Request[InitProducerIdRequestStruct]):
    API_KEY: int
    CLASSES: Incomplete
    def __init__(self, transactional_id: str, transaction_timeout_ms: int) -> None: ...
    def build(
        self, request_struct_class: type[InitProducerIdRequestStruct]
    ) -> InitProducerIdRequestStruct: ...

class AddPartitionsToTxnResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class AddPartitionsToTxnRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = AddPartitionsToTxnResponse_v0
    SCHEMA: Incomplete

AddPartitionsToTxnRequestStruct: TypeAlias = AddPartitionsToTxnRequest_v0

class AddPartitionsToTxnRequest(Request[AddPartitionsToTxnRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        transactional_id: str,
        producer_id: int,
        producer_epoch: int,
        topics: list[tuple[str, list[int]]],
    ) -> None: ...
    def build(
        self, request_struct_class: type[AddPartitionsToTxnRequestStruct]
    ) -> AddPartitionsToTxnRequestStruct: ...

class AddOffsetsToTxnResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class AddOffsetsToTxnRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = AddOffsetsToTxnResponse_v0
    SCHEMA: Incomplete

AddOffsetsToTxnRequestStruct: TypeAlias = AddOffsetsToTxnRequest_v0

class AddOffsetsToTxnRequest(Request[AddOffsetsToTxnRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        transactional_id: str,
        producer_id: int,
        producer_epoch: int,
        group_id: str,
    ) -> None: ...
    def build(
        self, request_struct_class: type[AddOffsetsToTxnRequestStruct]
    ) -> AddOffsetsToTxnRequestStruct: ...

class EndTxnResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class EndTxnRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = EndTxnResponse_v0
    SCHEMA: Incomplete

EndTxnRequestStruct: TypeAlias = EndTxnRequest_v0

class EndTxnRequest(Request[EndTxnRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        transactional_id: str,
        producer_id: int,
        producer_epoch: int,
        transaction_result: bool,
    ) -> None: ...
    def build(
        self, request_struct_class: type[EndTxnRequestStruct]
    ) -> EndTxnRequestStruct: ...

class TxnOffsetCommitResponse_v0(Response):
    API_KEY: int
    API_VERSION: int
    SCHEMA: Incomplete

class TxnOffsetCommitRequest_v0(RequestStruct):
    API_KEY: int
    API_VERSION: int
    RESPONSE_TYPE = TxnOffsetCommitResponse_v0
    SCHEMA: Incomplete

TxnOffsetCommitRequestStruct: TypeAlias = TxnOffsetCommitRequest_v0

class TxnOffsetCommitRequest(Request[TxnOffsetCommitRequestStruct]):
    API_KEY: int
    def __init__(
        self,
        transactional_id: str,
        group_id: str,
        producer_id: int,
        producer_epoch: int,
        topics: list[tuple[str, list[tuple[int, int, str]]]],
    ) -> None: ...
    def build(
        self, request_struct_class: type[TxnOffsetCommitRequestStruct]
    ) -> TxnOffsetCommitRequestStruct: ...
