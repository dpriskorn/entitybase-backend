from _typeshed import Incomplete
from attrs import define
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from jsonschema import _types
from referencing.exceptions import Unresolvable as _Unresolvable
from typing import Any

WEAK_MATCHES: frozenset[str]
STRONG_MATCHES: frozenset[str]

def __getattr__(name): ...

class _Error(Exception):
    message: Incomplete
    path: Incomplete
    schema_path: Incomplete
    context: Incomplete
    cause: Incomplete
    validator: Incomplete
    validator_value: Incomplete
    instance: Incomplete
    schema: Incomplete
    parent: Incomplete
    def __init__(
        self,
        message: str,
        validator: str = ...,
        path: Iterable[str | int] = (),
        cause: Exception | None = None,
        context=(),
        validator_value: Any = ...,
        instance: Any = ...,
        schema: Mapping[str, Any] | bool = ...,
        schema_path: Iterable[str | int] = (),
        parent: _Error | None = None,
        type_checker: _types.TypeChecker = ...,
    ) -> None: ...
    @classmethod
    def create_from(cls, other: _Error): ...
    @property
    def absolute_path(self) -> Sequence[str | int]: ...
    @property
    def absolute_schema_path(self) -> Sequence[str | int]: ...
    @property
    def json_path(self) -> str: ...

class ValidationError(_Error): ...
class SchemaError(_Error): ...

@define(slots=False)
class _RefResolutionError(Exception):
    def __eq__(self, other): ...

class _WrappedReferencingError(_RefResolutionError, _Unresolvable):
    def __init__(self, cause: _Unresolvable) -> None: ...
    def __eq__(self, other): ...
    def __getattr__(self, attr): ...
    def __hash__(self): ...

class UndefinedTypeCheck(Exception):
    type: Incomplete
    def __init__(self, type: str) -> None: ...

class UnknownType(Exception):
    type: Incomplete
    instance: Incomplete
    schema: Incomplete
    def __init__(self, type, instance, schema) -> None: ...

class FormatError(Exception):
    message: Incomplete
    cause: Incomplete
    def __init__(self, message, cause=None) -> None: ...

class ErrorTree:
    errors: MutableMapping[str, ValidationError]
    def __init__(self, errors: Iterable[ValidationError] = ()) -> None: ...
    def __contains__(self, index: str | int): ...
    def __getitem__(self, index): ...
    def __setitem__(self, index: str | int, value: ErrorTree): ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    @property
    def total_errors(self): ...

def by_relevance(weak=..., strong=...): ...

relevance: Incomplete

def best_match(errors, key=...): ...
