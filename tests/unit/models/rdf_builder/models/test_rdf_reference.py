import pytest
from unittest.mock import patch
from pydantic import ValidationError

pytestmark = pytest.mark.unit

from models.rdf_builder.models.rdf_reference import RDFReference
from models.internal_representation.references import Reference


class TestRDFReference:
    def test_rdf_reference_creation_with_hash(self) -> None:
        """Test creating RDFReference with valid hash."""
        reference = Reference(hash="a4d108601216cffd2ff1819ccf12b483486b62e7")
        rdf_ref = RDFReference(reference=reference, statement_uri="wds:Q42-12345678-ABCD")
        assert rdf_ref.statement_uri == "wds:Q42-12345678-ABCD"
        assert rdf_ref.hash == "a4d108601216cffd2ff1819ccf12b483486b62e7"

    def test_get_reference_uri(self) -> None:
        """Test generating reference URI."""
        reference = Reference(hash="test123")
        rdf_ref = RDFReference(reference=reference, statement_uri="wds:Q1-abcdef")
        assert rdf_ref.get_reference_uri == "wdref:test123"

    def test_rdf_reference_no_hash_raises_error(self) -> None:
        """Test that missing hash raises validation error."""
        reference = Reference(hash="")
        with patch(
            "models.rdf_builder.models.rdf_reference.raise_validation_error"
        ) as mock_raise:
            RDFReference(reference=reference, statement_uri="wds:Q42-test")
            mock_raise.assert_called_once()
            call_args = mock_raise.call_args[0][0]
            assert "Reference has no hash" in call_args
            assert "wds:Q42-test" in call_args

    def test_rdf_reference_none_hash_raises_error(self) -> None:
        """Test that None hash raises validation error."""
        with pytest.raises(ValidationError):
            # noinspection PyTypeChecker
            reference = Reference(hash=None)
