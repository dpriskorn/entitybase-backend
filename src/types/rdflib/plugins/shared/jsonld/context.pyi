from .errors import (
    INVALID_CONTEXT_ENTRY as INVALID_CONTEXT_ENTRY,
    INVALID_REMOTE_CONTEXT as INVALID_REMOTE_CONTEXT,
    RECURSIVE_CONTEXT_INCLUSION as RECURSIVE_CONTEXT_INCLUSION,
)
from .keys import (
    BASE as BASE,
    CONTAINER as CONTAINER,
    CONTEXT as CONTEXT,
    GRAPH as GRAPH,
    ID as ID,
    IMPORT as IMPORT,
    INCLUDED as INCLUDED,
    INDEX as INDEX,
    JSON as JSON,
    LANG as LANG,
    LIST as LIST,
    NEST as NEST,
    NONE as NONE,
    PREFIX as PREFIX,
    PROPAGATE as PROPAGATE,
    PROTECTED as PROTECTED,
    REV as REV,
    SET as SET,
    TYPE as TYPE,
    VALUE as VALUE,
    VERSION as VERSION,
    VOCAB as VOCAB,
)
from .util import (
    norm_url as norm_url,
    source_to_json as source_to_json,
    split_iri as split_iri,
)
from _typeshed import Incomplete
from rdflib.namespace import RDF as RDF
from typing import Any, Collection, Generator, NamedTuple

NODE_KEYS: Incomplete

class Defined(int): ...

UNDEF: Incomplete
URI_GEN_DELIMS: Incomplete

class Context:
    version: float
    language: Incomplete
    vocab: str | None
    doc_base: Incomplete
    terms: dict[str, Any]
    active: bool
    parent: Context | None
    propagate: bool
    def __init__(
        self,
        source: _ContextSourceType = None,
        base: str | None = None,
        version: float | None = 1.1,
    ) -> None: ...
    @property
    def base(self) -> str | None: ...
    @base.setter
    def base(self, base: str | None): ...
    def subcontext(self, source: Any, propagate: bool = True) -> Context: ...
    def get_context_for_term(self, term: Term | None) -> Context: ...
    def get_context_for_type(self, node: Any) -> Context | None: ...
    def get_id(self, obj: dict[str, Any]) -> Any: ...
    def get_type(self, obj: dict[str, Any]) -> Any: ...
    def get_language(self, obj: dict[str, Any]) -> Any: ...
    def get_value(self, obj: dict[str, Any]) -> Any: ...
    def get_graph(self, obj: dict[str, Any]) -> Any: ...
    def get_list(self, obj: dict[str, Any]) -> Any: ...
    def get_set(self, obj: dict[str, Any]) -> Any: ...
    def get_rev(self, obj: dict[str, Any]) -> Any: ...
    def get_key(self, key: str) -> str: ...
    def get_keys(self, key: str) -> Generator[str, None, None]: ...
    lang_key: Incomplete
    id_key: Incomplete
    type_key: Incomplete
    value_key: Incomplete
    list_key: Incomplete
    rev_key: Incomplete
    graph_key: Incomplete
    def add_term(
        self,
        name: str,
        idref: str,
        coercion: Defined | str = ...,
        container: Collection[Any] | str | Defined = ...,
        index: str | Defined | None = None,
        language: str | Defined | None = ...,
        reverse: bool = False,
        context: Any = ...,
        prefix: bool | None = None,
        protected: bool = False,
    ): ...
    def find_term(
        self,
        idref: str,
        coercion: str | Defined | None = None,
        container: Defined | str = ...,
        language: str | None = None,
        reverse: bool = False,
    ): ...
    def resolve(self, curie_or_iri: str) -> str: ...
    def resolve_iri(self, iri: str) -> str: ...
    def isblank(self, ref: str) -> bool: ...
    def expand(self, term_curie_or_iri: Any, use_vocab: bool = True) -> str | None: ...
    def shrink_iri(self, iri: str) -> str: ...
    def to_symbol(self, iri: str) -> str | None: ...
    def load(
        self,
        source: _ContextSourceType,
        base: str | None = None,
        referenced_contexts: set[Any] = None,
    ): ...
    def to_dict(self) -> dict[str, Any]: ...

class Term(NamedTuple):
    id: Incomplete
    name: Incomplete
    type: Incomplete
    container: Incomplete
    index: Incomplete
    language: Incomplete
    reverse: Incomplete
    context: Incomplete
    prefix: Incomplete
    protected: Incomplete
