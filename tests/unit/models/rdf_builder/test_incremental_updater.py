"""Tests for IncrementalRDFUpdater."""

from models.internal_representation.entity_data import EntityData
from models.rdf_builder.incremental_updater import IncrementalRDFUpdater


def test_incremental_rdf_updater_init():
    """Test IncrementalRDFUpdater initialization."""
    updater = IncrementalRDFUpdater(entity_id="Q1", current_rdf="<rdf>")
    assert updater.entity_id == "Q1"
    assert updater.current_rdf == "<rdf>"


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
