from _typeshed import Incomplete
from aiokafka.errors import (
    ConsumerStoppedError as ConsumerStoppedError,
    KafkaTimeoutError as KafkaTimeoutError,
    RecordTooLargeError as RecordTooLargeError,
)
from aiokafka.protocol.fetch import FetchRequest as FetchRequest
from aiokafka.protocol.offset import OffsetRequest as OffsetRequest
from aiokafka.record.control_record import (
    ABORT_MARKER as ABORT_MARKER,
    ControlRecord as ControlRecord,
)
from aiokafka.record.memory_records import MemoryRecords as MemoryRecords
from aiokafka.structs import (
    ConsumerRecord as ConsumerRecord,
    OffsetAndTimestamp as OffsetAndTimestamp,
    TopicPartition as TopicPartition,
)
from aiokafka.util import create_future as create_future, create_task as create_task

log: Incomplete
UNKNOWN_OFFSET: int
READ_UNCOMMITTED: int
READ_COMMITTED: int

class OffsetResetStrategy:
    LATEST: int
    EARLIEST: int
    NONE: int
    @classmethod
    def from_str(cls, name): ...
    @classmethod
    def to_str(cls, value): ...

class FetchResult:
    def __init__(self, tp, *, assignment, partition_records, backoff) -> None: ...
    def calculate_backoff(self): ...
    def check_assignment(self, tp): ...
    def getone(self): ...
    def getall(self, max_records=None): ...
    def has_more(self): ...

class FetchError:
    def __init__(self, *, error, backoff) -> None: ...
    def calculate_backoff(self): ...
    def check_raise(self) -> None: ...

class PartitionRecords:
    next_fetch_offset: Incomplete
    def __init__(
        self,
        tp,
        records,
        aborted_transactions,
        fetch_offset,
        key_deserializer,
        value_deserializer,
        check_crcs,
        isolation_level,
    ) -> None: ...
    def __iter__(self): ...
    def __next__(self): ...

class Fetcher:
    def __init__(
        self,
        client,
        subscriptions,
        *,
        key_deserializer=None,
        value_deserializer=None,
        fetch_min_bytes: int = 1,
        fetch_max_bytes: int = 52428800,
        fetch_max_wait_ms: int = 500,
        max_partition_fetch_bytes: int = 1048576,
        check_crcs: bool = True,
        fetcher_timeout: float = 0.2,
        prefetch_backoff: float = 0.1,
        retry_backoff_ms: int = 100,
        auto_offset_reset: str = "latest",
        isolation_level: str = "read_uncommitted",
    ) -> None: ...
    async def close(self) -> None: ...
    @property
    def error_future(self): ...
    async def next_record(self, partitions): ...
    async def fetched_records(self, partitions, timeout: int = 0, max_records=None): ...
    async def get_offsets_by_times(self, timestamps, timeout_ms): ...
    async def beginning_offsets(self, partitions, timeout_ms): ...
    async def end_offsets(self, partitions, timeout_ms): ...
    def request_offset_reset(self, tps, strategy): ...
    def seek_to(self, tp, offset) -> None: ...
