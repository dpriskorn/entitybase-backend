"""Tests for models.rest_api.utils module."""

import pytest
from fastapi import HTTPException


class TestRaiseValidationError:
    """Test suite for the raise_validation_error function."""

    def test_raises_http_exception_in_prod_environment(self, monkeypatch):
        """Test that HTTPException is raised in production environment."""
        from models.rest_api.utils import raise_validation_error

        monkeypatch.setenv("ENVIRONMENT", "prod")

        message = "Test validation error"
        status_code = 422

        with pytest.raises(HTTPException) as exc_info:
            raise_validation_error(message, status_code=status_code)

        assert exc_info.value.status_code == status_code
        assert exc_info.value.detail == message

    def test_default_status_code_is_400(self, monkeypatch):
        """Test that default status code is 400."""
        from models.rest_api.utils import raise_validation_error

        monkeypatch.setenv("ENVIRONMENT", "prod")

        message = "Test validation error"

        with pytest.raises(HTTPException) as exc_info:
            raise_validation_error(message)

        assert exc_info.value.status_code == 400

    def test_case_insensitive_environment_check(self, monkeypatch):
        """Test that environment check is case-insensitive."""
        from models.rest_api.utils import raise_validation_error

        monkeypatch.setenv("ENVIRONMENT", "PROD")

        with pytest.raises(HTTPException):
            raise_validation_error("test")

        monkeypatch.setenv("ENVIRONMENT", "Prod")

        with pytest.raises(HTTPException):
            raise_validation_error("test")

        monkeypatch.setenv("ENVIRONMENT", "PROD")

        with pytest.raises(HTTPException):
            raise_validation_error("test")


class TestInferEntityTypeFromId:
    """Test suite for the infer_entity_type_from_id function."""

    def test_infers_item_type(self):
        """Test inferring ITEM from Q-prefixed ID."""
        from models.rest_api.utils import infer_entity_type_from_id
        from models.data.infrastructure.s3.enums import EntityType

        result = infer_entity_type_from_id("Q12345")

        assert result == EntityType.ITEM

    def test_infers_property_type(self):
        """Test inferring PROPERTY from P-prefixed ID."""
        from models.rest_api.utils import infer_entity_type_from_id
        from models.data.infrastructure.s3.enums import EntityType

        result = infer_entity_type_from_id("P12345")

        assert result == EntityType.PROPERTY

    def test_infers_lexeme_type(self):
        """Test inferring LEXEME from L-prefixed ID."""
        from models.rest_api.utils import infer_entity_type_from_id
        from models.data.infrastructure.s3.enums import EntityType

        result = infer_entity_type_from_id("L12345")

        assert result == EntityType.LEXEME

    def test_invalid_format_returns_none(self):
        """Test that invalid IDs return None."""
        from models.rest_api.utils import infer_entity_type_from_id

        assert infer_entity_type_from_id("XYZ") is None
        assert infer_entity_type_from_id("") is None
        assert infer_entity_type_from_id("12345") is None


class TestValidateQid:
    """Test suite for the validate_qid function."""

    def test_valid_qid_passes(self):
        """Test validating a valid QID."""
        from models.rest_api.utils import validate_qid

        validate_qid("Q12345", "test_field")
        assert True  # No exception raised

    def test_empty_value_raises_error(self):
        """Test that empty value raises error."""
        from models.rest_api.utils import validate_qid

        with pytest.raises(HTTPException) as exc_info:
            validate_qid("", "test_field")

        assert exc_info.value.status_code == 400
        assert "required" in exc_info.value.detail

    def test_invalid_format_raises_error(self):
        """Test that invalid QID format raises error."""
        from models.rest_api.utils import validate_qid

        with pytest.raises(HTTPException) as exc_info:
            validate_qid("invalid", "test_field")

        assert exc_info.value.status_code == 400
        assert "valid QID format" in exc_info.value.detail


class TestValidateStateClients:
    """Test suite for the validate_state_clients function."""

    def test_valid_state_passes(self):
        """Test validating a state with required clients."""
        from unittest.mock import MagicMock
        from models.rest_api.utils import validate_state_clients

        mock_state = MagicMock()
        mock_state.mysql_client = MagicMock()
        mock_state.s3_client = MagicMock()

        validate_state_clients(mock_state)
        assert True  # No exception raised

    def test_missing_mysql_client_raises_error(self):
        """Test that missing mysql_client raises error."""
        from unittest.mock import MagicMock
        from models.rest_api.utils import validate_state_clients

        mock_state = MagicMock()
        del mock_state.mysql_client

        with pytest.raises(HTTPException) as exc_info:
            validate_state_clients(mock_state)

        assert exc_info.value.status_code == 500

    def test_missing_s3_client_raises_error(self):
        """Test that missing s3_client raises error."""
        from unittest.mock import MagicMock
        from models.rest_api.utils import validate_state_clients

        mock_state = MagicMock()
        del mock_state.s3_client

        with pytest.raises(HTTPException) as exc_info:
            validate_state_clients(mock_state)

        assert exc_info.value.status_code == 500
