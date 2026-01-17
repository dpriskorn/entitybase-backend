__all__ = ["sparqlquery"]

class _ArgumentError(Exception): ...
class _PrintHelpError(Exception): ...
class InvalidQueryError(Exception): ...

def sparqlquery(
    endpoints: list[str],
    query: str,
    result_format: str | None = None,
    result_keywords: dict[str, str] = {},
    auth: tuple[str, str] | None = None,
    use_stdin: bool = False,
    remote_storetype: str | None = None,
): ...
