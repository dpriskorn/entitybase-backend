from _typeshed import Incomplete
from aiokafka.client import (
    ConnectionGroup as ConnectionGroup,
    CoordinationType as CoordinationType,
)
from aiokafka.coordinator.assignors.roundrobin import (
    RoundRobinPartitionAssignor as RoundRobinPartitionAssignor,
)
from aiokafka.coordinator.protocol import ConsumerProtocol as ConsumerProtocol
from aiokafka.protocol.api import Response as Response
from aiokafka.protocol.commit import (
    OffsetCommitRequest as OffsetCommitRequest,
    OffsetFetchRequest as OffsetFetchRequest,
)
from aiokafka.protocol.group import (
    HeartbeatRequest as HeartbeatRequest,
    JoinGroupRequest as JoinGroupRequest,
    LeaveGroupRequest as LeaveGroupRequest,
    SyncGroupRequest as SyncGroupRequest,
)
from aiokafka.structs import (
    OffsetAndMetadata as OffsetAndMetadata,
    TopicPartition as TopicPartition,
)
from aiokafka.util import create_future as create_future, create_task as create_task

log: Incomplete
UNKNOWN_OFFSET: int

class BaseCoordinator:
    def __init__(
        self, client, subscription, *, exclude_internal_topics: bool = True
    ) -> None: ...

class NoGroupCoordinator(BaseCoordinator):
    def __init__(self, *args, **kw) -> None: ...
    def assign_all_partitions(self, check_unknown: bool = False) -> None: ...
    async def close(self) -> None: ...
    def check_errors(self) -> None: ...

class GroupCoordinator(BaseCoordinator):
    generation: Incomplete
    member_id: Incomplete
    group_id: Incomplete
    coordinator_id: Incomplete
    def __init__(
        self,
        client,
        subscription,
        *,
        group_id: str = "aiokafka-default-group",
        group_instance_id=None,
        session_timeout_ms: int = 10000,
        heartbeat_interval_ms: int = 3000,
        retry_backoff_ms: int = 100,
        enable_auto_commit: bool = True,
        auto_commit_interval_ms: int = 5000,
        assignors=...,
        exclude_internal_topics: bool = True,
        max_poll_interval_ms: int = 300000,
        rebalance_timeout_ms: int = 30000,
    ) -> None: ...
    def check_errors(self) -> None: ...
    async def close(self) -> None: ...
    def maybe_leave_group(self): ...
    def coordinator_dead(self) -> None: ...
    def reset_generation(self) -> None: ...
    def request_rejoin(self) -> None: ...
    def need_rejoin(self, subscription): ...
    async def ensure_coordinator_known(self) -> None: ...
    async def ensure_active_group(self, subscription, prev_assignment): ...
    def start_commit_offsets_refresh_task(self, assignment) -> None: ...
    async def commit_offsets(self, assignment, offsets) -> None: ...
    async def fetch_committed_offsets(self, partitions): ...

class CoordinatorGroupRebalance:
    group_id: Incomplete
    coordinator_id: Incomplete
    def __init__(
        self,
        coordinator,
        group_id,
        coordinator_id,
        subscription,
        assignors,
        session_timeout_ms,
        retry_backoff_ms,
    ) -> None: ...
    async def perform_group_join(self): ...
