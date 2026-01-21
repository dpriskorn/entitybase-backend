from io import StringIO

import pytest

pytestmark = pytest.mark.unit

from models.rdf_builder.writers.turtle import TurtleWriter


class TestTurtleWriter:
    def test_init(self) -> None:
        output = StringIO()
        writer = TurtleWriter(output=output, buffer_size=1024)
        assert writer.output == output
        assert writer.buffer_size == 1024
        assert writer.buffer == []
        assert writer.buffer_len == 0

    def test_write_header(self) -> None:
        output = StringIO()
        writer = TurtleWriter(output=output)
        writer.write_header()
        # Check that prefixes were written
        content = output.getvalue()
        assert "@prefix" in content  # TURTLE_PREFIXES contains prefixes

    def test_write_no_flush(self) -> None:
        output = StringIO()
        writer = TurtleWriter(output=output, buffer_size=100)
        writer.write("test text")
        assert writer.buffer == ["test text"]
        assert writer.buffer_len == 9
        assert output.getvalue() == ""  # Not flushed yet

    def test_write_with_flush(self) -> None:
        output = StringIO()
        writer = TurtleWriter(output=output, buffer_size=5)
        writer.write("long text")  # len=9 > 5, should flush
        assert writer.buffer == []
        assert writer.buffer_len == 0
        assert output.getvalue() == "long text"

    def test_flush(self) -> None:
        output = StringIO()
        writer = TurtleWriter(output=output)
        writer.write("test")
        writer.flush()
        assert writer.buffer == []
        assert writer.buffer_len == 0
        assert output.getvalue() == "test"

    def test_flush_empty(self) -> None:
        output = StringIO()
        writer = TurtleWriter(output=output)
        writer.flush()  # No-op
        assert output.getvalue() == ""

    def test_multiple_writes_and_flush(self) -> None:
        output = StringIO()
        writer = TurtleWriter(output=output, buffer_size=20)
        writer.write("line1")
        writer.write("line2")
        assert output.getvalue() == ""
        writer.flush()
        assert output.getvalue() == "line1line2"
