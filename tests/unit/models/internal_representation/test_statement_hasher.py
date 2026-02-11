"""Unit tests for StatementHasher."""

from models.internal_representation.statement_hasher import StatementHasher
from models.internal_representation.statements import Statement
from models.internal_representation.ranks import Rank
from models.internal_representation.values.entity_value import EntityValue
from models.internal_representation.qualifiers import Qualifier
from models.internal_representation.references import Reference, ReferenceValue


def test_statement_hash_consistency() -> None:
    """Same statement produces same hash"""
    statement = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="Q42$12345678-1234-1234-1234-123456789abc",
    )

    hash1 = StatementHasher.compute_hash(statement)
    hash2 = StatementHasher.compute_hash(statement)

    assert hash1 == hash2, "Same statement should produce same hash"
    assert isinstance(hash1, int), "Hash should be an integer"


def test_statement_hash_different_statements() -> None:
    """Different statements produce different hashes"""
    statement1 = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="Q42$12345678-1234-1234-1234-123456789abc",
    )

    statement2 = Statement(
        property="P31",
        value=EntityValue(value="Q515"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="Q42$87654321-4321-4321-4321-cba987654321",
    )

    hash1 = StatementHasher.compute_hash(statement1)
    hash2 = StatementHasher.compute_hash(statement2)

    assert hash1 != hash2, "Different statements should produce different hashes"


def test_statement_hash_excludes_statement_id() -> None:
    """Hash excludes statement_id (GUID)"""
    statement1 = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="Q42$11111111-1111-1111-1111-111111111111",
    )

    statement2 = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="Q42$22222222-2222-2222-2222-222222222222",
    )

    hash1 = StatementHasher.compute_hash(statement1)
    hash2 = StatementHasher.compute_hash(statement2)

    assert hash1 == hash2, "Hash should be independent of statement_id"


def test_statement_hash_dict_input() -> None:
    """Test computing hash from dict input."""
    statement_dict = {
        "property": "P31",
        "value": {
            "kind": "entity",
            "value": "Q5",
            "datatype_uri": "http://www.wikidata.org/entity/",
        },
        "rank": "normal",
        "qualifiers": [],
        "references": [],
        "statement_id": "Q5$12345678-1234-1234-1234-123456789012",
    }

    hash_value = StatementHasher.compute_hash(statement_dict)

    assert isinstance(hash_value, int)
    assert hash_value > 0


def test_statement_hash_includes_all_components() -> None:
    """Hash includes property, value, rank, qualifiers, references"""
    base_statement = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="test-id",
    )

    base_hash = StatementHasher.compute_hash(base_statement)

    # Different property
    different_property = Statement(
        property="P279",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="test-id",
    )
    hash_property = StatementHasher.compute_hash(different_property)
    assert base_hash != hash_property, "Hash should include property"

    # Different value
    different_value = Statement(
        property="P31",
        value=EntityValue(value="Q515"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="test-id",
    )
    hash_value = StatementHasher.compute_hash(different_value)
    assert base_hash != hash_value, "Hash should include value"

    # Different rank
    different_rank = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.PREFERRED,
        qualifiers=[],
        references=[],
        statement_id="test-id",
    )
    hash_rank = StatementHasher.compute_hash(different_rank)
    assert base_hash != hash_rank, "Hash should include rank"

    # With qualifiers
    with_qualifiers = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[
            Qualifier(property="P585", value=EntityValue(value="+1952-03-03T00:00:00Z"))
        ],
        references=[],
        statement_id="test-id",
    )
    hash_qualifiers = StatementHasher.compute_hash(with_qualifiers)
    assert base_hash != hash_qualifiers, "Hash should include qualifiers"

    # With references
    with_references = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[
            Reference(
                hash="ref1",
                snaks=[
                    ReferenceValue(property="P248", value=EntityValue(value="Q539"))
                ],
            )
        ],
        statement_id="test-id",
    )
    hash_references = StatementHasher.compute_hash(with_references)
    assert base_hash != hash_references, "Hash should include references"


def test_statement_hash_ordering() -> None:
    """Hash is deterministic (order of qualifiers/references doesn't matter after JSON sorting)"""
    statement = Statement(
        property="P31",
        value=EntityValue(value="Q5"),
        rank=Rank.NORMAL,
        qualifiers=[],
        references=[],
        statement_id="test-id",
    )

    hash1 = StatementHasher.compute_hash(statement)
    hash2 = StatementHasher.compute_hash(statement)

    assert hash1 == hash2, "Hash should be deterministic"
