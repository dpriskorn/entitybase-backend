"""RDF Turtle writer."""
from io import StringIO
from typing import TextIO

from pydantic import BaseModel, ConfigDict

from models.rdf_builder.writers.prefixes import TURTLE_PREFIXES


class TurtleWriter(BaseModel):
    """Buffered Turtle writer for efficient output."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    output: TextIO | StringIO
    buffer_size: int = 8192

    def model_post_init(self, context):
        self.buffer = []
        self.buffer_len = 0

    def write_header(self) -> None:
        """Write Turtle prefixes."""
        self._write(TURTLE_PREFIXES)

    def write(self, text: str) -> None:
        """Write text to buffer."""
        self.buffer.append(text)
        self.buffer_len += len(text)

        if self.buffer_len >= self.buffer_size:
            self.output.write("".join(self.buffer))
            self.buffer = []
            self.buffer_len = 0
            self.output.flush()

    def _write(self, text: str) -> None:
        self.output.write(text)
