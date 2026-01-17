from _typeshed import Incomplete
from aiokafka.structs import TopicPartition as TopicPartition
from collections.abc import Sequence
from typing import Any, NamedTuple

log: Incomplete

class ConsumerPair(NamedTuple):
    src_member_id: str
    dst_member_id: str

def is_sublist(source: Sequence[Any], target: Sequence[Any]) -> bool: ...

class PartitionMovements:
    partition_movements_by_topic: dict[str, dict[ConsumerPair, set[TopicPartition]]]
    partition_movements: dict[TopicPartition, ConsumerPair]
    def __init__(self) -> None: ...
    def move_partition(
        self, partition: TopicPartition, old_consumer: str, new_consumer: str
    ) -> None: ...
    def get_partition_to_be_moved(
        self, partition: TopicPartition, old_consumer: str, new_consumer: str
    ) -> TopicPartition: ...
    def are_sticky(self) -> bool: ...
