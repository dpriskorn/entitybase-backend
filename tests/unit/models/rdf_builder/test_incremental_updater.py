"""Tests for IncrementalRDFUpdater."""

import pytest
from unittest.mock import patch

from models.rdf_builder.incremental_updater import IncrementalRDFUpdater
from models.rdf_builder import DiffResult, EntityDiffs, StatementDiff, TermsDiff, SitelinksDiff
from models.internal_representation.entity_data import EntityData


def test_incremental_rdf_updater_init():
    """Test IncrementalRDFUpdater initialization."""
    updater = IncrementalRDFUpdater(entity_id="Q1", current_rdf="<rdf>")
    assert updater.entity_id == "Q1"
    assert updater.current_rdf == "<rdf>"


def test_incremental_rdf_updater_init_default():
    """Test IncrementalRDFUpdater initialization with default values."""
    updater = IncrementalRDFUpdater(entity_id="Q1")
    assert updater.entity_id == "Q1"
    assert updater.current_rdf == ""


def test_apply_statement_diffs_added():
    """Test applying statement diffs with added statements."""
    updater = IncrementalRDFUpdater(entity_id="Q123")
    diff = DiffResult(added=["stmt1", "stmt2"], removed=[])
    updater._apply_statement_diffs(diff)
    assert "# Added statement: stmt1" in updater.current_rdf
    assert "# Added statement: stmt2" in updater.current_rdf


def test_apply_statement_diffs_removed():
    """Test applying statement diffs with removed statements."""
    updater = IncrementalRDFUpdater(entity_id="Q123")
    diff = DiffResult(added=[], removed=["stmt1", "stmt2"])
    updater._apply_statement_diffs(diff)
    assert "# Removed statement: stmt1" in updater.current_rdf
    assert "# Removed statement: stmt2" in updater.current_rdf


def test_apply_terms_diffs_added():
    """Test applying terms diffs with added terms."""
    updater = IncrementalRDFUpdater(entity_id="Q123")
    diff = DiffResult(added=["term1"], removed=[])
    updater._apply_terms_diffs(diff)
    assert "# Added term: term1" in updater.current_rdf


def test_apply_terms_diffs_removed():
    """Test applying terms diffs with removed terms."""
    updater = IncrementalRDFUpdater(entity_id="Q123")
    diff = DiffResult(added=[], removed=["term1"])
    updater._apply_terms_diffs(diff)
    assert "# Removed term: term1" in updater.current_rdf


def test_apply_sitelinks_diffs_added():
    """Test applying sitelinks diffs with added links."""
    updater = IncrementalRDFUpdater(entity_id="Q123")
    diff = DiffResult(added=["enwiki"], removed=[])
    updater._apply_sitelinks_diffs(diff)
    assert "# Added sitelink: enwiki" in updater.current_rdf


def test_apply_sitelinks_diffs_removed():
    """Test applying sitelinks diffs with removed links."""
    updater = IncrementalRDFUpdater(entity_id="Q123")
    diff = DiffResult(added=[], removed=["enwiki"])
    updater._apply_sitelinks_diffs(diff)
    assert "# Removed sitelink: enwiki" in updater.current_rdf


def test_apply_diffs_combined():
    """Test applying all diffs together."""
    updater = IncrementalRDFUpdater(entity_id="Q123")
    diffs = EntityDiffs(
        statements=DiffResult(added=["stmt1"], removed=[]),
        terms=DiffResult(added=["label1"], removed=[]),
        sitelinks=DiffResult(added=["enwiki"], removed=[]),
    )
    updater.apply_diffs(diffs)
    assert "# Added statement: stmt1" in updater.current_rdf
    assert "# Added term: label1" in updater.current_rdf
    assert "# Added sitelink: enwiki" in updater.current_rdf


def test_get_updated_rdf():
    """Test getting the updated RDF string."""
    updater = IncrementalRDFUpdater(entity_id="Q123", current_rdf="<rdf>")
    result = updater.get_updated_rdf()
    assert result == "<rdf>"


def test_compute_diffs():
    """Test computing diffs between entities."""
    old_entity = EntityData(
        id="Q1",
        type="item",
        labels={"en": {"language": "en", "value": "Old"}},
        descriptions={},
        aliases={},
        statements=[],
        sitelinks={"enwiki": "Old_Page"},
    )

    new_entity = EntityData(
        id="Q1",
        type="item",
        labels={"en": {"language": "en", "value": "New"}},
        descriptions={},
        aliases={},
        statements=[],
        sitelinks={"enwiki": "New_Page", "frwiki": "Page_Fr"},
    )

    diffs = IncrementalRDFUpdater.compute_diffs(old_entity, new_entity)

    assert diffs.terms.modified
    assert diffs.sitelinks.modified
    assert diffs.sitelinks.added


def test_compute_diffs_with_none_sitelinks():
    """Test computing diffs when old entity has None sitelinks."""
    old_entity = EntityData(
        id="Q1",
        type="item",
        labels={},
        descriptions={},
        aliases={},
        statements=[],
        sitelinks=None,
    )

    new_entity = EntityData(
        id="Q1",
        type="item",
        labels={},
        descriptions={},
        aliases={},
        statements=[],
        sitelinks={"enwiki": "Page"},
    )

    diffs = IncrementalRDFUpdater.compute_diffs(old_entity, new_entity)
    # SitelinksDiff.added contains values (page names), not keys (site names)
    assert diffs.sitelinks.added == ["Page"]
