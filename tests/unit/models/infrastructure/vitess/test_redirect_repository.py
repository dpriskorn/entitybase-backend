"""Unit tests for redirect repository."""

from unittest.mock import Mock, patch
import pytest

from models.infrastructure.vitess.repositories.redirect import RedirectRepository


class TestRedirectRepository:
    """Test cases for RedirectRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection_manager = Mock()
        self.mock_id_resolver = Mock()
        self.mock_connection = Mock()
        self.mock_cursor = Mock()

        self.repository = RedirectRepository(
            self.mock_connection_manager, self.mock_id_resolver
        )

    def test_init(self) -> None:
        """Test repository initialization."""
        assert self.repository.connection_manager == self.mock_connection_manager
        assert self.repository.id_resolver == self.mock_id_resolver

    def test_set_target_success(self) -> None:
        """Test successful redirect target setting."""
        self.mock_id_resolver.resolve_id.side_effect = [100, 200]
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.rowcount = 1

        result = self.repository.set_target(self.mock_connection, "Q100", "Q200")

        assert result is True
        self.mock_id_resolver.resolve_id.assert_any_call(self.mock_connection, "Q100")
        self.mock_id_resolver.resolve_id.assert_any_call(self.mock_connection, "Q200")
        self.mock_cursor.execute.assert_called_once()

    def test_set_target_with_expected_value(self) -> None:
        """Test setting redirect target with expected value."""
        self.mock_id_resolver.resolve_id.side_effect = [100, 200]
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.rowcount = 1

        result = self.repository.set_target(
            self.mock_connection, "Q100", "Q200", expected_redirects_to=150
        )

        assert result is True
        # Verify the SQL includes the expected value condition
        call_args = self.mock_cursor.execute.call_args[0]
        assert "AND redirects_to = %s" in call_args[0]
        assert call_args[1] == (200, 100, 150)

    def test_set_target_entity_not_found(self) -> None:
        """Test setting redirect target when source entity not found."""
        self.mock_id_resolver.resolve_id.return_value = None

        with pytest.raises(Exception) as exc_info:
            self.repository.set_target(self.mock_connection, "Q100", "Q200")

        # Should call raise_validation_error
        self.mock_id_resolver.resolve_id.assert_called_once_with(
            self.mock_connection, "Q100"
        )

    def test_set_target_target_entity_not_found(self) -> None:
        """Test setting redirect target when target entity not found."""
        self.mock_id_resolver.resolve_id.side_effect = [100, None]

        with pytest.raises(Exception) as exc_info:
            self.repository.set_target(self.mock_connection, "Q100", "Q200")

        # Should call raise_validation_error for target
        assert self.mock_id_resolver.resolve_id.call_count == 2

    def test_set_target_no_rows_affected(self) -> None:
        """Test setting redirect target when no rows are affected."""
        self.mock_id_resolver.resolve_id.side_effect = [100, 200]
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.rowcount = 0

        result = self.repository.set_target(self.mock_connection, "Q100", "Q200")

        assert result is False

    def test_set_target_none_target(self) -> None:
        """Test setting redirect target to None (removing redirect)."""
        self.mock_id_resolver.resolve_id.return_value = 100
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.rowcount = 1

        result = self.repository.set_target(self.mock_connection, "Q100", None)

        assert result is True
        self.mock_id_resolver.resolve_id.assert_called_once_with(
            self.mock_connection, "Q100"
        )

    def test_create_success(self) -> None:
        """Test successful redirect creation."""
        self.mock_id_resolver.resolve_id.side_effect = [100, 200]
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )

        self.repository.create(self.mock_connection, "Q100", "Q200", "test-user")

        self.mock_id_resolver.resolve_id.assert_any_call(self.mock_connection, "Q100")
        self.mock_id_resolver.resolve_id.assert_any_call(self.mock_connection, "Q200")
        self.mock_cursor.execute.assert_called_once()

        # Verify SQL and parameters
        call_args = self.mock_cursor.execute.call_args[0]
        assert "INSERT INTO entity_redirects" in call_args[0]
        assert call_args[1] == (100, 200, "test-user")

    def test_create_default_created_by(self) -> None:
        """Test redirect creation with default created_by value."""
        self.mock_id_resolver.resolve_id.side_effect = [100, 200]
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )

        self.repository.create(self.mock_connection, "Q100", "Q200")

        call_args = self.mock_cursor.execute.call_args[0]
        assert call_args[1] == (100, 200, "rest-api")

    def test_create_source_not_found(self) -> None:
        """Test redirect creation when source entity not found."""
        self.mock_id_resolver.resolve_id.side_effect = [None, 200]

        with pytest.raises(Exception):
            self.repository.create(self.mock_connection, "Q100", "Q200")

    def test_create_target_not_found(self) -> None:
        """Test redirect creation when target entity not found."""
        self.mock_id_resolver.resolve_id.side_effect = [100, None]

        with pytest.raises(Exception):
            self.repository.create(self.mock_connection, "Q100", "Q200")

    def test_get_incoming_redirects_success(self) -> None:
        """Test getting incoming redirects successfully."""
        self.mock_id_resolver.resolve_id.return_value = 100
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.fetchall.return_value = [("Q50",), ("Q75",)]

        result = self.repository.get_incoming_redirects(self.mock_connection, "Q100")

        assert result == ["Q50", "Q75"]
        self.mock_id_resolver.resolve_id.assert_called_once_with(
            self.mock_connection, "Q100"
        )
        self.mock_cursor.execute.assert_called_once()

    def test_get_incoming_redirects_entity_not_found(self) -> None:
        """Test getting incoming redirects when entity not found."""
        self.mock_id_resolver.resolve_id.return_value = None

        result = self.repository.get_incoming_redirects(self.mock_connection, "Q100")

        assert result == []
        self.mock_id_resolver.resolve_id.assert_called_once_with(
            self.mock_connection, "Q100"
        )
        self.mock_cursor.execute.assert_not_called()

    def test_get_incoming_redirects_no_results(self) -> None:
        """Test getting incoming redirects with no results."""
        self.mock_id_resolver.resolve_id.return_value = 100
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.fetchall.return_value = []

        result = self.repository.get_incoming_redirects(self.mock_connection, "Q100")

        assert result == []

    def test_get_target_success(self) -> None:
        """Test getting redirect target successfully."""
        self.mock_id_resolver.resolve_id.return_value = 100
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.fetchone.return_value = ("Q200",)

        result = self.repository.get_target(self.mock_connection, "Q100")

        assert result == "Q200"
        self.mock_id_resolver.resolve_id.assert_called_once_with(
            self.mock_connection, "Q100"
        )
        self.mock_cursor.execute.assert_called_once()

    def test_get_target_no_redirect(self) -> None:
        """Test getting redirect target when no redirect exists."""
        self.mock_id_resolver.resolve_id.return_value = 100
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.fetchone.return_value = None

        result = self.repository.get_target(self.mock_connection, "Q100")

        assert result is None

    def test_get_target_entity_not_found(self) -> None:
        """Test getting redirect target when entity not found."""
        self.mock_id_resolver.resolve_id.return_value = None

        result = self.repository.get_target(self.mock_connection, "Q100")

        assert result is None
        self.mock_cursor.execute.assert_not_called()

    @patch("models.infrastructure.vitess.redirect_repository.logger")
    def test_debug_logging(self, mock_logger) -> None:
        """Test that debug logging is called."""
        self.mock_id_resolver.resolve_id.side_effect = [100, 200]
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )
        self.mock_cursor.rowcount = 1

        self.repository.set_target(self.mock_connection, "Q100", "Q200")

        mock_logger.debug.assert_called_with("Setting redirect target for Q100 to Q200")

    @patch("models.infrastructure.vitess.redirect_repository.logger")
    def test_create_debug_logging(self, mock_logger) -> None:
        """Test that debug logging is called for create."""
        self.mock_id_resolver.resolve_id.side_effect = [100, 200]
        self.mock_connection.cursor.return_value.__enter__.return_value = (
            self.mock_cursor
        )

        self.repository.create(self.mock_connection, "Q100", "Q200")

        mock_logger.debug.assert_called_with("Creating redirect from Q100 to Q200")
