from _typeshed import Incomplete
from aiokafka.cluster import ClusterMetadata as ClusterMetadata
from aiokafka.coordinator.assignors.abstract import (
    AbstractPartitionAssignor as AbstractPartitionAssignor,
)
from aiokafka.coordinator.protocol import (
    ConsumerProtocolMemberAssignment as ConsumerProtocolMemberAssignment,
    ConsumerProtocolMemberMetadata as ConsumerProtocolMemberMetadata,
)
from collections.abc import Iterable, Mapping

log: Incomplete

class RangePartitionAssignor(AbstractPartitionAssignor):
    name: str
    version: int
    @classmethod
    def assign(
        cls,
        cluster: ClusterMetadata,
        members: Mapping[str, ConsumerProtocolMemberMetadata],
    ) -> dict[str, ConsumerProtocolMemberAssignment]: ...
    @classmethod
    def metadata(cls, topics: Iterable[str]) -> ConsumerProtocolMemberMetadata: ...
    @classmethod
    def on_assignment(cls, assignment: ConsumerProtocolMemberAssignment) -> None: ...
