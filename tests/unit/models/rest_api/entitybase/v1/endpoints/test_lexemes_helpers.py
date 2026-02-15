"""Unit tests for lexeme helper functions."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from models.rest_api.entitybase.v1.endpoints.lexemes import (
    _extract_numeric_suffix,
    _parse_form_id,
    _parse_sense_id,
    _validate_qid,
)


class TestFormAndSenseHelpers:
    """Test helper functions for form/sense ID parsing."""

    def test_parse_form_id_full_format(self):
        result = _parse_form_id("L42-F1")
        assert result == ("L42", "F1")

    def test_parse_form_id_short_format(self):
        result = _parse_form_id("F12")
        assert result == ("", "F12")

    def test_parse_form_id_invalid_format(self):
        with pytest.raises(HTTPException) as exc:
            _parse_form_id("invalid-id")
        assert exc.value.status_code == 400

    def test_parse_sense_id_full_format(self):
        result = _parse_sense_id("L42-S1")
        assert result == ("L42", "S1")

    def test_parse_sense_id_short_format(self):
        result = _parse_sense_id("S12")
        assert result == ("", "S12")

    def test_parse_sense_id_invalid_format(self):
        with pytest.raises(HTTPException) as exc:
            _parse_sense_id("invalid-id")
        assert exc.value.status_code == 400

    def test_extract_numeric_suffix(self):
        assert _extract_numeric_suffix("F1") == 1
        assert _extract_numeric_suffix("F12") == 12
        assert _extract_numeric_suffix("S1") == 1
        assert _extract_numeric_suffix("S42") == 42


class TestQidValidation:
    """Test QID validation helper."""

    def test_validate_qid_valid_qid(self):
        result = _validate_qid("Q1860", "language")
        assert result == "Q1860"

    def test_validate_qid_valid_qid_large_number(self):
        result = _validate_qid("Q123456789", "lexical_category")
        assert result == "Q123456789"

    def test_validate_qid_empty_string(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("", "language")
        assert exc.value.status_code == 400
        assert "required" in exc.value.detail.lower()

    def test_validate_qid_invalid_format_no_q(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("1860", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail

    def test_validate_qid_invalid_format_lowercase(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("q1860", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail

    def test_validate_qid_invalid_format_no_digits(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("Q", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail

    def test_validate_qid_invalid_format_letters(self):
        with pytest.raises(HTTPException) as exc:
            _validate_qid("Qabc", "language")
        assert exc.value.status_code == 400
        assert "valid QID format" in exc.value.detail
