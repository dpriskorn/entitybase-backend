import logging
from _typeshed import Incomplete
from typing import Literal

TRACE_LOG_LEVEL: int

class ColourizedFormatter(logging.Formatter):
    level_name_colors: Incomplete
    use_colors: Incomplete
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool | None = None,
    ) -> None: ...
    def color_level_name(self, level_name: str, level_no: int) -> str: ...
    def should_use_colors(self) -> bool: ...
    def formatMessage(self, record: logging.LogRecord) -> str: ...

class DefaultFormatter(ColourizedFormatter):
    def should_use_colors(self) -> bool: ...

class AccessFormatter(ColourizedFormatter):
    status_code_colours: Incomplete
    def get_status_code(self, status_code: int) -> str: ...
    def formatMessage(self, record: logging.LogRecord) -> str: ...
