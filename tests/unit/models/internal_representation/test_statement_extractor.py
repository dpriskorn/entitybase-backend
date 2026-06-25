import sys

sys.path.insert(0, "src")

from models.internal_representation.statement_extractor import StatementExtractor


def test_extract_properties_from_claims() -> None:
    """Test extracting properties from claims dict"""
    claims: dict[str, list[dict[str, str]]] = {
        "P31": [{"id": "Q5$1", "value": "test"}],
        "P569": [{"id": "Q5$2", "value": "test"}, {"id": "Q5$3", "value": "test"}],
        "P19": [],
        "P279": [{"id": "Q5$4", "value": "test"}],
    }

    properties = StatementExtractor.extract_properties_from_claims(claims)

    expected = ["P279", "P31", "P569"]  # sorted, excluding empty P19
    assert properties == expected, f"Expected {expected}, got {properties}"


def test_extract_properties_from_claims_empty() -> None:
    """Test with no claims"""
    claims: dict[str, list[dict[str, str]]] = {}
    properties = StatementExtractor.extract_properties_from_claims(claims)
    assert properties == [], "Expected empty list"


def test_extract_properties_from_claims_all_empty() -> None:
    """Test with only empty claim lists"""
    claims: dict[str, list[dict[str, str]]] = {"P31": [], "P569": []}
    properties = StatementExtractor.extract_properties_from_claims(claims)
    assert properties == [], "Expected empty list"


def test_compute_property_counts_from_claims() -> None:
    """Test computing property counts from claims dict"""
    claims: dict[str, list[dict[str, str]]] = {
        "P31": [{"id": "Q5$1"}],
        "P569": [{"id": "Q5$2"}, {"id": "Q5$3"}],
        "P19": [],
    }

    counts = StatementExtractor.compute_property_counts_from_claims(claims)

    assert counts.root["P31"] == 1
    assert counts.root["P569"] == 2
    assert "P19" not in counts.root


def test_compute_property_counts_from_claims_empty() -> None:
    """Test computing property counts with empty claims dict"""
    claims: dict[str, list[dict[str, str]]] = {}

    counts = StatementExtractor.compute_property_counts_from_claims(claims)

    assert counts.root == {}


def test_compute_property_counts_from_claims_all_empty_lists() -> None:
    """Test computing property counts with only empty claim lists"""
    claims: dict[str, list[dict[str, str]]] = {"P31": [], "P569": []}

    counts = StatementExtractor.compute_property_counts_from_claims(claims)

    assert counts.root == {}
