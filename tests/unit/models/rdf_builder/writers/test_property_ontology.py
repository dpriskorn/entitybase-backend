"""Unit tests for property_ontology."""

import io
from unittest.mock import patch

from models.rdf_builder.property_registry.models import PropertyShape, PropertyPredicates
from models.rdf_builder.writers.property_ontology import PropertyOntologyWriter


class TestPropertyOntologyWriter:
    """Unit tests for PropertyOntologyWriter."""

    def test_write_property_metadata_basic(self) -> None:
        """Test writing basic property metadata."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                reference="pr:P31"
            ),
            labels={"en": {"value": "instance of"}},
            descriptions={"en": {"value": "that class of which this subject is a particular example and member"}}
        )

        PropertyOntologyWriter.write_property_metadata(output, shape)

        result = output.getvalue()
        assert "wd:P31 a wikibase:Property ;" in result
        assert 'rdfs:label "instance of"@en ;' in result
        assert 'schema:name "instance of"@en ;' in result
        assert 'schema:description "that class of which this subject is a particular example and member"@en ;' in result
        assert "wikibase:propertyType <http://wikiba.se/ontology#WikibaseItem> ;" in result
        assert "wikibase:directClaim wdt:P31 ;" in result
        assert "wikibase:claim p:P31 ;" in result
        assert "wikibase:statementProperty ps:P31 ;" in result
        assert "wikibase:qualifier pq:P31 ;" in result
        assert "wikibase:reference pr:P31 ;" in result
        assert "wikibase:novalue wdno:P31 ." in result

    def test_write_property_metadata_with_value_node(self) -> None:
        """Test writing property metadata with value node predicate."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P569",
            datatype="time",
            predicates=PropertyPredicates(
                direct="wdt:P569",
                statement="ps:P569",
                qualifier="pq:P569",
                reference="pr:P569",
                value_node="psv:P569"
            )
        )

        PropertyOntologyWriter.write_property_metadata(output, shape)

        result = output.getvalue()
        assert "wikibase:statementValue psv:P569 ;" in result
        assert "wikibase:qualifierValue pqv:P569 ;" in result
        assert "wikibase:referenceValue prv:P569 ;" in result

    def test_write_property_metadata_with_normalized_predicates(self) -> None:
        """Test writing property metadata with normalized predicates."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P625",
            datatype="globe-coordinate",
            predicates=PropertyPredicates(
                direct="wdt:P625",
                statement="ps:P625",
                qualifier="pq:P625",
                reference="pr:P625",
                statement_normalized="psn:P625",
                qualifier_normalized="pqn:P625",
                reference_normalized="prn:P625",
                direct_normalized="wdtn:P625"
            )
        )

        PropertyOntologyWriter.write_property_metadata(output, shape)

        result = output.getvalue()
        assert "wikibase:statementValueNormalized psn:P625 ;" in result
        assert "wikibase:qualifierValueNormalized pqn:P625 ;" in result
        assert "wikibase:referenceValueNormalized prn:P625 ;" in result
        assert "wikibase:directClaimNormalized wdtn:P625 ;" in result

    def test_write_property_metadata_multilingual(self) -> None:
        """Test writing property metadata with multiple languages."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P1476",
            datatype="monolingualtext",
            predicates=PropertyPredicates(
                direct="wdt:P1476",
                statement="ps:P1476",
                qualifier="pq:P1476",
                reference="pr:P1476"
            ),
            labels={
                "en": {"value": "title"},
                "de": {"value": "Titel"},
                "fr": {"value": "titre"}
            },
            descriptions={
                "en": {"value": "title of a creative work"},
                "de": {"value": "Titel eines Werks"}
            }
        )

        PropertyOntologyWriter.write_property_metadata(output, shape)

        result = output.getvalue()
        assert 'rdfs:label "title"@en ;' in result
        assert 'rdfs:label "Titel"@de ;' in result
        assert 'rdfs:label "titre"@fr ;' in result
        assert 'schema:description "title of a creative work"@en ;' in result
        assert 'schema:description "Titel eines Werks"@de ;' in result

    def test_datatype_uri_mapping(self) -> None:
        """Test datatype URI mapping for various datatypes."""
        test_cases = [
            ("wikibase-item", "http://wikiba.se/ontology#WikibaseItem"),
            ("string", "http://wikiba.se/ontology#String"),
            ("external-id", "http://wikiba.se/ontology#ExternalId"),
            ("time", "http://wikiba.se/ontology#Time"),
            ("quantity", "http://wikiba.se/ontology#Quantity"),
            ("url", "http://wikiba.se/ontology#Url"),
            ("math", "http://wikiba.se/ontology#Math"),
            ("geo-shape", "http://wikiba.se/ontology#GeoShape"),
            ("tabular-data", "http://wikiba.se/ontology#TabularData"),
            ("unknown", "http://wikiba.se/ontology#String"),  # Default fallback
        ]

        for datatype, expected_uri in test_cases:
            result = PropertyOntologyWriter._datatype_uri(datatype)
            assert result == expected_uri

    def test_datatype_uri_case_insensitive(self) -> None:
        """Test that datatype URI mapping handles case variations."""
        assert PropertyOntologyWriter._datatype_uri("commonsMedia") == "http://wikiba.se/ontology#CommonsMedia"
        assert PropertyOntologyWriter._datatype_uri("globe-coordinate") == "http://wikiba.se/ontology#Globecoordinate"
        assert PropertyOntologyWriter._datatype_uri("tabulardata") == "http://wikiba.se/ontology#TabularData"

    def test_write_property_basic(self) -> None:
        """Test writing basic property ontology."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                reference="pr:P31"
            )
        )

        PropertyOntologyWriter.write_property(output, shape)

        result = output.getvalue()
        assert "p:P31 a owl:ObjectProperty ." in result
        assert "psv:P31 a owl:ObjectProperty ." in result
        assert "pqv:P31 a owl:ObjectProperty ." in result
        assert "prv:P31 a owl:ObjectProperty ." in result
        assert "wdt:P31 a owl:ObjectProperty ." in result  # item type -> ObjectProperty
        assert "ps:P31 a owl:ObjectProperty ." in result
        assert "pq:P31 a owl:ObjectProperty ." in result
        assert "pr:P31 a owl:ObjectProperty ." in result

    def test_write_property_with_normalized_predicates(self) -> None:
        """Test writing property ontology with normalized predicates."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P625",
            datatype="globe-coordinate",
            predicates=PropertyPredicates(
                direct="wdt:P625",
                statement="ps:P625",
                qualifier="pq:P625",
                reference="pr:P625",
                statement_normalized="psn:P625",
                qualifier_normalized="pqn:P625",
                reference_normalized="prn:P625",
                direct_normalized="wdtn:P625"
            )
        )

        PropertyOntologyWriter.write_property(output, shape)

        result = output.getvalue()
        assert "psn:P625 a owl:ObjectProperty ." in result
        assert "pqn:P625 a owl:ObjectProperty ." in result
        assert "prn:P625 a owl:ObjectProperty ." in result
        assert "wdtn:P625 a owl:ObjectProperty ." in result

    def test_write_property_metadata_empty_labels_descriptions(self) -> None:
        """Test writing property metadata with empty labels and descriptions."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P123",
            datatype="string",
            predicates=PropertyPredicates(
                direct="wdt:P123",
                statement="ps:P123",
                qualifier="pq:P123",
                reference="pr:P123"
            ),
            labels={},
            descriptions={}
        )

        PropertyOntologyWriter.write_property_metadata(output, shape)

        result = output.getvalue()
        # Should not have any label or description triples
        assert "rdfs:label" not in result
        assert "schema:description" not in result
        assert "wikibase:propertyType <http://wikiba.se/ontology#String> ;" in result

    def test_write_property_metadata_special_characters(self) -> None:
        """Test writing property metadata with special characters in labels."""
        output = io.StringIO()
        shape = PropertyShape(
            pid="P1476",
            datatype="monolingualtext",
            predicates=PropertyPredicates(
                direct="wdt:P1476",
                statement="ps:P1476",
                qualifier="pq:P1476",
                reference="pr:P1476"
            ),
            labels={"en": {"value": 'Title with "quotes" and émojis 🎭'}}
        )

        PropertyOntologyWriter.write_property_metadata(output, shape)

        result = output.getvalue()
        # Special characters should be preserved (RDF handles escaping)
        assert 'rdfs:label "Title with "quotes" and émojis 🎭"@en ;' in result

    def test_write_property_different_property_ids(self) -> None:
        """Test writing properties with different ID formats."""
        test_cases = ["P1", "P123", "P12345"]

        for pid in test_cases:
            output = io.StringIO()
            shape = PropertyShape(
                pid=pid,
                datatype="wikibase-item",
                predicates=PropertyPredicates(
                    direct=f"wdt:{pid}",
                    statement=f"ps:{pid}",
                    qualifier=f"pq:{pid}",
                    reference=f"pr:{pid}"
                )
            )

            PropertyOntologyWriter.write_property(output, shape)
            result = output.getvalue()

            assert f"p:{pid} a owl:ObjectProperty ." in result
            assert f"wdt:{pid} a owl:ObjectProperty ." in result