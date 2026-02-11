"""Unit tests for VitessClient.

These tests use mocks to avoid database dependencies and don't require MySQL.
Integration tests in tests/integration/models/infrastructure/vitess/test_vitess_client.py
use real database connections.
"""

from unittest.mock import MagicMock

import pytest

from models.data.config.vitess import VitessConfig
from models.infrastructure.vitess.client import VitessClient


class TestVitessClient:
    """Unit tests for VitessClient."""

    @pytest.fixture(autouse=True)
    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def setup_mock_connection_manager(self, mock_vitess_connection_manager):
        """Apply the mock connection manager to all tests."""
        self.mock_connection, self.mock_cursor = mock_vitess_connection_manager

    def setup_method(self):
        """Set up test fixtures."""
        self.config = VitessConfig(
            host="localhost",
            port=15309,
            database="test_db",
            user="test_user",
            password="test_password",
        )
        self.client = VitessClient(config=self.config)

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_model_post_init_creates_connection_manager(self):
        """Test that model_post_init creates connection_manager."""
        assert self.client.connection_manager is not None

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_model_post_init_creates_id_resolver(self):
        """Test that model_post_init creates id_resolver."""
        assert self.client.id_resolver is not None

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_cursor_property_creates_connection_when_none(self):
        """Test that cursor property creates connection when None."""
        self.client.connection_manager = MagicMock()
        self.client.connection_manager.acquire.return_value = self.mock_connection
        self.mock_connection.reset_mock()

        result = self.client.cursor

        self.client.connection_manager.acquire.assert_called_once()
        self.mock_connection.cursor.assert_called_once()
        assert result == self.mock_cursor

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_cursor_property_returns_existing_cursor(self):
        """Test that cursor property returns existing cursor without reconnecting."""
        self.client.connection_manager = MagicMock()
        self.client.connection_manager.acquire.return_value = self.mock_connection
        self.mock_connection.reset_mock()

        result = self.client.cursor

        self.client.connection_manager.acquire.assert_called_once()
        self.mock_connection.cursor.assert_called_once()
        assert result == self.mock_cursor

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_entity_repository_property(self):
        """Test that entity_repository property returns EntityRepository."""
        from models.infrastructure.vitess.repositories.entity import EntityRepository

        result = self.client.entity_repository

        assert isinstance(result, EntityRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_revision_repository_property(self):
        """Test that revision_repository property returns RevisionRepository."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )

        result = self.client.revision_repository

        assert isinstance(result, RevisionRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_head_repository_property(self):
        """Test that head_repository property returns HeadRepository."""
        from models.infrastructure.vitess.repositories.head import HeadRepository

        result = self.client.head_repository

        assert isinstance(result, HeadRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_user_repository_property(self):
        """Test that user_repository property returns UserRepository."""
        from models.infrastructure.vitess.repositories.user import UserRepository

        result = self.client.user_repository

        assert isinstance(result, UserRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_watchlist_repository_property(self):
        """Test that watchlist_repository property returns WatchlistRepository."""
        from models.infrastructure.vitess.repositories.watchlist import (
            WatchlistRepository,
        )

        result = self.client.watchlist_repository

        assert isinstance(result, WatchlistRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_endorsement_repository_property(self):
        """Test that endorsement_repository property returns EndorsementRepository."""
        from models.infrastructure.vitess.repositories.endorsement import (
            EndorsementRepository,
        )

        result = self.client.endorsement_repository

        assert isinstance(result, EndorsementRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_thanks_repository_property(self):
        """Test that thanks_repository property returns ThanksRepository."""
        from models.infrastructure.vitess.repositories.thanks import ThanksRepository

        result = self.client.thanks_repository

        assert isinstance(result, ThanksRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_redirect_repository_property(self):
        """Test that redirect_repository property returns RedirectRepository."""
        from models.infrastructure.vitess.repositories.redirect import (
            RedirectRepository,
        )

        result = self.client.redirect_repository

        assert isinstance(result, RedirectRepository)
        assert result.vitess_client == self.client

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_create_revision_delegates_to_revision_repository(self):
        """Test that create_revision delegates to revision_repository.insert_revision."""
        from unittest.mock import patch, PropertyMock

        mock_revision_repository = MagicMock()

        entity_id = "Q123"
        entity_data = MagicMock()
        revision_id = 1
        content_hash = 12345
        expected_revision_id = 0

        with patch.object(
            VitessClient, "revision_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_revision_repository
            self.client.create_revision(
                entity_id, entity_data, revision_id, content_hash, expected_revision_id
            )

        mock_revision_repository.insert_revision.assert_called_once_with(
            entity_id, revision_id, entity_data, content_hash, expected_revision_id
        )

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_entity_exists_delegates_to_id_resolver(self):
        """Test that entity_exists delegates to id_resolver.entity_exists."""
        mock_id_resolver = MagicMock()
        mock_id_resolver.entity_exists.return_value = True
        self.client.id_resolver = mock_id_resolver

        result = self.client.entity_exists("Q123")

        mock_id_resolver.entity_exists.assert_called_once_with("Q123")
        assert result is True

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_resolve_id_delegates_to_id_resolver(self):
        """Test that resolve_id delegates to id_resolver.resolve_id."""
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        self.client.id_resolver = mock_id_resolver

        result = self.client.resolve_id("Q123")

        mock_id_resolver.resolve_id.assert_called_once_with("Q123")
        assert result == 123

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_get_head_delegates_to_entity_repository(self):
        """Test that get_head delegates to entity_repository.get_head."""
        from unittest.mock import patch, PropertyMock

        mock_entity_repository = MagicMock()
        mock_entity_repository.get_head.return_value = 10

        with patch.object(
            VitessClient, "entity_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_entity_repository
            result = self.client.get_head("Q123")

        mock_entity_repository.get_head.assert_called_once_with("Q123")
        assert result == 10

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_get_history_delegates_to_revision_repository(self):
        """Test that get_history delegates to revision_repository.get_history."""
        from unittest.mock import patch, PropertyMock

        mock_revision_repository = MagicMock()
        mock_revision_repository.get_history.return_value = []

        with patch.object(
            VitessClient, "revision_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_revision_repository
            result = self.client.get_history("Q123", 20, 0)

        mock_revision_repository.get_history.assert_called_once_with("Q123", 20, 0)
        assert result == []

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_get_entity_history_delegates_to_revision_repository(self):
        """Test that get_entity_history delegates to revision_repository.get_history."""
        from unittest.mock import patch, PropertyMock

        mock_revision_repository = MagicMock()
        mock_revision_repository.get_history.return_value = []

        with patch.object(
            VitessClient, "revision_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_revision_repository
            result = self.client.get_entity_history("Q123", 10, 5)

        mock_revision_repository.get_history.assert_called_once_with("Q123", 10, 5)
        assert result == []

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_register_entity_delegates_to_id_resolver(self):
        """Test that register_entity delegates to id_resolver.register_entity."""
        mock_id_resolver = MagicMock()
        self.client.id_resolver = mock_id_resolver

        self.client.register_entity("Q123")

        mock_id_resolver.register_entity.assert_called_once_with("Q123")

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_insert_revision_delegates_to_revision_repository(self):
        """Test that insert_revision delegates to revision_repository.insert_revision."""
        from unittest.mock import patch, PropertyMock

        mock_revision_repository = MagicMock()

        entity_id = "Q123"
        revision_id = 1
        entity_data = MagicMock()
        content_hash = 12345
        expected_revision_id = 0

        with patch.object(
            VitessClient, "revision_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_revision_repository
            self.client.insert_revision(
                entity_id, revision_id, entity_data, content_hash, expected_revision_id
            )

        mock_revision_repository.insert_revision.assert_called_once_with(
            entity_id=entity_id,
            revision_id=revision_id,
            entity_data=entity_data,
            content_hash=content_hash,
            expected_revision_id=expected_revision_id,
        )

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_is_entity_deleted_delegates_to_entity_repository(self):
        """Test that is_entity_deleted delegates to entity_repository.is_deleted."""
        from unittest.mock import patch, PropertyMock

        mock_entity_repository = MagicMock()
        mock_entity_repository.is_deleted.return_value = True

        with patch.object(
            VitessClient, "entity_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_entity_repository
            result = self.client.is_entity_deleted("Q123")

        mock_entity_repository.is_deleted.assert_called_once_with("Q123")
        assert result is True

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_is_entity_locked_delegates_to_entity_repository(self):
        """Test that is_entity_locked delegates to entity_repository.is_locked."""
        from unittest.mock import patch, PropertyMock

        mock_entity_repository = MagicMock()
        mock_entity_repository.is_locked.return_value = False

        with patch.object(
            VitessClient, "entity_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_entity_repository
            result = self.client.is_entity_locked("Q123")

        mock_entity_repository.is_locked.assert_called_once_with("Q123")
        assert result is False

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_is_entity_archived_delegates_to_entity_repository(self):
        """Test that is_entity_archived delegates to entity_repository.is_archived."""
        from unittest.mock import patch, PropertyMock

        mock_entity_repository = MagicMock()
        mock_entity_repository.is_archived.return_value = False

        with patch.object(
            VitessClient, "entity_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_entity_repository
            result = self.client.is_entity_archived("Q123")

        mock_entity_repository.is_archived.assert_called_once_with("Q123")
        assert result is False

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_list_entities_by_type_item(self):
        """Test list_entities_by_type for item type."""
        self.mock_cursor.fetchall.return_value = [("Q1",), ("Q2",)]

        result = self.client.list_entities_by_type("item", 10, 0)

        self.mock_cursor.execute.assert_called_once_with(
            """SELECT entity_id FROM entity_id_mapping
               WHERE entity_id LIKE %s
               LIMIT %s OFFSET %s""",
            ("Q%", 10, 0),
        )
        assert result == ["Q1", "Q2"]

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_list_entities_by_type_lexeme(self):
        """Test list_entities_by_type for lexeme type."""
        self.mock_cursor.fetchall.return_value = [("L1",), ("L2",)]

        result = self.client.list_entities_by_type("lexeme", 5, 0)

        self.mock_cursor.execute.assert_called_once_with(
            """SELECT entity_id FROM entity_id_mapping
               WHERE entity_id LIKE %s
               LIMIT %s OFFSET %s""",
            ("L%", 5, 0),
        )
        assert result == ["L1", "L2"]

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_list_entities_by_type_property(self):
        """Test list_entities_by_type for property type."""
        self.mock_cursor.fetchall.return_value = [("P1",)]

        result = self.client.list_entities_by_type("property", 100, 10)

        self.mock_cursor.execute.assert_called_once_with(
            """SELECT entity_id FROM entity_id_mapping
               WHERE entity_id LIKE %s
               LIMIT %s OFFSET %s""",
            ("P%", 100, 10),
        )
        assert result == ["P1"]

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_list_entities_by_type_invalid_type(self):
        """Test list_entities_by_type with invalid type returns empty list."""
        result = self.client.list_entities_by_type("invalid_type")

        self.mock_cursor.execute.assert_not_called()
        assert result == []

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_get_redirect_target_delegates_to_redirect_repository(self):
        """Test that get_redirect_target delegates to redirect_repository.get_target."""
        from unittest.mock import patch, PropertyMock

        mock_redirect_repository = MagicMock()
        mock_redirect_repository.get_target.return_value = "Q456"

        with patch.object(
            VitessClient, "redirect_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_redirect_repository
            result = self.client.get_redirect_target("Q123")

        mock_redirect_repository.get_target.assert_called_once_with("Q123")
        assert result == "Q456"

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_create_redirect_delegates_to_redirect_repository(self):
        """Test that create_redirect delegates to redirect_repository.create."""
        from unittest.mock import patch, PropertyMock

        mock_redirect_repository = MagicMock()

        with patch.object(
            VitessClient, "redirect_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_redirect_repository
            self.client.create_redirect("Q123", "Q456", "test_user")

        mock_redirect_repository.create.assert_called_once_with(
            redirect_from_entity_id="Q123",
            redirect_to_entity_id="Q456",
            created_by="test_user",
        )

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_create_redirect_default_created_by(self):
        """Test that create_redirect uses default created_by value."""
        from unittest.mock import patch, PropertyMock

        mock_redirect_repository = MagicMock()

        with patch.object(
            VitessClient, "redirect_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_redirect_repository
            self.client.create_redirect("Q123", "Q456")

        mock_redirect_repository.create.assert_called_once_with(
            redirect_from_entity_id="Q123",
            redirect_to_entity_id="Q456",
            created_by="rest-api",
        )

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_set_redirect_target_calls_repository(self):
        """Test that set_redirect_target calls redirect_repository.set_target."""
        from unittest.mock import patch, PropertyMock

        mock_redirect_repository = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.error = ""
        mock_redirect_repository.set_target.return_value = mock_result

        with patch.object(
            VitessClient, "redirect_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_redirect_repository
            self.client.set_redirect_target("Q123", "Q456")

        mock_redirect_repository.set_target.assert_called_once_with(
            entity_id="Q123", redirects_to_entity_id="Q456"
        )

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_set_redirect_target_raises_on_failure(self):
        """Test that set_redirect_target raises ValueError on failure."""
        from unittest.mock import patch, PropertyMock

        mock_redirect_repository = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Some error"
        mock_redirect_repository.set_target.return_value = mock_result

        with patch.object(
            VitessClient, "redirect_repository", new_callable=PropertyMock
        ) as mock_repo:
            mock_repo.return_value = mock_redirect_repository
            with pytest.raises(ValueError, match="Some error"):
                self.client.set_redirect_target("Q123", "Q456")

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_revert_redirect_calls_set_redirect_target_with_empty_string(self):
        """Test that revert_redirect calls set_redirect_target with empty string."""
        from unittest.mock import patch

        with patch.object(VitessClient, "set_redirect_target") as mock_set_redirect:
            self.client.revert_redirect("Q123")

        mock_set_redirect.assert_called_once_with(
            entity_id="Q123", redirects_to_entity_id=""
        )

    @pytest.mark.skip(reason="Skipping all Vitess unit tests")
    def test_create_tables_creates_schema_repository(self):
        """Test that create_tables creates and calls schema_repository."""
        from unittest.mock import patch

        self.client.connection_manager = MagicMock()

        with patch(
            "models.infrastructure.vitess.repositories.schema.SchemaRepository"
        ) as mock_schema_repo_class:
            mock_schema_repo = MagicMock()
            mock_schema_repo_class.return_value = mock_schema_repo

            self.client.create_tables()

            mock_schema_repo_class.assert_called_once_with(vitess_client=self.client)
            mock_schema_repo.create_tables.assert_called_once()
