# type: ignore[misc]
import io
from .struct import Struct as Struct
from .types import (
    Bytes as Bytes,
    Int32 as Int32,
    Int64 as Int64,
    Int8 as Int8,
    Schema as Schema,
    UInt32 as UInt32,
)
from _typeshed import Incomplete
from aiokafka.codec import (
    gzip_decode as gzip_decode,
    has_gzip as has_gzip,
    has_lz4 as has_lz4,
    has_snappy as has_snappy,
    has_zstd as has_zstd,
    lz4_decode as lz4_decode,
    snappy_decode as snappy_decode,
    zstd_decode as zstd_decode,
)
from collections.abc import Iterable
from typing import Literal, overload
from typing_extensions import Self

class Message(Struct):
    BASE_FIELDS: Incomplete
    MAGIC0_FIELDS: Incomplete
    MAGIC1_FIELDS: Incomplete
    SCHEMAS: Incomplete
    SCHEMA: Incomplete
    CODEC_MASK: int
    CODEC_GZIP: int
    CODEC_SNAPPY: int
    CODEC_LZ4: int
    CODEC_ZSTD: int
    TIMESTAMP_TYPE_MASK: int
    HEADER_SIZE: int
    @overload
    def __init__(
        self,
        *,
        value: bytes | None,
        key: bytes | None,
        magic: Literal[0],
        attributes: int,
        crc: int,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *,
        value: bytes | None,
        key: bytes | None,
        magic: Literal[1],
        attributes: int,
        crc: int,
        timestamp: int,
    ) -> None: ...
    @property
    def timestamp_type(self) -> Literal[0, 1] | None: ...
    crc: Incomplete
    def encode(self, recalc_crc: bool = True) -> bytes: ...
    @classmethod
    def decode(cls, data: io.BytesIO | bytes) -> Self: ...
    def validate_crc(self) -> bool: ...
    def is_compressed(self) -> bool: ...
    def decompress(
        self,
    ) -> list[tuple[int, int, "Message"] | tuple[None, None, "PartialMessage"]]: ...

class PartialMessage(bytes): ...

class MessageSet:
    ITEM: Incomplete
    HEADER_SIZE: int
    @classmethod
    def encode(
        cls, items: io.BytesIO | Iterable[tuple[int, bytes]], prepend_size: bool = True
    ) -> bytes: ...
    @classmethod
    def decode(
        cls, data: io.BytesIO | bytes, bytes_to_read: int | None = None
    ) -> list[tuple[int, int, Message] | tuple[None, None, PartialMessage]]: ...
    @classmethod
    def repr(
        cls,
        messages: io.BytesIO
        | list[tuple[int, int, Message] | tuple[None, None, PartialMessage]],
    ) -> str: ...
