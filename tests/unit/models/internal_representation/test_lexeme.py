"""Unit tests for Lexeme models."""

import pytest

from models.internal_representation.lexeme import (
    FormRepresentation,
    LexemeForm,
    SenseGloss,
    LexemeSense,
)


class TestFormRepresentation:
    """Unit tests for FormRepresentation."""

    def test_form_representation_valid(self) -> None:
        """Test valid FormRepresentation with language and value."""
        form = FormRepresentation(language="en", value="cats")

        assert form.language == "en"
        assert form.value == "cats"

    def test_form_representation_missing_language(self) -> None:
        """Test FormRepresentation fails validation without language."""
        with pytest.raises(ValueError):
            FormRepresentation(value="cats")

    def test_form_representation_missing_value(self) -> None:
        """Test FormRepresentation fails validation without value."""
        with pytest.raises(ValueError):
            FormRepresentation(language="en")

    def test_form_representation_frozen(self) -> None:
        """Test FormRepresentation is immutable (frozen=True)."""
        form = FormRepresentation(language="en", value="cats")

        with pytest.raises(Exception):  # Frozen instance error
            form.language = "de"


class TestLexemeForm:
    """Unit tests for LexemeForm."""

    def test_lexeme_form_valid(self) -> None:
        """Test valid LexemeForm with ID, representations, and grammatical features."""
        representation = FormRepresentation(language="en", value="cats")
        form = LexemeForm(
            id="L123-F1",
            representations={"en": representation},
            grammaticalFeatures=["Q110786"],
        )

        assert form.id == "L123-F1"
        assert "en" in form.representations
        assert form.representations["en"] == representation
        assert form.grammatical_features == ["Q110786"]

    def test_lexeme_form_invalid_id_format(self) -> None:
        """Test LexemeForm fails validation with invalid ID format."""
        with pytest.raises(ValueError):
            LexemeForm(
                id="F1",  # Missing L{num} prefix
                representations={},
            )

    def test_lexeme_form_without_representations(self) -> None:
        """Test LexemeForm with empty representations dict."""
        form = LexemeForm(id="L123-F1", representations={})

        assert form.representations == {}

    def test_lexeme_form_with_claims(self) -> None:
        """Test LexemeForm with claims dict."""
        form = LexemeForm(
            id="L123-F1",
            representations={},
            claims={"P31": [{"mainsnak": {"datavalue": {"value": "Q146"}}}]},
        )

        assert "P31" in form.claims

    def test_lexeme_form_frozen(self) -> None:
        """Test LexemeForm is immutable (frozen=True)."""
        form = LexemeForm(id="L123-F1", representations={})

        with pytest.raises(Exception):  # Frozen instance error
            form.id = "L456-F2"


class TestSenseGloss:
    """Unit tests for SenseGloss."""

    def test_sense_gloss_valid(self) -> None:
        """Test valid SenseGloss with language and value."""
        gloss = SenseGloss(language="en", value="feline animal")

        assert gloss.language == "en"
        assert gloss.value == "feline animal"

    def test_sense_gloss_missing_language(self) -> None:
        """Test SenseGloss fails validation without language."""
        with pytest.raises(ValueError):
            SenseGloss(value="feline animal")

    def test_sense_gloss_missing_value(self) -> None:
        """Test SenseGloss fails validation without value."""
        with pytest.raises(ValueError):
            SenseGloss(language="en")


class TestLexemeSense:
    """Unit tests for LexemeSense."""

    def test_lexeme_sense_valid(self) -> None:
        """Test valid LexemeSense with ID and glosses."""
        gloss = SenseGloss(language="en", value="feline animal")
        sense = LexemeSense(
            id="L123-S1",
            glosses={"en": gloss},
        )

        assert sense.id == "L123-S1"
        assert "en" in sense.glosses
        assert sense.glosses["en"] == gloss

    def test_lexeme_sense_invalid_id_format(self) -> None:
        """Test LexemeSense fails validation with invalid ID format."""
        with pytest.raises(ValueError):
            LexemeSense(
                id="S1",  # Missing L{num} prefix
                glosses={},
            )

    def test_lexeme_sense_without_glosses(self) -> None:
        """Test LexemeSense with empty glosses dict."""
        sense = LexemeSense(id="L123-S1", glosses={})

        assert sense.glosses == {}

    def test_lexeme_sense_with_claims(self) -> None:
        """Test LexemeSense with claims dict."""
        sense = LexemeSense(
            id="L123-S1",
            glosses={},
            claims={"P5137": [{"mainsnak": {"datavalue": {"value": "Q6256"}}}]},
        )

        assert "P5137" in sense.claims
