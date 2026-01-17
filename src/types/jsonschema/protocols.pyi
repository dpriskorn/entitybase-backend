import jsonschema
import referencing.jsonschema
from collections.abc import Iterable, Mapping
from jsonschema import _typing
from jsonschema.exceptions import ValidationError as ValidationError
from typing import Any, ClassVar, Protocol

class Validator(Protocol):
    META_SCHEMA: ClassVar[Mapping]
    VALIDATORS: ClassVar[Mapping]
    TYPE_CHECKER: ClassVar[jsonschema.TypeChecker]
    FORMAT_CHECKER: ClassVar[jsonschema.FormatChecker]
    ID_OF: _typing.id_of
    schema: Mapping | bool
    def __init__(
        self,
        schema: Mapping | bool,
        resolver: Any = None,
        format_checker: jsonschema.FormatChecker | None = None,
        *,
        registry: referencing.jsonschema.SchemaRegistry = ...,
    ) -> None: ...
    @classmethod
    def check_schema(cls, schema: Mapping | bool) -> None: ...
    def is_type(self, instance: Any, type: str) -> bool: ...
    def is_valid(self, instance: Any) -> bool: ...
    def iter_errors(self, instance: Any) -> Iterable[ValidationError]: ...
    def validate(self, instance: Any) -> None: ...
    def evolve(self, **kwargs) -> Validator: ...
