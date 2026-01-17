import pytest

pytestmark = pytest.mark.unit

from models.rdf_builder.ontology.wikibase import wikibase_predicates


class TestWikibasePredicates:
    def test_wikibase_predicates_standard_property(self):
        """Test wikibase_predicates for a standard property ID."""
        result = wikibase_predicates("P31")
        assert result.direct == "wdt:P31"
        assert result.statement == "ps:P31"
        assert result.statement_value == "ps:P31"
        assert result.qualifier == "pq:P31"
        assert result.reference == "pr:P31"
        assert result.statement_value_node == "psv:P31"

    def test_wikibase_predicates_different_pid(self):
        """Test wikibase_predicates with different property ID."""
        result = wikibase_predicates("P123")
        assert result.direct == "wdt:P123"
        assert result.statement == "ps:P123"
        assert result.statement_value == "ps:P123"
        assert result.qualifier == "pq:P123"
        assert result.reference == "pr:P123"
        assert result.statement_value_node == "psv:P123"

    def test_wikibase_predicates_numeric_pid(self):
        """Test wikibase_predicates with numeric property ID."""
        result = wikibase_predicates("123")
        assert result.direct == "wdt:123"
        assert result.statement == "ps:123"
        assert result.statement_value == "ps:123"
        assert result.qualifier == "pq:123"
        assert result.reference == "pr:123"
        assert result.statement_value_node == "psv:123"