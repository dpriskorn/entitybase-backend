"""Unit tests for ThanksRepository."""

from unittest.mock import MagicMock

from models.data.infrastructure.vitess.records.thanks import ThankItem
from models.infrastructure.vitess.repositories.thanks import ThanksRepository


class TestThanksRepository:
    """Unit tests for ThanksRepository."""

    def test_send_thank_success(self):
        """Test successful thank sending."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), None]  # author, no existing thank
        mock_cursor.lastrowid = 789
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is True
        assert result.data == 789

    def test_send_thank_entity_not_found(self):
        """Test sending thank when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q999", 1)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_send_thank_revision_not_found(self):
        """Test sending thank when revision not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = None  # no revision
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Revision not found" in result.error

    def test_send_thank_own_revision(self):
        """Test sending thank to own revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (111,)  # same user
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Cannot thank your own revision" in result.error

    def test_send_thank_already_thanked(self):
        """Test sending thank when already thanked."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), (1,)]  # author, existing thank
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Already thanked" in result.error

    def test_send_thank_invalid_params(self):
        """Test sending thank with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(0, "Q1", 1)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_thanks_received_invalid_params(self):
        """Test getting thanks received with invalid params."""
        mock_vitess_client = MagicMock()

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_received(0)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_revision_thanks_success(self):
        """Test getting thanks for a revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = [(1, 111, 222, "Q1", 1, "2023-01-01")]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision_thanks("Q1", 1)

        assert result.success is True
        assert len(result.data) == 1
        assert isinstance(result.data[0], ThankItem)

    def test_get_thanks_received_database_error(self):
        """Test getting thanks received with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_received(222)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_thanks_sent_database_error(self):
        """Test getting thanks sent with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_sent(111)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_revision_thanks_database_error(self):
        """Test getting revision thanks with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision_thanks("Q1", 1)

        assert result.success is False
        assert "DB error" in result.error

    def test_send_thank_already_sent(self):
        """Test sending thank when already sent."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), (1,)]  # author, existing thank
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Already thanked" in result.error

    def test_send_thank_database_error(self):
        """Test sending thank with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_thanks_sent_invalid_params(self):
        """Test getting thanks sent with invalid params."""
        mock_vitess_client = MagicMock()

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_sent(0)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_revision_thanks_no_thanks(self):
        """Test getting thanks for revision with none."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = []  # no thanks
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision_thanks("Q1", 1)

        assert result.success is True
        assert result.data == []

    def test_get_revision_thanks_entity_not_found(self):
        """Test getting thanks for revision when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision_thanks("Q999", 1)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_send_thank_logging_success(self, caplog):
        """Test that sending thank logs debug message."""
        import logging

        caplog.set_level(logging.DEBUG)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), None]  # author, no existing thank
        mock_cursor.lastrowid = 789
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        repo.send_thank(111, "Q1", 1)

        assert "Sending thank from user 111 for Q1:1" in caplog.text

    def test_get_thanks_received_logging_error(self, caplog):
        """Test that getting thanks received logs error on failure."""
        import logging

        caplog.set_level(logging.ERROR)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        repo.get_thanks_received(222)

        assert "Error getting thanks received: DB error" in caplog.text

    def test_get_thanks_sent_logging_error(self, caplog):
        """Test that getting thanks sent logs error on failure."""
        import logging

        caplog.set_level(logging.ERROR)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        repo.get_thanks_sent(111)

        assert "Error getting thanks sent: DB error" in caplog.text

    def test_get_revision_thanks_logging_error(self, caplog):
        """Test that getting revision thanks logs error on failure."""
        import logging

        caplog.set_level(logging.ERROR)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        repo.get_revision_thanks("Q1", 1)

        assert "Error getting revision thanks: DB error" in caplog.text
