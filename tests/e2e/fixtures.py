"""Shared test data fixtures for E2E tests."""

import pytest
from typing import Any


@pytest.fixture
def sample_item_data() -> dict[str, Any]:
    """Sample item entity data for testing."""
    return {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Item"}},
        "descriptions": {
            "en": {"language": "en", "value": "A test item for E2E testing"}
        },
    }


@pytest.fixture
def sample_item_with_statements() -> dict[str, Any]:
    """Sample item with statements for testing."""
    return {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Item with Statements"}},
        "descriptions": {
            "en": {"language": "en", "value": "Test item with statements"}
        },
        "statements": [
            {
                "property": {"id": "P31", "data_type": "wikibase-item"},
                "value": {"type": "value", "content": "Q5"},
                "rank": "normal",
            }
        ],
    }


@pytest.fixture
def sample_property_data() -> dict[str, Any]:
    """Sample property entity data for testing."""
    return {
        "type": "property",
        "datatype": "wikibase-item",
        "labels": {"en": {"language": "en", "value": "Test Property"}},
        "descriptions": {
            "en": {"language": "en", "value": "A test property for E2E testing"}
        },
    }


@pytest.fixture
def sample_lexeme_data() -> dict[str, Any]:
    """Sample lexeme entity data for testing."""
    return {
        "type": "lexeme",
        "language": "Q1860",
        "lexicalCategory": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "labels": {"en": {"language": "en", "value": "test lexeme"}},
        "forms": [
            {
                "id": "L1-F1",
                "representations": {"en": {"language": "en", "value": "tests"}},
                "grammaticalFeatures": ["Q110786"],
            }
        ],
        "senses": [
            {
                "id": "L1-S1",
                "glosses": {"en": {"language": "en", "value": "A test sense"}},
            }
        ],
    }


@pytest.fixture
def test_user_ids() -> list[int]:
    """Test user IDs for testing."""
    return [90001, 90002, 90003]


@pytest.fixture
def sample_sitelink() -> dict[str, Any]:
    """Sample sitelink data for testing."""
    return {"site": "enwiki", "title": "Test Article", "badges": []}


@pytest.fixture
def sample_edit_headers() -> dict[str, str]:
    """Sample edit headers for testing."""
    return {"X-Edit-Summary": "E2E test", "X-User-ID": "0"}
