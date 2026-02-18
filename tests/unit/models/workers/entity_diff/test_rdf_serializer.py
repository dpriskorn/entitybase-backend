"""Unit tests for rdf_serializer."""

import pytest
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS


class TestRDFSerializer:
    """Test RDFSerializer class."""

    def test_entity_data_to_rdf_with_item(self):
        """Test converting entity data with type 'item' to RDF."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"value": "Douglas Adams"}},
            "descriptions": {"en": {"value": "English writer"}},
            "claims": {},
        }

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "http://www.wikidata.org/entity/Q42" in result
        assert "http://www.wikidata.org/entity/Q35120" in result
        assert "Douglas Adams" in result

    def test_entity_data_to_rdf_with_property(self):
        """Test converting entity data with type 'property' to RDF."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {
            "id": "P31",
            "type": "property",
            "labels": {"en": {"value": "instance of"}},
            "descriptions": {},
            "claims": {},
        }

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "http://www.wikidata.org/entity/P31" in result
        assert "http://www.wikidata.org/entity/Q18616576" in result

    def test_entity_data_to_rdf_with_labels(self):
        """Test that labels are properly added to RDF."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {
            "id": "Q1",
            "type": "item",
            "labels": {
                "en": {"value": "Universe"},
                "fr": {"value": "Univers"},
                "de": {"value": "Universum"},
            },
            "descriptions": {},
            "claims": {},
        }

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "@en" in result or '"Universe"' in result
        assert "@fr" in result or '"Univers"' in result
        assert "@de" in result or '"Universum"' in result

    def test_entity_data_to_rdf_with_descriptions(self):
        """Test that descriptions are properly added to RDF."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {
            "id": "Q1",
            "type": "item",
            "labels": {},
            "descriptions": {"en": {"value": "Everything that exists"}},
            "claims": {},
        }

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "Everything that exists" in result
        assert "description" in result

    def test_entity_data_to_rdf_with_string_claims(self):
        """Test that string claims are properly added to RDF."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {
            "id": "Q42",
            "type": "item",
            "labels": {},
            "descriptions": {},
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "datavalue": {
                                "type": "string",
                                "value": "test value",
                            },
                        }
                    }
                ]
            },
        }

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "test value" in result
        assert "P31" in result

    def test_entity_data_to_rdf_ignores_non_string_claims(self):
        """Test that non-string claims are ignored."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {
            "id": "Q42",
            "type": "item",
            "labels": {},
            "descriptions": {},
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "datavalue": {
                                "type": "wikibase-entityid",
                                "value": {"id": "Q5"},
                            },
                        }
                    }
                ]
            },
        }

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "Q5" not in result

    def test_entity_data_to_rdf_ignores_non_value_snaks(self):
        """Test that non-value snaks are ignored."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {
            "id": "Q42",
            "type": "item",
            "labels": {},
            "descriptions": {},
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "novalue",
                        }
                    }
                ]
            },
        }

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "novalue" not in result

    def test_entity_data_to_rdf_empty_data(self):
        """Test converting empty entity data to RDF."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        entity_data = {"id": "Q1", "type": "item"}

        result = RDFSerializer.entity_data_to_rdf(entity_data, "turtle")

        assert "http://www.wikidata.org/entity/Q1" in result
        assert "http://www.wikidata.org/entity/Q35120" in result

    def test_add_entity_type_item(self):
        """Test _add_entity_type with item type."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")

        RDFSerializer._add_entity_type(g, entity_uri, "item")

        triples = list(g.triples((entity_uri, RDF.type, None)))
        assert len(triples) == 1
        assert str(triples[0][2]) == "http://www.wikidata.org/entity/Q35120"

    def test_add_entity_type_property(self):
        """Test _add_entity_type with property type."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/P31")

        RDFSerializer._add_entity_type(g, entity_uri, "property")

        triples = list(g.triples((entity_uri, RDF.type, None)))
        assert len(triples) == 1
        assert str(triples[0][2]) == "http://www.wikidata.org/entity/Q18616576"

    def test_add_entity_type_unknown(self):
        """Test _add_entity_type with unknown type."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")

        RDFSerializer._add_entity_type(g, entity_uri, "unknown")

        triples = list(g.triples((entity_uri, RDF.type, None)))
        assert len(triples) == 0

    def test_add_labels(self):
        """Test _add_labels method."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")
        labels = {
            "en": {"value": "Douglas Adams"},
            "fr": {"value": "Douglas Adams"},
        }

        RDFSerializer._add_labels(g, entity_uri, labels)

        triples = list(g.triples((entity_uri, RDFS.label, None)))
        assert len(triples) == 2

    def test_add_labels_with_invalid_data(self):
        """Test _add_labels with invalid label data."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")
        labels = {
            "en": "not a dict",
            "de": {"no_value_key": "test"},
        }

        RDFSerializer._add_labels(g, entity_uri, labels)

        triples = list(g.triples((entity_uri, RDFS.label, None)))
        assert len(triples) == 0

    def test_add_descriptions(self):
        """Test _add_descriptions method."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")
        descriptions = {
            "en": {"value": "English writer and humorist"},
            "fr": {"value": "Écrivain anglais"},
        }

        RDFSerializer._add_descriptions(g, entity_uri, descriptions)

        triples = list(
            g.triples((entity_uri, URIRef("http://schema.org/description"), None))
        )
        assert len(triples) == 2

    def test_add_descriptions_with_invalid_data(self):
        """Test _add_descriptions with invalid data."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")
        descriptions = {
            "en": "not a dict",
            "de": {"no_value_key": "test"},
        }

        RDFSerializer._add_descriptions(g, entity_uri, descriptions)

        triples = list(
            g.triples((entity_uri, URIRef("http://schema.org/description"), None))
        )
        assert len(triples) == 0

    def test_add_statements(self):
        """Test _add_statements method with string values."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")
        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "datavalue": {
                            "type": "string",
                            "value": "human",
                        },
                    }
                }
            ]
        }

        RDFSerializer._add_statements(g, entity_uri, claims)

        assert len(list(g.triples((None, None, Literal("human"))))) > 0

    def test_add_statements_ignores_non_string(self):
        """Test _add_statements ignores non-string datavalues."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")
        claims = {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "datavalue": {
                            "type": "wikibase-entityid",
                            "value": {"id": "Q5"},
                        },
                    }
                }
            ]
        }

        RDFSerializer._add_statements(g, entity_uri, claims)

        assert len(list(g)) == 0

    def test_add_statements_with_empty_claims(self):
        """Test _add_statements with empty claims."""
        from models.workers.entity_diff.rdf_serializer import RDFSerializer

        g = Graph()
        entity_uri = URIRef("http://www.wikidata.org/entity/Q42")

        RDFSerializer._add_statements(g, entity_uri, {})

        assert len(list(g)) == 0
