# type: ignore[misc]
import abc
from .struct import Struct as Struct
from .types import (
    Array as Array,
    Int16 as Int16,
    Int32 as Int32,
    Schema as Schema,
    String as String,
    TaggedFields as TaggedFields,
)
from _typeshed import Incomplete
from aiokafka.errors import IncompatibleBrokerVersion as IncompatibleBrokerVersion
from io import BytesIO
from typing import Any, ClassVar, Generic, TypeVar

class RequestHeader_v1(Struct):
    SCHEMA: Incomplete
    def __init__(
        self,
        request: RequestStruct,
        correlation_id: int = 0,
        client_id: str = "aiokafka",
    ) -> None: ...

class RequestHeader_v2(Struct):
    SCHEMA: Incomplete
    def __init__(
        self,
        request: RequestStruct,
        correlation_id: int = 0,
        client_id: str = "aiokafka",
        tags: dict[int, bytes] | None = None,
    ) -> None: ...

class ResponseHeader_v0(Struct):
    SCHEMA: Incomplete

class ResponseHeader_v1(Struct):
    SCHEMA: Incomplete

T = TypeVar("T", bound="RequestStruct")

class Request(abc.ABC, Generic[T], metaclass=abc.ABCMeta):
    API_KEY: ClassVar[int]
    ALLOW_UNKNOWN_API_VERSION: ClassVar[bool]
    def __init_subclass__(cls) -> None: ...
    @abc.abstractmethod
    def build(self, request_struct_class: type[T]) -> T: ...
    def prepare(self, versions: dict[int, tuple[int, int]]) -> T: ...

class RequestStruct(Struct, metaclass=abc.ABCMeta):
    FLEXIBLE_VERSION: ClassVar[bool]
    API_KEY: ClassVar[int]
    API_VERSION: ClassVar[int]
    RESPONSE_TYPE: ClassVar[type[Response]]
    SCHEMA: ClassVar[Schema]
    def __init_subclass__(cls) -> None: ...
    def to_object(self) -> dict[str, Any]: ...
    def build_request_header(
        self, correlation_id: int, client_id: str
    ) -> RequestHeader_v1 | RequestHeader_v2: ...
    def parse_response_header(
        self, read_buffer: BytesIO | bytes
    ) -> ResponseHeader_v0 | ResponseHeader_v1: ...

class Response(Struct, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def API_KEY(self) -> int: ...
    @property
    @abc.abstractmethod
    def API_VERSION(self) -> int: ...
    def to_object(self) -> dict[str, Any]: ...
