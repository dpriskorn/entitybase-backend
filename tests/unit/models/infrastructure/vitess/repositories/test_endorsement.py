"""Unit tests for EndorsementRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.endorsement import EndorsementRepository


class TestEndorsementRepository:
    """Unit tests for EndorsementRepository."""

    def test_create_endorsement_statement_not_found(self):
        """Test endorsement creation when statement doesn't exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # statement not found
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is False
        assert "Statement not found" in result.error

    def test_create_endorsement_already_exists(self):
        """Test endorsement creation when already endorsed."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(1,), (1, None)]  # statement exists, existing active endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is False
        assert "Already endorsed" in result.error

    def test_create_endorsement_invalid_params(self):
        """Test endorsement creation with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(0, 789)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_withdraw_endorsement_success(self):
        """Test successful endorsement withdrawal."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (123,)  # existing endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(456, 789)

        assert result.success is True
        assert result.data == 123

    def test_withdraw_endorsement_no_active(self):
        """Test withdrawal when no active endorsement exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # no active endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(456, 789)

        assert result.success is False
        assert "No active endorsement found" in result.error

    def test_get_statement_endorsements_success(self):
        """Test getting statement endorsements."""
    pass

    def test_get_statement_endorsements_invalid_params(self):
        """Test getting endorsements with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_statement_endorsements(0)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_user_endorsement_stats_success(self):
        """Test getting user endorsement stats."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(10,), (7,)]  # total, active
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsement_stats(456)

        assert result.success is True
        assert result.data["total_endorsements_given"] == 10
        assert result.data["total_endorsements_active"] == 7

    def test_create_endorsement_reactivate_with_different_user(self):
        """Test reactivation when endorsed by different user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(456,), (1, None)]  # author, existing endorsement by different user
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(111, 789)  # different user

        assert result.success is False
        assert "Already endorsed" in result.error

    def test_withdraw_endorsement_not_found(self):
        """Test withdrawing non-existent endorsement."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # no endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(456, 789)

        assert result.success is False
        assert "No active endorsement found" in result.error







    def test_get_batch_statement_endorsement_stats_mixed(self):
        """Test batch stats with mix of statements with and without endorsements."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (789, 3, 2, 1),  # has endorsements
            # 790 has none, not in results
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([789, 790])

        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["statement_hash"] == 789
        assert result.data[0]["total_endorsements"] == 3
        assert result.data[1]["statement_hash"] == 790
        assert result.data[1]["total_endorsements"] == 0

    def test_get_statement_endorsements_database_error(self):
        """Test getting statement endorsements with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_statement_endorsements(789)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_user_endorsements_database_error(self):
        """Test getting user endorsements with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsements(456)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_user_endorsement_stats_database_error(self):
        """Test getting user endorsement stats with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsement_stats(456)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_batch_statement_endorsement_stats_database_error(self):
        """Test batch stats with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([789])

        assert result.success is False
        assert "DB error" in result.error

    def test_withdraw_endorsement_database_error(self):
        """Test withdrawal with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (123,)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(456, 789)

        assert result.success is False
        assert "DB error" in result.error

    def test_create_endorsement_reactivate_removed(self):
        """Test endorsement creation reactivating a previously removed endorsement."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(1,), (1, "2023-01-01")]  # statement exists, existing removed endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is True
        assert result.data == 1  # existing id

    def test_withdraw_endorsement_invalid_params(self):
        """Test withdrawal with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.withdraw_endorsement(0, 789)

        assert result.success is False
        assert "Invalid parameters" in result.error







    def test_get_user_endorsements_invalid_params(self):
        """Test getting user endorsements with invalid params."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_endorsements(0)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_batch_statement_endorsement_stats_success(self):
        """Test getting batch statement endorsement stats."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (789, 5, 3, 2),  # statement_hash, total, active, withdrawn
            (790, 2, 2, 0)
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([789, 790])

        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["statement_hash"] == 789
        assert result.data[0]["total_endorsements"] == 5

    def test_get_batch_statement_endorsement_stats_empty(self):
        """Test getting batch stats with no endorsements."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([789, 790])

        assert result.success is True
        assert len(result.data) == 2
        assert result.data[0]["total_endorsements"] == 0

    def test_get_batch_statement_endorsement_stats_invalid_params(self):
        """Test batch stats with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.get_batch_statement_endorsement_stats([])

        assert result.success is False
        assert "Invalid parameters" in result.error



    def test_create_endorsement_database_error(self):
        """Test endorsement creation with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # statement exists
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        result = repo.create_endorsement(456, 789)

        assert result.success is False
        assert "DB error" in result.error

    def test_create_endorsement_logging_success(self, caplog):
        """Test that creating endorsement logs debug message on success."""
        import logging
        caplog.set_level(logging.DEBUG)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # statement exists
        mock_cursor.lastrowid = 123
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        repo.create_endorsement(456, 789)

        assert "Creating endorsement from user 456 for statement 789" in caplog.text

    def test_withdraw_endorsement_logging_success(self, caplog):
        """Test that withdrawing endorsement logs debug message."""
        import logging
        caplog.set_level(logging.DEBUG)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (123,)  # existing endorsement
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        repo.withdraw_endorsement(456, 789)

        assert "Withdrawing endorsement from user 456 for statement 789" in caplog.text

    def test_get_statement_endorsements_logging_success(self, caplog):
        """Test that getting statement endorsements logs error on failure."""
        import logging
        caplog.set_level(logging.ERROR)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        repo.get_statement_endorsements(789)

        assert "Error getting statement endorsements: DB error" in caplog.text

    def test_get_user_endorsements_logging_success(self, caplog):
        """Test that getting user endorsements logs error on failure."""
        import logging
        caplog.set_level(logging.ERROR)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        repo.get_user_endorsements(456)

        assert "Error getting user endorsements: DB error" in caplog.text

    def test_get_user_endorsement_stats_logging_success(self, caplog):
        """Test that getting user endorsement stats logs error on failure."""
        import logging
        caplog.set_level(logging.ERROR)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        repo.get_user_endorsement_stats(456)

        assert "Error getting user endorsement stats: DB error" in caplog.text

    def test_get_batch_statement_endorsement_stats_logging_success(self, caplog):
        """Test that getting batch stats logs error on failure."""
        import logging
        caplog.set_level(logging.ERROR)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = EndorsementRepository(vitess_client=mock_vitess_client)

        repo.get_batch_statement_endorsement_stats([789])

        assert "Error getting batch statement endorsement stats: DB error" in caplog.text
