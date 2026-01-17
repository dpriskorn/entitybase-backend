from _typeshed import Incomplete
from aiokafka.protocol.struct import Struct as Struct
from aiokafka.protocol.types import (
    Array as Array,
    Bytes as Bytes,
    Int16 as Int16,
    Int32 as Int32,
    Schema as Schema,
    String as String,
)
from aiokafka.structs import TopicPartition as TopicPartition
from typing import NamedTuple

class ConsumerProtocolMemberMetadata(Struct):
    version: int
    subscription: list[str]
    user_data: bytes
    SCHEMA: Incomplete

class ConsumerProtocolMemberAssignment(Struct):
    class Assignment(NamedTuple):
        topic: str
        partitions: list[int]

    version: int
    assignment: list[Assignment]
    user_data: bytes
    SCHEMA: Incomplete
    def partitions(self) -> list[TopicPartition]: ...

class ConsumerProtocol:
    PROTOCOL_TYPE: str
    ASSIGNMENT_STRATEGIES: Incomplete
    METADATA = ConsumerProtocolMemberMetadata
    ASSIGNMENT = ConsumerProtocolMemberAssignment
