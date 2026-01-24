"""Test lexeme processing with real data."""

import json
from pathlib import Path

from models.json_parser.entity_parser import parse_entity_data
from models.internal_representation.metadata_extractor import MetadataExtractor


def test_lexeme_l42_processing():
    """Test that L42 lexeme can be parsed and processed."""
    test_data_path = Path(__file__).parent.parent.parent.parent / "test_data" / "json" / "entities" / "L42.json"

    with open(test_data_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Parse the entity
    entity_data = parse_entity_data(raw_data)

    assert entity_data.id == "L42"
    assert entity_data.type == "lexeme"
    assert entity_data.lemmas is not None
    assert entity_data.forms is not None
    assert entity_data.senses is not None

    # Test hash generation for some terms
    extractor = MetadataExtractor()

    # Test lemma hashing
    lemma_text = entity_data.lemmas["en"]["value"]
    lemma_hash = extractor.hash_string(lemma_text)
    assert isinstance(lemma_hash, int)
    assert lemma_hash > 0

    # Test form representation hashing
    for form in entity_data.forms:
        for lang, rep in form.representations.items():
            rep_hash = extractor.hash_string(rep.value)
            assert isinstance(rep_hash, int)
            assert rep_hash > 0

    # Test sense gloss hashing
    for sense in entity_data.senses:
        for lang, gloss in sense.glosses.items():
            gloss_hash = extractor.hash_string(gloss.value)
            assert isinstance(gloss_hash, int)
            assert gloss_hash > 0

    print("✅ Lexeme L42 processing test passed")


if __name__ == "__main__":
    test_lexeme_l42_processing()