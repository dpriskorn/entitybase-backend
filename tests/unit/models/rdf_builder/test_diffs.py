"""Tests for diff classes."""

from models.rdf_builder import DiffResult, StatementDiff, TermsDiff, SitelinksDiff, EntityDiffs


def test_diff_result_model():
    """Test DiffResult model."""
    diff = DiffResult(
        added=["item1"], removed=["item2"], modified=[{"old": "a", "new": "b"}]
    )
    assert diff.added == ["item1"]
    assert diff.removed == ["item2"]
    assert diff.modified == [{"old": "a", "new": "b"}]


def test_statement_diff():
    """Test StatementDiff computation."""

    # Mock statements with ids
    class MockStmt:
        def __init__(self, stmt_id):
            self.id = stmt_id

    old_stmts = [MockStmt("s1"), MockStmt("s2")]
    new_stmts = [MockStmt("s1"), MockStmt("s3")]

    diff = StatementDiff.compute(old_stmts, new_stmts)

    assert len(diff.added) == 1
    assert diff.added[0].id == "s3"
    assert len(diff.removed) == 1
    assert diff.removed[0].id == "s2"


def test_terms_diff():
    """Test TermsDiff computation."""
    old_terms = {"en": {"language": "en", "value": "Old"}}
    new_terms = {
        "en": {"language": "en", "value": "New"},
        "fr": {"language": "fr", "value": "Nouveau"},
    }

    diff = TermsDiff.compute(old_terms, new_terms)

    assert len(diff.added) == 1
    assert diff.modified[0]["new"]["value"] == "New"


def test_sitelinks_diff():
    """Test SitelinksDiff computation."""
    old_links = {"enwiki": "Old_Page"}
    new_links = {"enwiki": "New_Page", "frwiki": "Page_Fr"}

    diff = SitelinksDiff.compute(old_links, new_links)

    assert len(diff.added) == 1
    assert diff.added[0] == "Page_Fr"
    assert len(diff.removed) == 0
    assert len(diff.modified) == 1
    assert diff.modified[0]["old"] == "Old_Page"
    assert diff.modified[0]["new"] == "New_Page"


def test_entity_diffs_model():
    """Test EntityDiffs model."""
    statements_diff = DiffResult(added=["s1"], removed=["s2"])
    terms_diff = DiffResult(modified=[{"old": "old_term", "new": "new_term"}])
    sitelinks_diff = DiffResult(added=["frwiki"])

    entity_diffs = EntityDiffs(
        statements=statements_diff, terms=terms_diff, sitelinks=sitelinks_diff
    )

    assert entity_diffs.statements.added == ["s1"]
    assert entity_diffs.terms.modified[0]["new"] == "new_term"
    assert entity_diffs.sitelinks.added == ["frwiki"]


def test_statement_diff_with_modified():
    """Test StatementDiff with modified statements."""
    class MockStmt:
        def __init__(self, stmt_id, property_id):
            self.id = stmt_id
            self.property_id = property_id

    old_stmts = [MockStmt("s1", "P1"), MockStmt("s2", "P2")]
    new_stmts = [MockStmt("s1", "P1"), MockStmt("s2", "P2_modified")]

    diff = StatementDiff.compute(old_stmts, new_stmts)

    # For now, simplified version doesn't detect modifications
    assert len(diff.added) == 0
    assert len(diff.removed) == 0
    assert len(diff.modified) == 0


def test_terms_diff_edge_cases():
    """Test TermsDiff with various edge cases."""
    # Empty dicts
    diff = TermsDiff.compute({}, {})
    assert len(diff.added) == 0
    assert len(diff.removed) == 0
    assert len(diff.modified) == 0

    # Only additions
    old_terms = {}
    new_terms = {"en": {"language": "en", "value": "Test"}}
    diff = TermsDiff.compute(old_terms, new_terms)
    assert len(diff.added) == 1
    assert len(diff.removed) == 0
    assert len(diff.modified) == 0

    # Only removals
    old_terms = {"en": {"language": "en", "value": "Test"}}
    new_terms = {}
    diff = TermsDiff.compute(old_terms, new_terms)
    assert len(diff.added) == 0
    assert len(diff.removed) == 1
    assert len(diff.modified) == 0


def test_sitelinks_diff_edge_cases():
    """Test SitelinksDiff with various edge cases."""
    # Empty dicts
    diff = SitelinksDiff.compute({}, {})
    assert len(diff.added) == 0
    assert len(diff.removed) == 0
    assert len(diff.modified) == 0

    # Only additions
    old_links = {}
    new_links = {"enwiki": "Page"}
    diff = SitelinksDiff.compute(old_links, new_links)
    assert len(diff.added) == 1
    assert len(diff.removed) == 0
    assert len(diff.modified) == 0

    # Only removals
    old_links = {"enwiki": "Page"}
    new_links = {}
    diff = SitelinksDiff.compute(old_links, new_links)
    assert len(diff.added) == 0
    assert len(diff.removed) == 1
    assert len(diff.modified) == 0
