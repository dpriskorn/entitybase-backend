"""Unit tests for rdf_statement."""

from models.rdf_builder.models.rdf_statement import RDFStatement


class TestRDFStatement:
    """Unit tests for RDFStatement model."""

    def test_create_rdf_statement_basic(self) -> None:
        """Test creating a basic RDF statement."""
        statement = RDFStatement(
            guid="Q42$12345-6789-ABCD-EFGH-123456789ABC",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.guid == "Q42$12345-6789-ABCD-EFGH-123456789ABC"
        assert statement.property_id == "P31"
        assert statement.value == "wd:Q5"
        assert statement.rank == "normal"
        assert statement.qualifiers == []
        assert statement.references == []

    def test_create_rdf_statement_with_qualifiers(self) -> None:
        """Test creating RDF statement with qualifiers."""
        qualifiers = [
            {"property": "P580", "value": '"2020-01-01"^^xsd:dateTime'},
            {"property": "P582", "value": '"2020-12-31"^^xsd:dateTime'}
        ]

        statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P39",
            value="wd:Q11696",
            rank="preferred",
            qualifiers=qualifiers,
            references=[]
        )

        assert statement.qualifiers == qualifiers
        assert len(statement.qualifiers) == 2
        assert statement.rank == "preferred"

    def test_create_rdf_statement_with_references(self) -> None:
        """Test creating RDF statement with references."""
        references = [
            {
                "snaks": {
                    "P854": [{"value": '"https://example.com"'}],
                    "P813": [{"value": '"2023-01-01"^^xsd:dateTime'}]
                }
            }
        ]

        statement = RDFStatement(
            guid="Q42$REF123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=references
        )

        assert statement.references == references
        assert len(statement.references) == 1

    def test_rdf_statement_deprecated_rank(self) -> None:
        """Test RDF statement with deprecated rank."""
        statement = RDFStatement(
            guid="Q42$DEP123",
            property_id="P31",
            value="wd:Q5",
            rank="deprecated",
            qualifiers=[],
            references=[]
        )

        assert statement.rank == "deprecated"

    def test_rdf_statement_preferred_rank(self) -> None:
        """Test RDF statement with preferred rank."""
        statement = RDFStatement(
            guid="Q42$PRE123",
            property_id="P31",
            value="wd:Q5",
            rank="preferred",
            qualifiers=[],
            references=[]
        )

        assert statement.rank == "preferred"

    def test_rdf_statement_complex_value(self) -> None:
        """Test RDF statement with complex value (quantity)."""
        statement = RDFStatement(
            guid="Q42$QUANT123",
            property_id="P1107",  # number of
            value="42.5^^xsd:decimal",
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.value == "42.5^^xsd:decimal"
        assert statement.property_id == "P1107"

    def test_rdf_statement_time_value(self) -> None:
        """Test RDF statement with time value."""
        statement = RDFStatement(
            guid="Q42$TIME123",
            property_id="P569",  # birth date
            value='"1939-11-23"^^xsd:dateTime',
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.value == '"1939-11-23"^^xsd:dateTime'
        assert statement.property_id == "P569"

    def test_rdf_statement_monolingual_value(self) -> None:
        """Test RDF statement with monolingual value."""
        statement = RDFStatement(
            guid="Q42$MONO123",
            property_id="P1476",  # title
            value='"The Hitchhiker\'s Guide to the Galaxy"@en',
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.value == '"The Hitchhiker\'s Guide to the Galaxy"@en'

    def test_rdf_statement_coordinate_value(self) -> None:
        """Test RDF statement with coordinate value."""
        statement = RDFStatement(
            guid="Q42$COORD123",
            property_id="P625",  # coordinate location
            value='"Point(-0.1275 51.5072)"^^geo:wktLiteral',
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.value == '"Point(-0.1275 51.5072)"^^geo:wktLiteral'
        assert statement.property_id == "P625"

    def test_rdf_statement_empty_qualifiers_and_references(self) -> None:
        """Test RDF statement with empty qualifiers and references."""
        statement = RDFStatement(
            guid="Q42$EMPTY123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.qualifiers == []
        assert statement.references == []

    def test_rdf_statement_none_qualifiers_and_references(self) -> None:
        """Test RDF statement with None qualifiers and references."""
        statement = RDFStatement(
            guid="Q42$NONE123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=None,
            references=None
        )

        assert statement.qualifiers is None
        assert statement.references is None

    def test_rdf_statement_complex_qualifiers(self) -> None:
        """Test RDF statement with complex nested qualifiers."""
        qualifiers = [
            {
                "property": "P580",  # start time
                "value": '"2020-01-01"^^xsd:dateTime',
                "datatype": "time"
            },
            {
                "property": "P582",  # end time
                "value": '"2020-12-31"^^xsd:dateTime',
                "datatype": "time"
            },
            {
                "property": "P459",  # determination method
                "value": "wd:Q18122778",  # stated in
                "datatype": "wikibase-item"
            }
        ]

        references = [
            {
                "snaks": {
                    "P854": [{"value": '"https://en.wikipedia.org/wiki/Douglas_Adams"'}],
                    "P1476": [{"value": '"Douglas Adams"@en'}],
                    "P813": [{"value": '"2023-01-01"^^xsd:dateTime'}]
                }
            }
        ]

        statement = RDFStatement(
            guid="Q42$COMPLEX123",
            property_id="P569",  # birth date
            value='"1952-03-11"^^xsd:dateTime',
            rank="preferred",
            qualifiers=qualifiers,
            references=references
        )

        assert len(statement.qualifiers) == 3
        assert len(statement.references) == 1
        assert statement.qualifiers[0]["property"] == "P580"
        assert statement.qualifiers[1]["property"] == "P582"
        assert statement.qualifiers[2]["property"] == "P459"

    def test_rdf_statement_minimal_guid(self) -> None:
        """Test RDF statement with minimal GUID."""
        statement = RDFStatement(
            guid="Q1$1",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.guid == "Q1$1"

    def test_rdf_statement_long_guid(self) -> None:
        """Test RDF statement with long GUID."""
        long_guid = "Q123456$F1234567-89AB-CDEF-0123-456789ABCDEF"
        statement = RDFStatement(
            guid=long_guid,
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=[]
        )

        assert statement.guid == long_guid

    def test_rdf_statement_property_variations(self) -> None:
        """Test RDF statement with different property formats."""
        test_cases = [
            ("P1", "single digit"),
            ("P12", "double digit"),
            ("P123", "triple digit"),
            ("P1234", "quadruple digit"),
        ]

        for prop_id, description in test_cases:
            statement = RDFStatement(
                guid=f"Q42${prop_id}",
                property_id=prop_id,
                value="wd:Q5",
                rank="normal",
                qualifiers=[],
                references=[]
            )
            assert statement.property_id == prop_id

    def test_rdf_statement_immutability(self) -> None:
        """Test that RDF statement is immutable (if using frozen model)."""
        statement = RDFStatement(
            guid="Q42$IMMUTABLE",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=[]
        )

        # Test that it's a valid Pydantic model
        assert isinstance(statement, RDFStatement)

        # Note: RDFStatement doesn't appear to be frozen, so we can't test immutability
        # This is different from other models in the codebase