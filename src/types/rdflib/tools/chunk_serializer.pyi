from pathlib import Path
from rdflib.graph import Graph

__all__ = ["serialize_in_chunks"]

def serialize_in_chunks(
    g: Graph,
    max_triples: int = 10000,
    max_file_size_kb: int | None = None,
    file_name_stem: str = "chunk",
    output_dir: Path | None = None,
    write_prefixes: bool = False,
) -> None: ...
