"""Unit tests for rdf_service."""

from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.services.rdf_service import serialize_entity_to_turtle


class TestRdfService:
    """Unit tests for RdfService."""

    def test_serialize_entity_to_turtle_basic(self):
        """Test serializing basic entity data to Turtle format."""
        entity_data = {
            "type": "item",
            "id": "Q1",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
        }

        with patch(
            "models.rest_api.entitybase.v1.services.rdf_service.parse_entity"
        ) as mock_parse, patch(
            "models.rdf_builder.converter.EntityConverter"
        ) as mock_converter_class:
            mock_entity = MagicMock()
            mock_parse.return_value = mock_entity

            mock_converter_instance = MagicMock()
            mock_converter_instance.convert_to_string.return_value = "@prefix wd: <http://wikidata.org/entity/> ."
            mock_converter_class.return_value = mock_converter_instance

            result = serialize_entity_to_turtle(entity_data)

            mock_parse.assert_called_once_with(entity_data)
            mock_converter_class.assert_called_once()
            mock_converter_instance.convert_to_string.assert_called_once_with(mock_entity)
            assert isinstance(result, str)

    def test_serialize_entity_to_turtle_with_property_registry(self):
        """Test serializing entity with custom property registry."""
        entity_data = {
            "type": "property",
            "id": "P1",
            "labels": {"en": {"language": "en", "value": "Test Property"}},
        }

        mock_registry = MagicMock()

        with patch(
            "models.rest_api.entitybase.v1.services.rdf_service.parse_entity"
        ) as mock_parse, patch(
            "models.rdf_builder.converter.EntityConverter"
        ) as mock_converter_class:
            mock_entity = MagicMock()
            mock_parse.return_value = mock_entity

            mock_converter_instance = MagicMock()
            mock_converter_instance.convert_to_string.return_value = "@prefix wp: <http://wikidata.org/prop/> ."
            mock_converter_class.return_value = mock_converter_instance

            result = serialize_entity_to_turtle(entity_data, property_registry=mock_registry)

            mock_converter_class.assert_called_once_with(
                property_registry=mock_registry,
                enable_deduplication=True,
            )
            assert isinstance(result, str)

    def test_serialize_entity_to_turtle_empty_entity(self):
        """Test serializing empty entity data."""
        entity_data = {"type": "item", "id": "Q1"}

        with patch(
            "models.rest_api.entitybase.v1.services.rdf_service.parse_entity"
        ) as mock_parse, patch(
            "models.rdf_builder.converter.EntityConverter"
        ) as mock_converter_class:
            mock_entity = MagicMock()
            mock_parse.return_value = mock_entity

            mock_converter_instance = MagicMock()
            mock_converter_instance.convert_to_string.return_value = ""
            mock_converter_class.return_value = mock_converter_instance

            result = serialize_entity_to_turtle(entity_data)

            assert result == ""
