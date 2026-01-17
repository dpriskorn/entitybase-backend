import json as json
import orjson as orjson
import pathlib
from _typeshed import Incomplete
from html.parser import HTMLParser
from rdflib.parser import InputSource, URLInputSource
from typing import Any, IO, TextIO

__all__ = [
    "json",
    "source_to_json",
    "split_iri",
    "norm_url",
    "context_from_urlinputsource",
    "orjson",
    "_HAS_ORJSON",
]

_HAS_ORJSON: bool

def source_to_json(
    source: IO[bytes] | TextIO | InputSource | str | bytes | pathlib.PurePath | None,
    fragment_id: str | None = None,
    extract_all_scripts: bool | None = False,
) -> tuple[dict | list[dict], Any]: ...
def split_iri(iri: str) -> tuple[str, str | None]: ...
def norm_url(base: str, url: str) -> str: ...
def context_from_urlinputsource(source: URLInputSource) -> str | None: ...

class HTMLJSONParser(HTMLParser):
    fragment_id: Incomplete
    json: list[dict]
    contains_json: bool
    fragment_id_does_not_match: bool
    base: Incomplete
    extract_all_scripts: Incomplete
    script_count: int
    def __init__(
        self, fragment_id: str | None = None, extract_all_scripts: bool | None = False
    ) -> None: ...
    def handle_starttag(self, tag, attrs) -> None: ...
    def handle_data(self, data) -> None: ...
    def get_json(self) -> list[dict]: ...
    def get_base(self): ...
