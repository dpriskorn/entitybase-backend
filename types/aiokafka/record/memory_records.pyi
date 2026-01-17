from ._protocols import (
    DefaultRecordBatchProtocol as DefaultRecordBatchProtocol,
    LegacyRecordBatchProtocol as LegacyRecordBatchProtocol,
    MemoryRecordsProtocol as MemoryRecordsProtocol,
)
from .default_records import DefaultRecordBatch as DefaultRecordBatch
from .legacy_records import LegacyRecordBatch as LegacyRecordBatch
from _typeshed import Incomplete
from aiokafka.errors import CorruptRecordException as CorruptRecordException
from aiokafka.util import NO_EXTENSIONS as NO_EXTENSIONS

class _MemoryRecordsPy(MemoryRecordsProtocol):
    LENGTH_OFFSET: Incomplete
    LOG_OVERHEAD: Incomplete
    MAGIC_OFFSET: Incomplete
    MIN_SLICE: Incomplete
    def __init__(self, bytes_data: bytes) -> None: ...
    def size_in_bytes(self) -> int: ...
    def has_next(self) -> bool: ...
    def next_batch(
        self, _min_slice: int = ..., _magic_offset: int = ...
    ) -> DefaultRecordBatchProtocol | LegacyRecordBatchProtocol | None: ...

MemoryRecords: type[MemoryRecordsProtocol]
