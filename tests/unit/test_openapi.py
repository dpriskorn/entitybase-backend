"""Test OpenAPI schema generation for the FastAPI application."""

from models.rest_api.main import app


class TestOpenAPISchema:
    """Test OpenAPI schema generation for the FastAPI application."""

    def test_openapi_schema_generation(self):
        """Test that OpenAPI schema can be generated without errors."""
        # This should not raise PydanticInvalidForJsonSchema
        schema = app.openapi()

        # Basic validation
        assert isinstance(schema, dict)
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_openapi_schema_structure(self):
        """Test that the generated schema has required OpenAPI structure."""
        schema = app.openapi()

        # Check OpenAPI version
        assert schema["openapi"].startswith("3.")

        # Check info section
        assert "title" in schema["info"]
        assert "version" in schema["info"]

        # Check paths exist
        assert isinstance(schema["paths"], dict)
        assert len(schema["paths"]) > 0

    def test_openapi_schema_components(self):
        """Test that schema includes components/schemas for Pydantic models."""
        schema = app.openapi()

        # Should have components section
        assert "components" in schema
        assert "schemas" in schema["components"]

        # Should include our main response models
        schemas = schema["components"]["schemas"]
        expected_models = ["EntityResponse", "QualifierResponse", "ReferenceResponse"]

        for model in expected_models:
            assert model in schemas, f"Missing {model} in OpenAPI schemas"