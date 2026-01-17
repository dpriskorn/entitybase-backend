from _typeshed import Incomplete
from rdflib import Dataset as Dataset
from rdflib.serializer import Serializer as Serializer
from typing import Any, IO

add_remove_methods: Incomplete

class PatchSerializer(Serializer):
    store: Dataset
    def __init__(self, store: Dataset) -> None: ...
    def serialize(
        self,
        stream: IO[bytes],
        base: str | None = None,
        encoding: str | None = None,
        **kwargs: Any,
    ) -> None: ...
