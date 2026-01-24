"""Unit tests for reference and qualifier models."""

import pytest
from pydantic import ValidationError

from models.internal_representation.reference_qualifier_models import ReferenceModel, QualifierModel


class TestReferenceModel:
    """Unit tests for ReferenceModel."""

    def test_reference_model_creation_valid(self):
        """Test creating a valid ReferenceModel."""
        snaks = {"P123": [{"snaktype": "value", "property": "P123", "datavalue": {"type": "string", "value": "test"}}]}
        snaks_order = ["P123"]

        ref = ReferenceModel(
            hash="abc123",
            snaks=snaks,
            snaks_order=snaks_order,
        )

        assert ref.hash == "abc123"
        assert ref.snaks == snaks
        assert ref.snaks_order == snaks_order

    def test_reference_model_missing_hash(self):
        """Test ReferenceModel creation without hash."""
        snaks = {"P123": []}
        snaks_order = []

        with pytest.raises(ValidationError):
            ReferenceModel(
                snaks=snaks,
                snaks_order=snaks_order,
                hash=None
            )

    def test_reference_model_empty_snaks(self):
        """Test ReferenceModel with empty snaks."""
        snaks = {}
        snaks_order = []

        ref = ReferenceModel(
            hash="def456",
            snaks=snaks,
            snaks_order=snaks_order,
        )

        assert ref.snaks == {}
        assert ref.snaks_order == []


class TestQualifierModel:
    """Unit tests for QualifierModel."""

    def test_qualifier_model_creation_valid(self):
        """Test creating a valid QualifierModel."""
        qualifiers = {"P123": [{"snaktype": "value", "property": "P123", "datavalue": {"type": "string", "value": "qualifier"}}]}

        qual = QualifierModel(qualifiers=qualifiers)

        assert qual.qualifiers == qualifiers

    def test_qualifier_model_missing_qualifiers(self):
        """Test QualifierModel creation without qualifiers."""
        with pytest.raises(ValueError):
            # noinspection PyArgumentList
            QualifierModel()

    def test_qualifier_model_empty_qualifiers(self):
        """Test QualifierModel with empty qualifiers."""
        qual = QualifierModel(qualifiers={})

        assert qual.qualifiers == {}
