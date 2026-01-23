"""Unit tests for converter."""

import io
from unittest.mock import MagicMock, patch

import pytest

from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.registry import PropertyRegistry


class TestEntityConverter:
    """Unit tests for EntityConverter."""

    def test_converter_initialization(self) -> None:
        """Test EntityConverter initialization."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        assert converter.property_registry == property_registry
        assert converter.writers is not None
        assert converter.uri is not None

    def test_converter_with_custom_params(self) -> None:
        """Test EntityConverter with custom parameters."""
        property_registry = PropertyRegistry(properties={})
        mock_metadata_dir = MagicMock()
        mock_redirects_dir = MagicMock()

        converter = EntityConverter(
            property_registry=property_registry,
            entity_metadata_dir=mock_metadata_dir,
            redirects_dir=mock_redirects_dir
        )

        assert converter.property_registry == property_registry
        assert converter.entity_metadata_dir == mock_metadata_dir
        assert converter.redirects_dir == mock_redirects_dir

    @patch('models.rdf_builder.converter.TripleWriters.write_header')
    def test_convert_to_turtle_basic(self, mock_write_header) -> None:
        """Test basic Turtle conversion."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        # Mock entity with minimal data
        mock_entity = MagicMock()
        mock_entity.id = "Q42"

        output = io.StringIO()

        # Mock all the conversion methods
        with patch.object(converter, '_write_entity_metadata') as mock_write_entity, \
             patch.object(converter, '_write_statements') as mock_write_statements, \
             patch.object(converter, '_write_redirects') as mock_write_redirects, \
             patch.object(converter, '_write_referenced_entity_metadata') as mock_write_refs, \
             patch.object(converter, '_write_property_metadata') as mock_write_props:

            converter.convert_to_turtle(mock_entity, output)

            # Verify header was written
            mock_write_header.assert_called_once_with(output)

            # Verify all conversion methods were called
            mock_write_entity.assert_called_once_with(mock_entity, output)
            mock_write_statements.assert_called_once_with(mock_entity, output)
            mock_write_redirects.assert_called_once_with(mock_entity, output)
            mock_write_refs.assert_called_once_with(mock_entity, output)
            mock_write_props.assert_called_once_with(mock_entity, output)

    def test_write_entity_metadata(self) -> None:
        """Test writing entity metadata."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()

        # Mock entity with labels and descriptions
        mock_entity = MagicMock()
        mock_entity.id = "Q42"

        mock_labels = MagicMock()
        mock_labels.data = {
            "en": MagicMock(value="Test Entity"),
            "de": MagicMock(value="Test Entität")
        }
        mock_entity.labels = mock_labels

        mock_descriptions = MagicMock()
        mock_descriptions.data = {
            "en": MagicMock(value="A test entity")
        }
        mock_entity.descriptions = mock_descriptions

        mock_entity.aliases = MagicMock(data={})
        mock_entity.sitelinks = None

        converter._write_entity_metadata(mock_entity, output)

        result = output.getvalue()
        assert "wd:Q42 a wikibase:Item ." in result
        assert 'wd:Q42 rdfs:label "Test Entity"@en .' in result
        assert 'wd:Q42 rdfs:label "Test Entität"@de .' in result
        assert 'wd:Q42 schema:description "A test entity"@en .' in result

    def test_write_entity_metadata_with_sitelinks(self) -> None:
        """Test writing entity metadata with sitelinks."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()

        mock_entity = MagicMock()
        mock_entity.id = "Q42"
        mock_entity.labels = MagicMock(data={})
        mock_entity.descriptions = MagicMock(data={})
        mock_entity.aliases = MagicMock(data={})

        mock_sitelinks = MagicMock()
        mock_sitelinks.data = {"enwiki": {"site": "enwiki", "title": "Test Page"}}
        mock_entity.sitelinks = mock_sitelinks

        converter._write_entity_metadata(mock_entity, output)

        result = output.getvalue()
        assert "wd:Q42 schema:sameAs <https://enwiki.wikipedia.org/wiki/Test_Page> ." in result

    def test_write_entity_metadata_with_aliases(self) -> None:
        """Test writing entity metadata with aliases."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()

        mock_entity = MagicMock()
        mock_entity.id = "Q42"
        mock_entity.labels = MagicMock(data={})
        mock_entity.descriptions = MagicMock(data={})
        mock_entity.sitelinks = None

        mock_aliases = MagicMock()
        mock_aliases.data = {
            "en": [MagicMock(value="Test"), MagicMock(value="Example")]
        }
        mock_entity.aliases = mock_aliases

        converter._write_entity_metadata(mock_entity, output)

        result = output.getvalue()
        assert 'wd:Q42 skos:altLabel "Test"@en .' in result
        assert 'wd:Q42 skos:altLabel "Example"@en .' in result

    @patch('models.rdf_builder.converter.parse_statement')
    def test_write_statements(self, mock_parse_statement) -> None:
        """Test writing statements."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()

        # Mock entity with statements
        mock_entity = MagicMock()
        mock_entity.id = "Q42"
        mock_entity.statements = MagicMock()
        mock_entity.statements.data = [
            {"mainsnak": {"property": "P31"}, "rank": "normal"},
            {"mainsnak": {"property": "P279"}, "rank": "preferred"}
        ]

        # Mock parsed statements
        mock_stmt1 = MagicMock()
        mock_stmt1.get_rdfstatement.return_value = MagicMock()
        mock_stmt2 = MagicMock()
        mock_stmt2.get_rdfstatement.return_value = MagicMock()

        mock_parse_statement.side_effect = [mock_stmt1, mock_stmt2]

        with patch.object(converter, '_write_statement') as mock_write_statement:
            converter._write_statements(mock_entity, output)

            # Verify statements were parsed and written
            assert mock_parse_statement.call_count == 2
            assert mock_write_statement.call_count == 2

            # Verify calls
            mock_write_statement.assert_any_call("Q42", mock_stmt1.get_rdfstatement.return_value, output)
            mock_write_statement.assert_any_call("Q42", mock_stmt2.get_rdfstatement.return_value, output)

    def test_write_statement(self) -> None:
        """Test writing individual statement."""
        property_registry = PropertyRegistry(properties={})
        mock_shape = MagicMock()
        property_registry.shape = mock_shape
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()

        # Mock RDF statement
        mock_rdf_stmt = MagicMock()
        mock_rdf_stmt.property_id = "P31"

        # Mock writers
        with patch.object(converter.writers, 'write_statement') as mock_write_statement:
            converter._write_statement("Q42", mock_rdf_stmt, output)

            # Verify property shape lookup
            property_registry.shape.assert_called_once_with("P31")

            # Verify statement writing
            mock_write_statement.assert_called_once_with(
                output, "Q42", mock_rdf_stmt, mock_shape, property_registry, None
            )

    def test_write_property_metadata(self) -> None:
        """Test writing property metadata."""
        property_registry = PropertyRegistry(properties={})
        property_registry.shape = MagicMock()
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()

        # Mock entity with statements
        mock_entity = MagicMock()
        mock_entity.statements = MagicMock()
        mock_entity.statements.data = [
            {"mainsnak": {"property": "P31"}, "qualifiers": {"P580": []}, "references": []},
            {"mainsnak": {"property": "P279"}, "qualifiers": {}, "references": []}
        ]

        # Mock parsed statements
        mock_stmt1 = MagicMock()
        mock_stmt1.property = "P31"
        mock_stmt1.qualifiers = [MagicMock(property="P580")]
        mock_stmt1.references = []

        mock_stmt2 = MagicMock()
        mock_stmt2.property = "P279"
        mock_stmt2.qualifiers = []
        mock_stmt2.references = []

        with patch('models.rdf_builder.converter.parse_statement') as mock_parse, \
             patch('models.rdf_builder.converter.PropertyOntologyWriter') as mock_writer:

            mock_parse.side_effect = [mock_stmt1, mock_stmt2]

            converter._write_property_metadata(mock_entity, output)

            # Verify property shape lookups
            assert property_registry.shape.call_count == 2
            property_registry.shape.assert_any_call("P31")
            property_registry.shape.assert_any_call("P279")
            property_registry.shape.assert_any_call("P580")

            # Verify ontology writing calls
            assert mock_writer.write_property_metadata.call_count == 2
            assert mock_writer.write_property.call_count == 2
            assert mock_writer.write_novalue_class.call_count == 2

    @patch('models.rdf_builder.converter.parse_statement')
    def test_collect_referenced_entities(self, mock_parse_statement) -> None:
        """Test collecting referenced entities."""
        # Mock entity with statements referencing other entities
        mock_entity = MagicMock()
        mock_entity.statements = MagicMock()
        mock_entity.statements.data = [
            {"mainsnak": {"property": "P31"}, "rank": "normal"}
        ]

        # Mock parsed statement with entity value
        mock_stmt = MagicMock()
        mock_stmt.value = MagicMock()
        mock_stmt.value.kind = "entity"
        mock_stmt.value.value = "Q5"
        mock_stmt.qualifiers = []
        mock_stmt.references = []

        mock_parse_statement.return_value = mock_stmt

        result = EntityConverter._collect_referenced_entities(mock_entity)

        assert result == {"Q5"}
        mock_parse_statement.assert_called_once()

    def test_collect_referenced_entities_qualifiers(self) -> None:
        """Test collecting referenced entities from qualifiers."""
        with patch('models.rdf_builder.converter.parse_statement') as mock_parse:
            mock_entity = MagicMock()
            mock_entity.statements = MagicMock()
            mock_entity.statements.data = [{"mainsnak": {"property": "P31"}}]

            mock_stmt = MagicMock()
            mock_stmt.value = MagicMock()
            mock_stmt.value.kind = "string"  # Not entity
            mock_stmt.qualifiers = [
                MagicMock(property="P580", value=MagicMock(kind="entity", value="Q1985727"))
            ]
            mock_stmt.references = []

            mock_parse.return_value = mock_stmt

            result = EntityConverter._collect_referenced_entities(mock_entity)

            assert result == {"Q1985727"}

    def test_collect_referenced_entities_references(self) -> None:
        """Test collecting referenced entities from references."""
        with patch('models.rdf_builder.converter.parse_statement') as mock_parse:
            mock_entity = MagicMock()
            mock_entity.statements = MagicMock()
            mock_entity.statements.data = [{"mainsnak": {"property": "P31"}}]

            mock_ref_snak = MagicMock()
            mock_ref_snak.property = "P248"
            mock_ref_snak.value = MagicMock(kind="entity", value="Q123456")

            mock_ref = MagicMock()
            mock_ref.snaks = [mock_ref_snak]

            mock_stmt = MagicMock()
            mock_stmt.value = MagicMock(kind="string")
            mock_stmt.qualifiers = []
            mock_stmt.references = [mock_ref]

            mock_parse.return_value = mock_stmt

            result = EntityConverter._collect_referenced_entities(mock_entity)

            assert result == {"Q123456"}

    def test_converter_properties_property(self) -> None:
        """Test converter properties property."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        assert converter.properties == property_registry

    def test_converter_dedupe_property(self) -> None:
        """Test converter dedupe property."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry, enable_deduplication=True)

        dedupe = converter.dedupe
        assert dedupe is not None

    def test_converter_dedupe_disabled(self) -> None:
        """Test converter with deduplication disabled."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry, enable_deduplication=False)

        assert converter.dedupe is None

    @patch('models.json_parser.entity_parser.parse_entity')
    def test_load_referenced_entity_success(self, mock_parse_entity) -> None:
        """Test loading referenced entity successfully."""
        property_registry = PropertyRegistry(properties={})
        from pathlib import Path
        temp_dir = Path("/tmp/test")
        converter = EntityConverter(property_registry=property_registry, entity_metadata_dir=temp_dir)

        mock_entity_data = MagicMock()
        mock_parse_entity.return_value = mock_entity_data

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', new_callable=MagicMock) as mock_open, \
             patch('json.loads', return_value={"id": "Q5"}):

            result = converter._load_referenced_entity("Q5")

            assert result == mock_entity_data
            mock_parse_entity.assert_called_once_with({"id": "Q5"})

    def test_load_referenced_entity_no_metadata_dir(self) -> None:
        """Test loading referenced entity without metadata dir."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        with pytest.raises(ValueError, match="No entity_metadata_dir set"):
            converter._load_referenced_entity("Q5")

    def test_load_referenced_entity_file_not_found(self) -> None:
        """Test loading referenced entity when file doesn't exist."""
        property_registry = PropertyRegistry(properties={})
        from pathlib import Path
        temp_dir = Path("/tmp/test")
        converter = EntityConverter(property_registry=property_registry, entity_metadata_dir=temp_dir)

        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="Entity Q5 not found"):
                converter._load_referenced_entity("Q5")

    @patch('models.json_parser.entity_parser.parse_entity')
    def test_write_referenced_entity_metadata(self, mock_parse_entity) -> None:
        """Test writing referenced entity metadata."""
        property_registry = PropertyRegistry(properties={})
        from pathlib import Path
        temp_dir = Path("/tmp/test")
        converter = EntityConverter(property_registry=property_registry, entity_metadata_dir=temp_dir)

        output = io.StringIO()

        # Mock entity with referenced entities
        mock_entity = MagicMock()
        mock_entity.id = "Q42"

        # Mock statements with entity references
        with patch.object(converter, '_collect_referenced_entities', return_value={"Q5"}), \
             patch.object(converter, '_load_referenced_entity') as mock_load, \
             patch.object(converter.writers, 'write_entity_type') as mock_write_type, \
             patch.object(converter.writers, 'write_label') as mock_write_label, \
             patch.object(converter.writers, 'write_description') as mock_write_desc:

            mock_ref_entity = MagicMock()
            mock_ref_entity.id = "Q5"
            mock_ref_entity.labels = MagicMock(data={"en": MagicMock(value="Human")})
            mock_ref_entity.descriptions = MagicMock(data={})
            mock_load.return_value = mock_ref_entity

            converter._write_referenced_entity_metadata(mock_entity, output)

            mock_load.assert_called_once_with("Q5")
            mock_write_type.assert_called_once_with(output, "Q5")
            mock_write_label.assert_called_once_with(output, "Q5", "en", "Human")

    def test_write_referenced_entity_metadata_no_metadata_dir(self) -> None:
        """Test writing referenced entity metadata without metadata dir."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()
        mock_entity = MagicMock()

        # Should return early without error
        converter._write_referenced_entity_metadata(mock_entity, output)

    @patch('models.rdf_builder.converter.load_entity_redirects')
    def test_fetch_redirects_from_file(self, mock_load_redirects) -> None:
        """Test fetching redirects from file."""
        property_registry = PropertyRegistry(properties={})
        from pathlib import Path
        temp_dir = Path("/tmp/test")
        converter = EntityConverter(property_registry=property_registry, redirects_dir=temp_dir)

        mock_load_redirects.return_value = ["Q100", "Q200"]

        result = converter._fetch_redirects("Q42")

        assert set(result) == {"Q100", "Q200"}
        mock_load_redirects.assert_called_once_with("Q42", temp_dir)

    def test_fetch_redirects_vitess_client(self) -> None:
        """Test fetching redirects from Vitess client."""
        property_registry = PropertyRegistry(properties={})
        mock_vitess = MagicMock()
        converter = EntityConverter(property_registry=property_registry, vitess_client=mock_vitess)

        mock_vitess.get_incoming_redirects.return_value = ["Q100"]

        result = converter._fetch_redirects("Q42")

        assert result == ["Q100"]
        mock_vitess.get_incoming_redirects.assert_called_once_with("Q42")

    def test_fetch_redirects_vitess_exception(self) -> None:
        """Test fetching redirects when Vitess throws exception."""
        property_registry = PropertyRegistry(properties={})
        mock_vitess = MagicMock()
        converter = EntityConverter(property_registry=property_registry, vitess_client=mock_vitess)

        mock_vitess.get_incoming_redirects.side_effect = Exception("Vitess error")

        result = converter._fetch_redirects("Q42")

        assert result == []
        mock_vitess.get_incoming_redirects.assert_called_once_with("Q42")

    @patch('models.rdf_builder.converter.load_entity_redirects')
    def test_fetch_redirects_file_exception(self, mock_load_redirects) -> None:
        """Test fetching redirects when file loading throws exception."""
        property_registry = PropertyRegistry(properties={})
        from pathlib import Path
        temp_dir = Path("/tmp/test")
        converter = EntityConverter(property_registry=property_registry, redirects_dir=temp_dir)

        mock_load_redirects.side_effect = Exception("File error")

        result = converter._fetch_redirects("Q42")

        assert result == []
        mock_load_redirects.assert_called_once_with("Q42", temp_dir)

    def test_write_redirects(self) -> None:
        """Test writing redirects."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()
        mock_entity = MagicMock()
        mock_entity.id = "Q42"

        with patch.object(converter, '_fetch_redirects', return_value=["Q100", "Q200"]) as mock_fetch, \
             patch('models.rdf_builder.writers.triple.TripleWriters.write_redirect') as mock_write_redirect:

            converter._write_redirects(mock_entity, output)

            mock_fetch.assert_called_once_with("Q42")
            assert mock_write_redirect.call_count == 2
            mock_write_redirect.assert_any_call(output, "Q100", "Q42")
            mock_write_redirect.assert_any_call(output, "Q200", "Q42")

    def test_write_property_metadata_with_references(self) -> None:
        """Test writing property metadata including references."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        output = io.StringIO()

        # Mock entity with statements including references
        mock_entity = MagicMock()
        mock_entity.statements = MagicMock()

        with patch('models.rdf_builder.property_registry.registry.PropertyRegistry.shape', MagicMock()) as mock_shape:
            mock_entity.statements.data = [
                {"mainsnak": {"property": "P31"}, "qualifiers": {}, "references": [
                    {"snaks": {"P248": {"property": "P248"}}}
                ]}
            ]

            # Mock parsed statement with reference
            mock_ref_snak = MagicMock()
            mock_ref_snak.property = "P248"

            mock_ref = MagicMock()
            mock_ref.snaks = [mock_ref_snak]

            mock_stmt = MagicMock()
            mock_stmt.property = "P31"
            mock_stmt.qualifiers = []
            mock_stmt.references = [mock_ref]

            with patch('models.rdf_builder.converter.parse_statement', return_value=mock_stmt), \
                 patch('models.rdf_builder.converter.PropertyOntologyWriter') as mock_writer:

                converter._write_property_metadata(mock_entity, output)

                # Should include P248 from reference
                property_registry.shape.assert_any_call("P248")

    def test_convert_to_string(self) -> None:
        """Test convert_to_string method."""
        property_registry = PropertyRegistry(properties={})
        converter = EntityConverter(property_registry=property_registry)

        mock_entity = MagicMock()

        with patch('models.rdf_builder.converter.EntityConverter.convert_to_turtle') as mock_convert:
            mock_convert.return_value = None  # convert_to_turtle writes to buffer

            result = converter.convert_to_string(mock_entity)

            mock_convert.assert_called_once()
            # The result should be from the StringIO buffer
            # Since convert_to_turtle is mocked, result is empty string
            assert isinstance(result, str)