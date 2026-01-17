from aiokafka.errors import KafkaError
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, NamedTuple, TypeVar

__all__ = [
    "BrokerMetadata",
    "ConsumerRecord",
    "OffsetAndMetadata",
    "PartitionMetadata",
    "RecordMetadata",
    "TopicPartition",
]

class TopicPartition(NamedTuple):
    topic: str
    partition: int

class BrokerMetadata(NamedTuple):
    nodeId: int | str
    host: str
    port: int
    rack: str | None

class PartitionMetadata(NamedTuple):
    topic: str
    partition: int
    leader: int
    replicas: list[int]
    isr: list[int]
    error: KafkaError | None

class OffsetAndMetadata(NamedTuple):
    offset: int
    metadata: str

class RecordMetadata(NamedTuple):
    topic: str
    partition: int
    topic_partition: TopicPartition
    offset: int
    timestamp: int | None
    timestamp_type: int
    log_start_offset: int | None

KT = TypeVar("KT")
VT = TypeVar("VT")

@dataclass
class ConsumerRecord(Generic[KT, VT]):
    topic: str
    partition: int
    offset: int
    timestamp: int
    timestamp_type: int
    key: KT | None
    value: VT | None
    checksum: int | None
    serialized_key_size: int
    serialized_value_size: int
    headers: Sequence[tuple[str, bytes]]

class OffsetAndTimestamp(NamedTuple):
    offset: int
    timestamp: int | None
