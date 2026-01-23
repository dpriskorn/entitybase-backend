import pytest

from models.json_parser import parse_qualifiers, parse_qualifier
from models.internal_representation.qualifiers import Qualifier


def test_parse_qualifiers_basic() -> None:
    """Test parsing qualifiers with entity values"""
    qualifiers_json = {
        "P2": [
            {
                "snaktype": "value",
                "property": "P2",
                "datatype": "wikibase-item",
                "datavalue": {
                    "value": {"entity-type": "item", "numeric-id": 42, "id": "Q42"},
                    "type": "wikibase-entityid",
                },
            }
        ]
    }

    qualifiers = parse_qualifiers(qualifiers_json)
    assert len(qualifiers) == 1
    assert qualifiers[0].property == "P2"
    assert qualifiers[0].value.kind == "entity"
    assert qualifiers[0].value.value == "Q42"


def test_parse_qualifiers_multiple() -> None:
    """Test parsing qualifiers with multiple qualifiers of same property"""
    qualifiers_json = {
        "P2": [
            {
                "snaktype": "value",
                "property": "P2",
                "datatype": "wikibase-item",
                "datavalue": {
                    "value": {"entity-type": "item", "numeric-id": 42},
                    "type": "wikibase-entityid",
                },
            },
            {
                "snaktype": "value",
                "property": "P2",
                "datatype": "wikibase-item",
                "datavalue": {
                    "value": {"entity-type": "item", "numeric-id": 666},
                    "type": "wikibase-entityid",
                },
            },
        ]
    }

    qualifiers = parse_qualifiers(qualifiers_json)
    assert len(qualifiers) == 2
    assert all(q.property == "P2" for q in qualifiers)
    assert all(q.value.kind == "entity" for q in qualifiers)


def test_parse_qualifier_with_novalue() -> None:
    """Test parsing qualifier with novalue"""
    qualifier_json = {"snaktype": "novalue", "property": "P2"}

    qualifier = parse_qualifier(qualifier_json)
    assert qualifier.property == "P2"
    assert qualifier.value.kind == "novalue"


def test_parse_qualifier_with_somevalue() -> None:
    """Test parsing qualifier with somevalue"""
    qualifier_json = {"snaktype": "somevalue", "property": "P3"}

    qualifier = parse_qualifier(qualifier_json)
    assert qualifier.property == "P3"
    assert qualifier.value.kind == "somevalue"


def test_parse_qualifier_with_property_override() -> None:
    """Test parsing qualifier where property is overridden in JSON"""
    qualifier_json = {
        "snaktype": "value",
        "property": "P999",  # Different from parameter
        "datavalue": {
            "value": "test",
            "type": "string"
        }
    }

    # Property in JSON should take precedence
    qualifier = parse_qualifier(qualifier_json, property_id="P123")
    assert qualifier.property == "P999"
    assert qualifier.value.kind == "string"
    assert qualifier.value.value == "test"


def test_parse_qualifier_property_fallback() -> None:
    """Test parsing qualifier where property falls back to parameter"""
    qualifier_json = {
        "snaktype": "value",
        "datavalue": {
            "value": "test",
            "type": "string"
        }
        # No property field in JSON
    }

    qualifier = parse_qualifier(qualifier_json, property_id="P123")
    assert qualifier.property == "P123"


def test_parse_qualifiers_empty() -> None:
    """Test parsing empty qualifiers dictionary"""
    qualifiers = parse_qualifiers({})
    assert qualifiers == []


def test_parse_qualifiers_mixed_properties() -> None:
    """Test parsing qualifiers with multiple different properties"""
    qualifiers_json = {
        "P2": [
            {
                "snaktype": "value",
                "property": "P2",
                "datavalue": {"value": "test1", "type": "string"}
            }
        ],
        "P3": [
            {
                "snaktype": "value",
                "property": "P3",
                "datavalue": {"value": "test2", "type": "string"}
            },
            {
                "snaktype": "novalue",
                "property": "P3"
            }
        ]
    }

    qualifiers = parse_qualifiers(qualifiers_json)
    assert len(qualifiers) == 3

    # Check first property
    p2_qualifiers = [q for q in qualifiers if q.property == "P2"]
    assert len(p2_qualifiers) == 1
    assert p2_qualifiers[0].value.value == "test1"

    # Check second property
    p3_qualifiers = [q for q in qualifiers if q.property == "P3"]
    assert len(p3_qualifiers) == 2
    assert p3_qualifiers[0].value.value == "test2"
    assert p3_qualifiers[1].value.kind == "novalue"


def test_parse_qualifiers_time_values() -> None:
    """Test parsing qualifiers with time values"""
    qualifiers_json = {
        "P580": [  # start time
            {
                "snaktype": "value",
                "property": "P580",
                "datatype": "time",
                "datavalue": {
                    "value": {
                        "time": "+2020-01-01T00:00:00Z",
                        "timezone": 0,
                        "before": 0,
                        "after": 0,
                        "precision": 11,
                        "calendarmodel": "http://www.wikidata.org/entity/Q1985727"
                    },
                    "type": "time"
                }
            }
        ]
    }

    qualifiers = parse_qualifiers(qualifiers_json)
    assert len(qualifiers) == 1
    assert qualifiers[0].property == "P580"
    assert qualifiers[0].value.kind == "time"
    assert qualifiers[0].value.value == "+2020-01-01T00:00:00Z"


def test_parse_qualifiers_quantity_values() -> None:
    """Test parsing qualifiers with quantity values"""
    qualifiers_json = {
        "P1107": [  # number of
            {
                "snaktype": "value",
                "property": "P1107",
                "datatype": "quantity",
                "datavalue": {
                    "value": {
                        "amount": "42",
                        "unit": "1"
                    },
                    "type": "quantity"
                }
            }
        ]
    }

    qualifiers = parse_qualifiers(qualifiers_json)
    assert len(qualifiers) == 1
    assert qualifiers[0].property == "P1107"
    assert qualifiers[0].value.kind == "quantity"
    assert qualifiers[0].value.value == "42"


def test_parse_qualifier_result_immutability() -> None:
    """Test that parsed qualifier results are immutable"""
    qualifier_json = {"snaktype": "novalue", "property": "P2"}

    qualifier = parse_qualifier(qualifier_json)
    assert isinstance(qualifier, Qualifier)

    # Should not be able to modify frozen model
    import pytest
    with pytest.raises(Exception):  # TypeError or ValidationError
        qualifier.property = "P999"


def test_parse_qualifiers_result_immutability() -> None:
    """Test that parsed qualifiers list results are immutable"""
    qualifiers_json = {
        "P2": [{"snaktype": "novalue", "property": "P2"}]
    }

    qualifiers = parse_qualifiers(qualifiers_json)
    assert len(qualifiers) == 1
    assert isinstance(qualifiers[0], Qualifier)

    # Should not be able to modify the list
    with pytest.raises(AttributeError):
        qualifiers.append(Qualifier(property="P3", value=None))

    # Should not be able to modify individual qualifiers
    with pytest.raises(Exception):  # TypeError or ValidationError
        qualifiers[0].property = "P999"
