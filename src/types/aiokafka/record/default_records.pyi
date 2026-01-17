from ._protocols import (
    DefaultRecordBatchBuilderProtocol as DefaultRecordBatchBuilderProtocol,
    DefaultRecordBatchProtocol as DefaultRecordBatchProtocol,
    DefaultRecordMetadataProtocol as DefaultRecordMetadataProtocol,
    DefaultRecordProtocol as DefaultRecordProtocol,
)
from .util import (
    calc_crc32c as calc_crc32c,
    decode_varint as decode_varint,
    encode_varint as encode_varint,
    size_of_varint as size_of_varint,
)
from _typeshed import Incomplete
from aiokafka.codec import (
    gzip_decode as gzip_decode,
    gzip_encode as gzip_encode,
    lz4_decode as lz4_decode,
    lz4_encode as lz4_encode,
    snappy_decode as snappy_decode,
    snappy_encode as snappy_encode,
    zstd_decode as zstd_decode,
    zstd_encode as zstd_encode,
)
from aiokafka.errors import (
    CorruptRecordException as CorruptRecordException,
    UnsupportedCodecError as UnsupportedCodecError,
)
from aiokafka.util import NO_EXTENSIONS as NO_EXTENSIONS
from collections.abc import Callable as Callable, Collection, Sized
from dataclasses import dataclass
from typing import Any
from typing_extensions import Self

class DefaultRecordBase:
    HEADER_STRUCT: Incomplete
    ATTRIBUTES_OFFSET: Incomplete
    CRC_OFFSET: Incomplete
    AFTER_LEN_OFFSET: Incomplete
    CODEC_MASK: int
    CODEC_NONE: int
    CODEC_GZIP: int
    CODEC_SNAPPY: int
    CODEC_LZ4: int
    CODEC_ZSTD: int
    TIMESTAMP_TYPE_MASK: int
    TRANSACTIONAL_MASK: int
    CONTROL_MASK: int
    LOG_APPEND_TIME: int
    CREATE_TIME: int
    NO_PARTITION_LEADER_EPOCH: int

class _DefaultRecordBatchPy(DefaultRecordBase, DefaultRecordBatchProtocol):
    def __init__(self, buffer: bytes | bytearray | memoryview) -> None: ...
    @property
    def base_offset(self) -> int: ...
    @property
    def magic(self) -> int: ...
    @property
    def crc(self) -> int: ...
    @property
    def attributes(self) -> int: ...
    @property
    def compression_type(self) -> int: ...
    @property
    def timestamp_type(self) -> int: ...
    @property
    def is_transactional(self) -> bool: ...
    @property
    def is_control_batch(self) -> bool: ...
    @property
    def last_offset_delta(self) -> int: ...
    @property
    def first_timestamp(self) -> int: ...
    @property
    def max_timestamp(self) -> int: ...
    @property
    def producer_id(self) -> int: ...
    @property
    def producer_epoch(self) -> int: ...
    @property
    def base_sequence(self) -> int: ...
    @property
    def next_offset(self) -> int: ...
    def __iter__(self) -> Self: ...
    def __next__(self) -> _DefaultRecordPy: ...
    def validate_crc(self) -> bool: ...

@dataclass(frozen=True)
class _DefaultRecordPy(DefaultRecordProtocol):
    offset: int
    timestamp: int
    timestamp_type: int
    key: bytes | None
    value: bytes | None
    headers: list[tuple[str, bytes | None]]
    @property
    def checksum(self) -> None: ...

class _DefaultRecordBatchBuilderPy(
    DefaultRecordBase, DefaultRecordBatchBuilderProtocol
):
    MAX_RECORD_OVERHEAD: int
    def __init__(
        self,
        magic: int,
        compression_type: int,
        is_transactional: int,
        producer_id: int,
        producer_epoch: int,
        base_sequence: int,
        batch_size: int,
    ) -> None: ...
    def append(
        self,
        offset: int,
        timestamp: int | None,
        key: bytes | None,
        value: bytes | None,
        headers: list[tuple[str, bytes | None]],
        encode_varint: Callable[[int, Callable[[int], None]], int] = ...,
        size_of_varint: Callable[[int], int] = ...,
        get_type: Callable[[Any], type] = ...,
        type_int: type[int] = ...,
        time_time: Callable[[], float] = ...,
        byte_like: Collection[type] = ...,
        bytearray_type: type[bytearray] = ...,
        len_func: Callable[[Sized], int] = ...,
        zero_len_varint: int = 1,
    ) -> _DefaultRecordMetadataPy | None: ...
    def build(self) -> bytearray: ...
    def size(self) -> int: ...
    def size_in_bytes(
        self,
        offset: int,
        timestamp: int,
        key: bytes | None,
        value: bytes | None,
        headers: list[tuple[str, bytes | None]],
    ) -> int: ...
    @classmethod
    def size_of(
        cls,
        key: bytes | None,
        value: bytes | None,
        headers: list[tuple[str, bytes | None]],
    ) -> int: ...
    @classmethod
    def estimate_size_in_bytes(
        cls,
        key: bytes | None,
        value: bytes | None,
        headers: list[tuple[str, bytes | None]],
    ) -> int: ...
    def set_producer_state(
        self, producer_id: int, producer_epoch: int, base_sequence: int
    ) -> None: ...
    @property
    def producer_id(self) -> int: ...
    @property
    def producer_epoch(self) -> int: ...
    @property
    def base_sequence(self) -> int: ...

@dataclass(frozen=True)
class _DefaultRecordMetadataPy(DefaultRecordMetadataProtocol):
    offset: int
    size: int
    timestamp: int
    @property
    def crc(self) -> None: ...

DefaultRecordBatchBuilder: type[DefaultRecordBatchBuilderProtocol]
DefaultRecordMetadata: type[DefaultRecordMetadataProtocol]
DefaultRecordBatch: type[DefaultRecordBatchProtocol]
DefaultRecord: type[DefaultRecordProtocol]
