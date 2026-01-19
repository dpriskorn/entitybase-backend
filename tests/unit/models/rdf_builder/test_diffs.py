"""Tests for diff classes."""

import pytest

from models.rdf_builder.diffs import DiffResult, StatementDiff, TermsDiff, SitelinksDiff


def test_diff_result_model():
    """Test DiffResult model."""
    diff = DiffResult(added=["item1"], removed=["item2"], modified=[{"old": "a", "new": "b"}])
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
    new_terms = {"en": {"language": "en", "value": "New"}, "fr": {"language": "fr", "value": "Nouveau"}}

    diff = TermsDiff.compute(old_terms, new_terms)

    assert len(diff.added) == 1
    assert diff.modified[0]["new"]["value"] == "New"


def test_sitelinks_diff():
    """Test SitelinksDiff computation."""
    old_links = {"enwiki": "Old_Page"}
    new_links = {"enwiki": "New_Page", "frwiki": "Page_Fr"}

    diff = SitelinksDiff.compute(old_links, new_links)

    assert len(diff.added) == 1
    assert diff.modified[0]["new"] == "New_Page"