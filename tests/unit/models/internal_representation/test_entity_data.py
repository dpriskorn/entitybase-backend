"""Tests for EntityData and parse_entity_data."""

import pytest

from models.internal_representation.entity_data import EntityData
from models.json_parser.entity_parser import parse_entity_data


def test_parse_entity_data_basic():
    """Test parsing basic entity JSON into EntityData."""
    raw_data = {
        "id": "Q1",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Item"}},
        "descriptions": {"en": {"language": "en", "value": "A test item"}},
        "aliases": {"en": [{"language": "en", "value": "Test"}]},
        "claims": {},
        "sitelinks": {"enwiki": "Test_Item"}
    }

    entity = parse_entity_data(raw_data)

    assert isinstance(entity, EntityData)
    assert entity.id == "Q1"
    assert entity.type == "item"
    assert "en" in entity.labels
    assert entity.labels["en"]["value"] == "Test Item"
    assert entity.sitelinks == {"enwiki": "Test_Item"}


def test_entity_data_model():
    """Test EntityData model creation."""
    entity = EntityData(
        id="Q1",
        type="item",
        labels={},
        descriptions={},
        aliases={},
        statements=[],
        sitelinks=None
    )

    assert entity.id == "Q1"
    assert entity.statements == []