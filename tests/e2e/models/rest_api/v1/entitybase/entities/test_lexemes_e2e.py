"""E2E tests for comprehensive lexeme operations."""

import pytest


@pytest.mark.e2e
def test_create_lexeme(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: Create a new lexeme entity."""
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"].startswith("L")
    assert "forms" in data
    assert "senses" in data


# Form Operations Tests


@pytest.mark.e2e
def test_list_lexeme_forms(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: List all forms for a lexeme."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # List forms
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    assert response.status_code == 200
    data = response.json()
    assert "forms" in data
    assert len(data["forms"]) > 0


@pytest.mark.e2e
def test_get_single_form(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: Get single form by ID."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get form ID from lexeme
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    assert response.status_code == 200
    forms_data = response.json()
    form_id = forms_data["forms"][0]["id"]

    # Get single form
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/forms/{form_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


@pytest.mark.e2e
def test_delete_form(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: Delete a form by ID."""
    # Create lexeme with 2 forms
    lexeme_data = {
        **sample_lexeme_data,
        "forms": [
            {
                "id": "L1-F1",
                "representations": {"en": {"language": "en", "value": "form1"}},
                "grammaticalFeatures": ["Q110786"],
            },
            {
                "id": "L1-F2",
                "representations": {"en": {"language": "en", "value": "form2"}},
                "grammaticalFeatures": ["Q110786"],
            },
        ],
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get forms
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    forms_data = response.json()
    form_id = forms_data["forms"][0]["id"]

    # Delete form
    response = e2e_api_client.delete(
        f"{e2e_base_url}/representations/entities/lexemes/forms/{form_id}",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify deletion
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    forms_data = response.json()
    assert len(forms_data["forms"]) == 1


@pytest.mark.e2e
def test_get_all_form_representations(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Get all representations for a form."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get form ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    forms_data = response.json()
    form_id = forms_data["forms"][0]["id"]

    # Get all representations
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/forms/{form_id}/representation"
    )
    assert response.status_code == 200
    data = response.json()
    assert "representations" in data


@pytest.mark.e2e
def test_get_form_representation_by_language(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Get representation for a form in specific language."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get form ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    forms_data = response.json()
    form_id = forms_data["forms"][0]["id"]

    # Get representation by language
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/forms/{form_id}/representation/en"
    )
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert data["value"] == "tests"


@pytest.mark.e2e
def test_update_form_representation(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Update form representation for language."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get form ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    forms_data = response.json()
    form_id = forms_data["forms"][0]["id"]

    # Update representation
    update_data = {"language": "en", "value": "updated representation"}
    response = e2e_api_client.put(
        f"{e2e_base_url}/representations/entities/lexemes/forms/{form_id}/representation/en",
        json=update_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify update
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/forms/{form_id}/representation/en"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "updated representation"


@pytest.mark.e2e
def test_delete_form_representation(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Delete form representation for language."""
    # Create lexeme with multiple language representations
    lexeme_data = {
        **sample_lexeme_data,
        "forms": [
            {
                "id": "L1-F1",
                "representations": {
                    "en": {"language": "en", "value": "english"},
                    "de": {"language": "de", "value": "deutsch"},
                },
                "grammaticalFeatures": ["Q110786"],
            }
        ],
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get form ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/forms"
    )
    forms_data = response.json()
    form_id = forms_data["forms"][0]["id"]

    # Delete representation
    response = e2e_api_client.delete(
        f"{e2e_base_url}/representations/entities/lexemes/forms/{form_id}/representation/de",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200


# Sense Operations Tests


@pytest.mark.e2e
def test_list_lexeme_senses(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: List all senses for a lexeme."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # List senses
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    assert response.status_code == 200
    data = response.json()
    assert "senses" in data
    assert len(data["senses"]) > 0


@pytest.mark.e2e
def test_get_single_sense(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: Get single sense by ID."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get sense ID from lexeme
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    assert response.status_code == 200
    senses_data = response.json()
    sense_id = senses_data["senses"][0]["id"]

    # Get single sense
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/senses/{sense_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


@pytest.mark.e2e
def test_delete_sense(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: Delete a sense by ID."""
    # Create lexeme with 2 senses
    lexeme_data = {
        **sample_lexeme_data,
        "senses": [
            {"id": "L1-S1", "glosses": {"en": {"language": "en", "value": "sense1"}}},
            {"id": "L1-S2", "glosses": {"en": {"language": "en", "value": "sense2"}}},
        ],
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get senses
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    senses_data = response.json()
    sense_id = senses_data["senses"][0]["id"]

    # Delete sense
    response = e2e_api_client.delete(
        f"{e2e_base_url}/representations/entities/lexemes/senses/{sense_id}",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify deletion
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    senses_data = response.json()
    assert len(senses_data["senses"]) == 1


@pytest.mark.e2e
def test_get_all_sense_glosses(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Get all glosses for a sense."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get sense ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    senses_data = response.json()
    sense_id = senses_data["senses"][0]["id"]

    # Get all glosses
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/senses/{sense_id}/glosses"
    )
    assert response.status_code == 200
    data = response.json()
    assert "glosses" in data


@pytest.mark.e2e
def test_get_sense_gloss_by_language(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Get gloss for a sense in specific language."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get sense ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    senses_data = response.json()
    sense_id = senses_data["senses"][0]["id"]

    # Get gloss by language
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/senses/{sense_id}/glosses/en"
    )
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert data["value"] == "A test sense"


@pytest.mark.e2e
def test_update_sense_gloss(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: Update sense gloss for language."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get sense ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    senses_data = response.json()
    sense_id = senses_data["senses"][0]["id"]

    # Update gloss
    update_data = {"language": "en", "value": "updated gloss"}
    response = e2e_api_client.put(
        f"{e2e_base_url}/representations/entities/lexemes/senses/{sense_id}/glosses/en",
        json=update_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Verify update
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/senses/{sense_id}/glosses/en"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "updated gloss"


@pytest.mark.e2e
def test_delete_sense_gloss(e2e_api_client, e2e_base_url, sample_lexeme_data) -> None:
    """E2E test: Delete sense gloss for language."""
    # Create lexeme with multiple language glosses
    lexeme_data = {
        **sample_lexeme_data,
        "senses": [
            {
                "id": "L1-S1",
                "glosses": {
                    "en": {"language": "en", "value": "english gloss"},
                    "de": {"language": "de", "value": "deutsch gloss"},
                },
            }
        ],
    }
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200
    lexeme_id = response.json()["id"]

    # Get sense ID
    response = e2e_api_client.get(
        f"{e2e_base_url}/representations/entities/lexemes/{lexeme_id}/senses"
    )
    senses_data = response.json()
    sense_id = senses_data["senses"][0]["id"]

    # Delete gloss
    response = e2e_api_client.delete(
        f"{e2e_base_url}/representations/entities/lexemes/senses/{sense_id}/glosses/de",
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200


# Batch Operations Tests


@pytest.mark.e2e
def test_get_form_representations_batch(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Fetch form representations by hash(es)."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Get batch representations (may return empty if no hashes exist yet)
    response = e2e_api_client.get(f"{e2e_base_url}/representations/123,456")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.e2e
def test_get_sense_glosses_batch(
    e2e_api_client, e2e_base_url, sample_lexeme_data
) -> None:
    """E2E test: Fetch sense glosses by hash(es)."""
    # Create lexeme
    response = e2e_api_client.post(
        f"{e2e_base_url}/representations/entities/lexemes",
        json=sample_lexeme_data,
        headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    # Get batch glosses (may return empty if no hashes exist yet)
    response = e2e_api_client.get(f"{e2e_base_url}/representations/123,456")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
