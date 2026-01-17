import abc
from _typeshed import Incomplete
from aiokafka.cluster import ClusterMetadata as ClusterMetadata
from aiokafka.coordinator.protocol import (
    ConsumerProtocolMemberAssignment as ConsumerProtocolMemberAssignment,
    ConsumerProtocolMemberMetadata as ConsumerProtocolMemberMetadata,
)
from collections.abc import Iterable, Mapping

log: Incomplete

class AbstractPartitionAssignor(abc.ABC, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def name(self) -> str: ...
    @classmethod
    @abc.abstractmethod
    def assign(
        cls,
        cluster: ClusterMetadata,
        members: Mapping[str, ConsumerProtocolMemberMetadata],
    ) -> dict[str, ConsumerProtocolMemberAssignment]: ...
    @classmethod
    @abc.abstractmethod
    def metadata(cls, topics: Iterable[str]) -> ConsumerProtocolMemberMetadata: ...
    @classmethod
    @abc.abstractmethod
    def on_assignment(cls, assignment: ConsumerProtocolMemberAssignment) -> None: ...
