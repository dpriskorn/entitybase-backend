import referencing.jsonschema
from _typeshed import Incomplete
from jsonschema.protocols import Validator as Validator
from typing import Any, Protocol

class SchemaKeywordValidator(Protocol):
    def __call__(
        self,
        validator: Validator,
        value: Any,
        instance: Any,
        schema: referencing.jsonschema.Schema,
    ) -> None: ...

id_of: Incomplete
ApplicableValidators: Incomplete
