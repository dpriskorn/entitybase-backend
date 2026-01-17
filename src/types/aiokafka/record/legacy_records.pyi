from ._protocols import (
    LegacyRecordBatchBuilderProtocol as LegacyRecordBatchBuilderProtocol,
    LegacyRecordBatchProtocol as LegacyRecordBatchProtocol,
    LegacyRecordMetadataProtocol as LegacyRecordMetadataProtocol,
    LegacyRecordProtocol as LegacyRecordProtocol,
)
from _typeshed import Incomplete
from aiokafka.codec import (
    gzip_decode as gzip_decode,
    gzip_encode as gzip_encode,
    lz4_decode as lz4_decode,
    lz4_encode as lz4_encode,
    snappy_decode as snappy_decode,
    snappy_encode as snappy_encode,
)
from aiokafka.errors import (
    CorruptRecordException as CorruptRecordException,
    UnsupportedCodecError as UnsupportedCodecError,
)
from aiokafka.util import NO_EXTENSIONS as NO_EXTENSIONS
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any, Literal
from typing_extensions import Never

class LegacyRecordBase:
    HEADER_STRUCT_V0: Incomplete
    HEADER_STRUCT_V1: Incomplete
    LOG_OVERHEAD: Incomplete
    CRC_OFFSET: Incomplete
    MAGIC_OFFSET: Incomplete
    RECORD_OVERHEAD_V0: Incomplete
    RECORD_OVERHEAD_V1: Incomplete
    RECORD_OVERHEAD: Incomplete
    KEY_OFFSET_V0: Incomplete
    KEY_OFFSET_V1: Incomplete
    KEY_LENGTH: Incomplete
    VALUE_LENGTH: Incomplete
    CODEC_MASK: int
    CODEC_GZIP: int
    CODEC_SNAPPY: int
    CODEC_LZ4: int
    TIMESTAMP_TYPE_MASK: int
    LOG_APPEND_TIME: int
    CREATE_TIME: int

class _LegacyRecordBatchPy(LegacyRecordBase, LegacyRecordBatchProtocol):
    is_control_batch: bool
    is_transactional: bool
    producer_id: int | None
    def __init__(self, buffer: bytes | bytearray | memoryview, magic: int) -> None: ...
    @property
    def next_offset(self) -> int: ...
    def validate_crc(self) -> bool: ...
    def __iter__(self) -> Generator[_LegacyRecordPy, None, None]: ...

@dataclass(frozen=True)
class _LegacyRecordPy(LegacyRecordProtocol):
    offset: int
    timestamp: int | None
    timestamp_type: Literal[0, 1] | None
    key: bytes | None
    value: bytes | None
    crc: int
    @property
    def headers(self) -> list[Never]: ...
    @property
    def checksum(self) -> int: ...

class _LegacyRecordBatchBuilderPy(LegacyRecordBase, LegacyRecordBatchBuilderProtocol):
    def __init__(
        self, magic: Literal[0, 1], compression_type: int, batch_size: int
    ) -> None: ...
    def append(
        self,
        offset: int,
        timestamp: int | None,
        key: bytes | None,
        value: bytes | None,
        headers: Any = None,
    ) -> _LegacyRecordMetadataPy | None: ...
    def build(self) -> bytearray: ...
    def size(self) -> int: ...
    def size_in_bytes(
        self, offset: Any, timestamp: Any, key: bytes | None, value: bytes | None
    ) -> int: ...
    @classmethod
    def record_overhead(cls, magic: int) -> int: ...

class _LegacyRecordMetadataPy(LegacyRecordMetadataProtocol):
    def __init__(self, offset: int, crc: int, size: int, timestamp: int) -> None: ...
    @property
    def offset(self) -> int: ...
    @property
    def crc(self) -> int: ...
    @property
    def size(self) -> int: ...
    @property
    def timestamp(self) -> int: ...

LegacyRecordBatchBuilder: type[LegacyRecordBatchBuilderProtocol]
LegacyRecordMetadata: type[LegacyRecordMetadataProtocol]
LegacyRecordBatch: type[LegacyRecordBatchProtocol]
LegacyRecord: type[LegacyRecordProtocol]
