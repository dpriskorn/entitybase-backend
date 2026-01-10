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
    """Test counting statements per property"""
    claims: dict[str, list[dict[str, str]]] = {
        "P31": [{"id": "Q5$1", "value": "test"}],
        "P569": [{"id": "Q5$2", "value": "test"}, {"id": "Q5$3", "value": "test"}],
        "P19": [],
        "P279": [{"id": "Q5$4", "value": "test"}],
    }

    counts = StatementExtractor.compute_property_counts_from_claims(claims)

    expected = {"P31": 1, "P569": 2, "P279": 1}  # excluding empty P19
    assert counts == expected, f"Expected {expected}, got {counts}"


def test_compute_property_counts_from_claims_empty() -> None:
    """Test with no claims"""
    claims: dict[str, list[dict[str, str]]] = {}
    counts = StatementExtractor.compute_property_counts_from_claims(claims)
    assert counts == {}, "Expected empty dict"


def test_compute_property_counts_from_claims_all_empty() -> None:
    """Test with only empty claim lists"""
    claims: dict[str, list[dict[str, str]]] = {"P31": [], "P569": []}
    counts = StatementExtractor.compute_property_counts_from_claims(claims)
    assert counts == {}, "Expected empty dict"
