from _typeshed import Incomplete
from aiokafka.cluster import ClusterMetadata as ClusterMetadata
from aiokafka.coordinator.assignors.abstract import (
    AbstractPartitionAssignor as AbstractPartitionAssignor,
)
from aiokafka.coordinator.assignors.sticky.partition_movements import (
    PartitionMovements as PartitionMovements,
)
from aiokafka.coordinator.assignors.sticky.sorted_set import SortedSet as SortedSet
from aiokafka.coordinator.protocol import (
    ConsumerProtocolMemberAssignment as ConsumerProtocolMemberAssignment,
    ConsumerProtocolMemberMetadata as ConsumerProtocolMemberMetadata,
    Schema as Schema,
)
from aiokafka.protocol.struct import Struct as Struct
from aiokafka.protocol.types import Array as Array, Int32 as Int32, String as String
from aiokafka.structs import TopicPartition as TopicPartition
from collections.abc import (
    Collection,
    Iterable,
    Mapping,
    MutableSequence,
    Sequence,
    Sized,
)
from typing import Any, NamedTuple

log: Incomplete

class ConsumerGenerationPair(NamedTuple):
    consumer: str
    generation: int

class ConsumerSubscription(NamedTuple):
    consumer: str
    partitions: Sequence[TopicPartition]

def has_identical_list_elements(list_: Sequence[list[Any]]) -> bool: ...
def subscriptions_comparator_key(element: tuple[str, Sized]) -> tuple[int, str]: ...
def partitions_comparator_key(
    element: tuple[TopicPartition, Sized],
) -> tuple[int, str, int]: ...
def remove_if_present(collection: MutableSequence[Any], element: Any) -> None: ...

class StickyAssignorMemberMetadataV1(NamedTuple):
    subscription: list[str]
    partitions: list[TopicPartition]
    generation: int

class StickyAssignorUserDataV1(Struct):
    class PreviousAssignment(NamedTuple):
        topic: str
        partitions: list[int]

    previous_assignment: list[PreviousAssignment]
    generation: int
    SCHEMA: Incomplete

class StickyAssignmentExecutor:
    members: Incomplete
    current_assignment: dict[str, list[TopicPartition]]
    previous_assignment: dict[TopicPartition, ConsumerGenerationPair]
    current_partition_consumer: dict[TopicPartition, str]
    is_fresh_assignment: bool
    partition_to_all_potential_consumers: dict[TopicPartition, list[str]]
    consumer_to_all_potential_partitions: dict[str, list[TopicPartition]]
    sorted_current_subscriptions: SortedSet[ConsumerSubscription]
    sorted_partitions: list[TopicPartition]
    unassigned_partitions: list[TopicPartition]
    revocation_required: bool
    partition_movements: Incomplete
    def __init__(
        self,
        cluster: ClusterMetadata,
        members: dict[str, StickyAssignorMemberMetadataV1],
    ) -> None: ...
    def perform_initial_assignment(self) -> None: ...
    def balance(self) -> None: ...
    def get_final_assignment(
        self, member_id: str
    ) -> Collection[tuple[str, list[int]]]: ...

class StickyPartitionAssignor(AbstractPartitionAssignor):
    DEFAULT_GENERATION_ID: int
    name: str
    version: int
    member_assignment: list[TopicPartition] | None
    generation: int
    @classmethod
    def assign(
        cls,
        cluster: ClusterMetadata,
        members: Mapping[str, ConsumerProtocolMemberMetadata],
    ) -> dict[str, ConsumerProtocolMemberAssignment]: ...
    @classmethod
    def parse_member_metadata(
        cls, metadata: ConsumerProtocolMemberMetadata
    ) -> StickyAssignorMemberMetadataV1: ...
    @classmethod
    def metadata(cls, topics: Iterable[str]) -> ConsumerProtocolMemberMetadata: ...
    @classmethod
    def on_assignment(cls, assignment: ConsumerProtocolMemberAssignment) -> None: ...
    @classmethod
    def on_generation_assignment(cls, generation: int) -> None: ...
