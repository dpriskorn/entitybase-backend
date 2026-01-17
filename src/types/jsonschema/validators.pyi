import contextlib
import referencing.jsonschema
from _typeshed import Incomplete
from collections.abc import Generator, Iterable, Mapping
from jsonschema import _format, _types, _typing, _utils, exceptions as exceptions
from jsonschema.protocols import Validator as Validator

def __getattr__(name): ...
def validates(version): ...
def create(
    meta_schema: referencing.jsonschema.ObjectSchema,
    validators: Mapping[str, _typing.SchemaKeywordValidator]
    | Iterable[tuple[str, _typing.SchemaKeywordValidator]] = (),
    version: str | None = None,
    type_checker: _types.TypeChecker = ...,
    format_checker: _format.FormatChecker = ...,
    id_of: _typing.id_of = ...,
    applicable_validators: _typing.ApplicableValidators = ...,
) -> type[Validator]: ...
def extend(
    validator, validators=(), version=None, type_checker=None, format_checker=None
): ...

Draft3Validator: Incomplete
Draft4Validator: Incomplete
Draft6Validator: Incomplete
Draft7Validator: Incomplete
Draft201909Validator: Incomplete
Draft202012Validator: Incomplete

class _RefResolver:
    referrer: Incomplete
    cache_remote: Incomplete
    handlers: Incomplete
    store: Incomplete
    def __init__(
        self,
        base_uri,
        referrer,
        store=...,
        cache_remote: bool = True,
        handlers=(),
        urljoin_cache=None,
        remote_cache=None,
    ) -> None: ...
    @classmethod
    def from_schema(cls, schema, id_of=..., *args, **kwargs): ...
    def push_scope(self, scope) -> None: ...
    def pop_scope(self) -> None: ...
    @property
    def resolution_scope(self): ...
    @property
    def base_uri(self): ...
    @contextlib.contextmanager
    def in_scope(self, scope) -> Generator[None]: ...
    @contextlib.contextmanager
    def resolving(self, ref) -> Generator[Incomplete]: ...
    def resolve(self, ref): ...
    def resolve_from_url(self, url): ...
    def resolve_fragment(self, document, fragment): ...
    def resolve_remote(self, uri): ...

def validate(instance, schema, cls=None, *args, **kwargs) -> None: ...
def validator_for(
    schema, default: type[Validator] | _utils.Unset = ...
) -> type[Validator]: ...
