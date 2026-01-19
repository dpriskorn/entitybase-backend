from models.rest_api.v1.entitybase.handlers.entity.types import logger


class TestTypes:
    def test_logger_defined(self) -> None:
        """Test that logger is properly defined."""
        assert logger is not None
        assert logger.name == "models.rest_api.v1.entitybase.handlers.entity.types"
