import pytest

pytestmark = pytest.mark.unit

from models.rdf_builder.writers.prefixes import TURTLE_PREFIXES


class TestTurtlePrefixes:
    def test_turtle_prefixes_contains_standard_prefixes(self) -> None:
        """Test that TURTLE_PREFIXES contains expected RDF prefixes."""
        assert "@prefix rdf:" in TURTLE_PREFIXES
        assert "@prefix xsd:" in TURTLE_PREFIXES
        assert "@prefix wikibase:" in TURTLE_PREFIXES
        assert "@prefix wd:" in TURTLE_PREFIXES
        assert "@prefix wdt:" in TURTLE_PREFIXES
        assert "@prefix p:" in TURTLE_PREFIXES
        assert "@prefix ps:" in TURTLE_PREFIXES
        assert "@prefix pq:" in TURTLE_PREFIXES
        assert "@prefix pr:" in TURTLE_PREFIXES

    def test_turtle_prefixes_format(self) -> None:
        """Test that TURTLE_PREFIXES is properly formatted."""
        lines = TURTLE_PREFIXES.strip().split("\n")
        for line in lines:
            assert line.startswith("@prefix ")
            assert line.endswith(" .")
            assert "<" in line and ">" in line

    def test_turtle_prefixes_no_duplicates(self) -> None:
        """Test that there are no duplicate prefixes."""
        lines = TURTLE_PREFIXES.strip().split("\n")
        prefixes = [line.split(":")[0] for line in lines]
        assert len(prefixes) == len(set(prefixes))
