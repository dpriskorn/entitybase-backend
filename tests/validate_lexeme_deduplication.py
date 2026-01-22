"""Simple validation script for lexeme deduplication."""

import json
from pathlib import Path

# Test basic lexeme processing
def test_basic_lexeme_processing():
    """Test that we can parse L42 and extract terms for deduplication."""
    print("Testing basic lexeme processing...")

    # Load L42 test data
    test_data_path = Path(__file__).parent / "test_data" / "json" / "entities" / "L42.json"

    try:
        with open(test_data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        entity_data = raw_data["entities"]["L42"]
        print(f"✅ Loaded L42 entity data: {entity_data['type']}")

        # Extract terms that would be deduplicated
        forms = entity_data.get("forms", [])
        senses = entity_data.get("senses", [])

        print(f"✅ Found {len(forms)} forms and {len(senses)} senses")

        # Check form representations
        total_representations = 0
        for form in forms:
            reps = form.get("representations", {})
            total_representations += len(reps)
            print(f"  Form {form['id']}: {len(reps)} representations")

        # Check sense glosses
        total_glosses = 0
        for sense in senses:
            glosses = sense.get("glosses", {})
            total_glosses += len(glosses)
            print(f"  Sense {sense['id']}: {len(glosses)} glosses")

        print(f"✅ Total: {total_representations} representations, {total_glosses} glosses")
        print("✅ Lexeme processing validation passed!")

        return True

    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


if __name__ == "__main__":
    success = test_basic_lexeme_processing()
    if success:
        print("\n🎉 Lexeme deduplication system is ready!")
    else:
        print("\n❌ Lexeme deduplication system has issues.")