"""Unit tests for lexeme form and sense ID assignment utilities."""

import pytest


class TestAssignFormAndSenseIds:
    """Test auto-ID generation for forms and senses."""

    def test_assign_form_ids_no_forms(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import assign_form_ids

        result = assign_form_ids("L42", [])
        assert result.get_json() == []

    def test_assign_form_ids_with_existing_ids(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import assign_form_ids

        forms = [
            {
                "id": "L42-F1",
                "representations": {"en": {"language": "en", "value": "test"}},
            },
            {
                "id": "L42-F2",
                "representations": {"en": {"language": "en", "value": "tests"}},
            },
        ]
        result = assign_form_ids("L42", forms)
        assert result.get_json()[0]["id"] == "L42-F1"
        assert result.get_json()[1]["id"] == "L42-F2"

    def test_assign_form_ids_missing_ids(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import assign_form_ids

        forms = [
            {"representations": {"en": {"language": "en", "value": "test"}}},
            {"representations": {"en": {"language": "en", "value": "tests"}}},
        ]
        result = assign_form_ids("L42", forms)
        assert result.get_json()[0]["id"] == "L42-F1"
        assert result.get_json()[1]["id"] == "L42-F2"

    def test_assign_form_ids_mixed_ids(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import assign_form_ids

        forms = [
            {
                "id": "L42-F5",
                "representations": {"en": {"language": "en", "value": "test"}},
            },
            {"representations": {"en": {"language": "en", "value": "tests"}}},
        ]
        result = assign_form_ids("L42", forms)
        assert result.get_json()[0]["id"] == "L42-F5"
        assert result.get_json()[1]["id"] == "L42-F6"

    def test_assign_form_ids_empty_id(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import assign_form_ids

        forms = [
            {"id": "", "representations": {"en": {"language": "en", "value": "test"}}},
        ]
        result = assign_form_ids("L42", forms)
        assert result.get_json()[0]["id"] == "L42-F1"

    def test_assign_form_ids_continues_after_highest(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import assign_form_ids

        forms = [
            {
                "id": "L42-F1",
                "representations": {"en": {"language": "en", "value": "first"}},
            },
            {
                "id": "L42-F10",
                "representations": {"en": {"language": "en", "value": "tenth"}},
            },
            {"representations": {"en": {"language": "en", "value": "new"}}},
        ]
        result = assign_form_ids("L42", forms)
        assert result.get_json()[0]["id"] == "L42-F1"
        assert result.get_json()[1]["id"] == "L42-F10"
        assert result.get_json()[2]["id"] == "L42-F11"

    def test_assign_sense_ids_no_senses(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
            assign_sense_ids,
        )

        result = assign_sense_ids("L42", [])
        assert result.get_json() == []

    def test_assign_sense_ids_with_existing_ids(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
            assign_sense_ids,
        )

        senses = [
            {
                "id": "L42-S1",
                "glosses": {"en": {"language": "en", "value": "first meaning"}},
            },
            {
                "id": "L42-S2",
                "glosses": {"en": {"language": "en", "value": "second meaning"}},
            },
        ]
        result = assign_sense_ids("L42", senses)
        assert result.get_json()[0]["id"] == "L42-S1"
        assert result.get_json()[1]["id"] == "L42-S2"

    def test_assign_sense_ids_missing_ids(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
            assign_sense_ids,
        )

        senses = [
            {"glosses": {"en": {"language": "en", "value": "first meaning"}}},
            {"glosses": {"en": {"language": "en", "value": "second meaning"}}},
        ]
        result = assign_sense_ids("L42", senses)
        assert result.get_json()[0]["id"] == "L42-S1"
        assert result.get_json()[1]["id"] == "L42-S2"

    def test_assign_sense_ids_mixed_ids(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
            assign_sense_ids,
        )

        senses = [
            {"id": "L42-S3", "glosses": {"en": {"language": "en", "value": "third"}}},
            {"glosses": {"en": {"language": "en", "value": "new"}}},
        ]
        result = assign_sense_ids("L42", senses)
        assert result.get_json()[0]["id"] == "L42-S3"
        assert result.get_json()[1]["id"] == "L42-S4"

    def test_assign_sense_ids_continues_after_highest(self):
        from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
            assign_sense_ids,
        )

        senses = [
            {"id": "L42-S1", "glosses": {"en": {"language": "en", "value": "first"}}},
            {"id": "L42-S5", "glosses": {"en": {"language": "en", "value": "fifth"}}},
            {"glosses": {"en": {"language": "en", "value": "new"}}},
        ]
        result = assign_sense_ids("L42", senses)
        assert result.get_json()[0]["id"] == "L42-S1"
        assert result.get_json()[1]["id"] == "L42-S5"
        assert result.get_json()[2]["id"] == "L42-S6"
