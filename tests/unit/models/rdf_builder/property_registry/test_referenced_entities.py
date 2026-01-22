import os
from pathlib import Path

from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.ontology.datatypes import property_shape
from models.rdf_builder.property_registry.registry import PropertyRegistry

TEST_DATA_DIR = Path(os.environ["TEST_DATA_DIR"])


def test_load_referenced_entity_missing_file() -> None:
    """Test that missing referenced entity JSON raises FileNotFoundError"""
    entity_metadata_dir = TEST_DATA_DIR / "json" / "entities"

    properties = {
        "P31": property_shape("P31", "wikibase-item"),
    }
    registry = PropertyRegistry(properties=properties)

    converter = EntityConverter(
        property_registry=registry, entity_metadata_dir=entity_metadata_dir
    )

    try:
        converter._load_referenced_entity("Q999999")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "Q999999" in str(e)


def test_converter_with_cache_path_generates_referenced_entity() -> None:
    """Test that EntityConverter with entity_metadata_dir generates referenced entity metadata"""
    entity_metadata_dir = TEST_DATA_DIR / "json" / "entities"

    entity_id = "Q17948861"
    json_path = entity_metadata_dir / f"{entity_id}.json"

    import json

    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    from models.json_parser.entity_parser import parse_entity

    entity = parse_entity(entity_json)

    properties = {
        "P31": property_shape("P31", "wikibase-item"),
    }
    registry = PropertyRegistry(properties=properties)

    converter = EntityConverter(
        property_registry=registry, entity_metadata_dir=entity_metadata_dir
    )
    actual_ttl = converter.convert_to_string(entity)

    assert "wd:Q17633526 a wikibase:Item" in actual_ttl
    assert 'rdfs:label "Wikinews article"@en' in actual_ttl
