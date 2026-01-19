from io import StringIO

import pytest

pytestmark = pytest.mark.unit

from models.rdf_builder.writers.turtle import TurtleWriter


class TestTurtleWriter:
    def test_init(self):
        output = StringIO()
        writer = TurtleWriter(output, buffer_size=1024)
        assert writer.output == output
        assert writer.buffer_size == 1024
        assert writer._buffer == []
        assert writer._buffer_len == 0

    def test_write_header(self):
        output = StringIO()
        writer = TurtleWriter(output)
        writer.write_header()
        # Check that prefixes were written
        content = output.getvalue()
        assert "@prefix" in content  # TURTLE_PREFIXES contains prefixes

    def test_write_no_flush(self):
        output = StringIO()
        writer = TurtleWriter(output, buffer_size=100)
        writer.write("test text")
        assert writer._buffer == ["test text"]
        assert writer._buffer_len == 9
        assert output.getvalue() == ""  # Not flushed yet

    def test_write_with_flush(self):
        output = StringIO()
        writer = TurtleWriter(output, buffer_size=5)
        writer.write("long text")  # len=9 > 5, should flush
        assert writer._buffer == []
        assert writer._buffer_len == 0
        assert output.getvalue() == "long text"

    def test_flush(self):
        output = StringIO()
        writer = TurtleWriter(output)
        writer.write("test")
        writer.flush()
        assert writer._buffer == []
        assert writer._buffer_len == 0
        assert output.getvalue() == "test"

    def test_flush_empty(self):
        output = StringIO()
        writer = TurtleWriter(output)
        writer.flush()  # No-op
        assert output.getvalue() == ""

    def test_multiple_writes_and_flush(self):
        output = StringIO()
        writer = TurtleWriter(output, buffer_size=20)
        writer.write("line1")
        writer.write("line2")
        assert output.getvalue() == ""
        writer.flush()
        assert output.getvalue() == "line1line2"
