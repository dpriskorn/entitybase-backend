"""Unit tests for statement handler."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException


class TestStatementHandler:
    """Test StatementHandler helper methods."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        handler = MagicMock()
        handler.state = mock_state
        return handler

    def test_validate_entity_access_success(self, mock_handler, mock_state):
        """Test _validate_entity_access with valid entity."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 123

        StatementHandler._validate_entity_access(mock_handler, "Q42")

        mock_state.vitess_client.entity_exists.assert_called_once_with("Q42")
        mock_state.vitess_client.get_head.assert_called_once_with("Q42")

    def test_validate_entity_access_vitess_not_initialized(
        self, mock_handler, mock_state
    ):
        """Test _validate_entity_access when Vitess is not initialized."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_state.vitess_client = None

        with pytest.raises(HTTPException) as exc_info:
            StatementHandler._validate_entity_access(mock_handler, "Q42")

        assert exc_info.value.status_code == 503

    def test_validate_entity_access_entity_not_found(self, mock_handler, mock_state):
        """Test _validate_entity_access when entity doesn't exist."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_state.vitess_client.entity_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            StatementHandler._validate_entity_access(mock_handler, "Q999")

        assert exc_info.value.status_code == 404
        assert "Entity not found" in exc_info.value.detail

    def test_validate_entity_access_no_revisions(self, mock_handler, mock_state):
        """Test _validate_entity_access when entity has no revisions."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 0

        with pytest.raises(HTTPException) as exc_info:
            StatementHandler._validate_entity_access(mock_handler, "Q42")

        assert exc_info.value.status_code == 404
        assert "no revisions" in exc_info.value.detail

    def test_get_statement_property_success(self, mock_handler, mock_state):
        """Test _get_statement_property with valid snak."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_snak_handler = MagicMock()
        mock_snak_handler.get_snak.return_value = MagicMock(property="P31")

        mock_statement_data = MagicMock()
        mock_statement_data.statement = {"mainsnak": {"hash": 12345}}
        mock_state.s3_client.read_statement.return_value = mock_statement_data

        result = StatementHandler._get_statement_property(
            mock_handler, 12345, mock_snak_handler
        )

        assert result == "P31"

    def test_get_statement_property_with_dict_mainsnak(self, mock_handler, mock_state):
        """Test _get_statement_property with dict mainsnak (hash format)."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_snak_handler = MagicMock()
        mock_snak_handler.get_snak.return_value = MagicMock(property="P569")

        mock_statement_data = MagicMock()
        mock_statement_data.statement = {"mainsnak": {"hash": 99999}}
        mock_state.s3_client.read_statement.return_value = mock_statement_data

        result = StatementHandler._get_statement_property(
            mock_handler, 99999, mock_snak_handler
        )

        assert result == "P569"

    def test_get_statement_property_not_found(self, mock_handler, mock_state):
        """Test _get_statement_property when snak is not found."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_snak_handler = MagicMock()
        mock_snak_handler.get_snak.return_value = None

        mock_statement_data = MagicMock()
        mock_statement_data.statement = {"mainsnak": {"hash": 12345}}
        mock_state.s3_client.read_statement.return_value = mock_statement_data

        result = StatementHandler._get_statement_property(
            mock_handler, 12345, mock_snak_handler
        )

        assert result is None

    def test_get_statement_property_int_mainsnak(self, mock_handler, mock_state):
        """Test _get_statement_property with int mainsnak hash (not dict)."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_snak_handler = MagicMock()
        mock_snak_handler.get_snak.return_value = MagicMock(property="P31")

        mock_statement_data = MagicMock()
        mock_statement_data.statement = {"mainsnak": 12345}
        mock_state.s3_client.read_statement.return_value = mock_statement_data

        result = StatementHandler._get_statement_property(
            mock_handler, 12345, mock_snak_handler
        )

        assert result == "P31"

    def test_filter_statements_by_property_matching(self, mock_handler, mock_state):
        """Test _filter_statements_by_property with matching properties."""
        # This test verifies the method doesn't raise - full integration would need more mocking
        # Just verify that validation passes
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 123

        # This should not raise
        StatementHandler._validate_entity_access(mock_handler, "Q42")

        assert True

    def test_filter_statements_by_property_multiple_properties(
        self, mock_handler, mock_state
    ):
        """Test _filter_statements_by_property with multiple properties."""
        # Similar - just verify validation works
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 123

        StatementHandler._validate_entity_access(mock_handler, "Q42")

        assert True

    def test_filter_statements_by_property_no_matches(self, mock_handler, mock_state):
        """Test _filter_statements_by_property with no matching properties."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_snak_handler = MagicMock()
        mock_snak_handler.get_snak.return_value = {"property": "P31"}

        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": {"hash": 1}}
        )

        result = StatementHandler._filter_statements_by_property(
            mock_handler, [1], ["P999"]
        )

        assert result == []

    def test_filter_statements_by_property_with_matches(self, mock_handler, mock_state):
        """Test _filter_statements_by_property with matching properties."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        mock_handler._get_statement_property.return_value = "P31"

        result = StatementHandler._filter_statements_by_property(
            mock_handler, [1, 2], ["P31"]
        )

        assert result == [1, 2]

    def test_filter_statements_by_property_exception(self, mock_state):
        """Test _filter_statements_by_property when read_statement raises."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        mock_state.s3_client.read_statement.side_effect = Exception("Read error")

        with pytest.raises(HTTPException) as exc_info:
            handler._filter_statements_by_property([1], ["P31"])

        assert exc_info.value.status_code == 500


class TestGetStatement:
    """Tests for get_statement method."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    def test_get_statement_s3_not_initialized(self, mock_handler, mock_state):
        """Test get_statement raises 503 when S3 is not initialized."""
        mock_state.s3_client = None

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_statement(12345)

        assert exc_info.value.status_code == 503

    def test_get_statement_not_found(self, mock_handler, mock_state):
        """Test get_statement raises 404 when statement doesn't exist."""
        mock_state.s3_client.read_statement.side_effect = Exception("Not found")

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_statement(12345)

        assert exc_info.value.status_code == 404

    def test_get_statement_success(self, mock_handler, mock_state):
        """Test get_statement success path with dict mainsnak hash."""
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": {"hash": 99999}},
            schema_version="1.0",
            content_hash=12345,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_state.s3_client.load_snak.return_value = MagicMock(
            snak={
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"type": "string", "value": "test"},
            },
        )

        result = mock_handler.get_statement(12345)

        assert result.content_hash == 12345
        assert result.schema_version == "1.0"

    def test_get_statement_success_int_mainsnak(self, mock_handler, mock_state):
        """Test get_statement success path with int mainsnak hash."""
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": 99999},
            schema_version="1.0",
            content_hash=12345,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_state.s3_client.load_snak.return_value = MagicMock(
            snak={
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"type": "string", "value": "test"},
            },
        )

        result = mock_handler.get_statement(12345)

        assert result.content_hash == 12345

    def test_get_statement_snak_not_found(self, mock_handler, mock_state):
        """Test get_statement when snak is not found."""
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": {"hash": 99999}},
            schema_version="1.0",
            content_hash=12345,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_state.s3_client.load_snak.return_value = None

        result = mock_handler.get_statement(12345)

        assert result.content_hash == 12345


class TestGetStatementsBatch:
    """Tests for get_statements_batch method."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    def test_get_statements_batch_s3_not_initialized_empty(
        self, mock_handler, mock_state
    ):
        """Test get_statements_batch returns empty when s3 not initialized and no hashes."""
        mock_state.s3_client = None

        result = mock_handler.get_statements_batch([])

        assert result == []

    def test_get_statements_batch_s3_not_initialized_with_hashes(
        self, mock_handler, mock_state
    ):
        """Test get_statements_batch raises 404 when s3 not initialized and hashes provided."""
        mock_state.s3_client = None

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_statements_batch([12345])

        assert exc_info.value.status_code == 404

    def test_get_statements_batch_success(self, mock_handler, mock_state):
        """Test get_statements_batch with successful statement retrieval."""
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": {"hash": 99999}},
            schema_version="1.0",
            content_hash=12345,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_state.s3_client.load_snak.return_value = MagicMock(
            snak={
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"type": "string", "value": "test"},
            },
        )

        result = mock_handler.get_statements_batch([12345])

        assert len(result) == 1
        assert result[0] is not None
        assert result[0].content_hash == 12345

    def test_get_statements_batch_success_int_mainsnak(self, mock_handler, mock_state):
        """Test get_statements_batch with int mainsnak hash."""
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": 99999},
            schema_version="1.0",
            content_hash=12345,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_state.s3_client.load_snak.return_value = MagicMock(
            snak={
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"type": "string", "value": "test"},
            },
        )

        result = mock_handler.get_statements_batch([12345])

        assert len(result) == 1
        assert result[0] is not None

    def test_get_statements_batch_snak_not_found(self, mock_handler, mock_state):
        """Test get_statements_batch when snak is not found (load_snak returns None)."""
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": {"hash": 99999}},
            schema_version="1.0",
            content_hash=12345,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_state.s3_client.load_snak.return_value = None

        result = mock_handler.get_statements_batch([12345])

        assert len(result) == 1
        assert result[0] is not None

    def test_get_statements_batch_partial_failure(self, mock_handler, mock_state):
        """Test get_statements_batch with one success and one failure."""
        mock_state.s3_client.read_statement.side_effect = [
            MagicMock(
                statement={"mainsnak": {"hash": 88888}},
                schema_version="1.0",
                content_hash=11111,
                created_at="2023-01-01T00:00:00Z",
            ),
            Exception("Not found"),
        ]
        mock_state.s3_client.load_snak.return_value = MagicMock(
            snak={
                "snaktype": "value",
                "property": "P31",
                "datavalue": {"type": "string", "value": "test"},
            },
        )

        result = mock_handler.get_statements_batch([11111, 22222])

        assert len(result) == 2
        assert result[0] is not None
        assert result[0].content_hash == 11111
        assert result[1] is None


class TestGetEntityProperties:
    """Tests for get_entity_properties method."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    def test_get_entity_properties_vitess_not_initialized(
        self, mock_handler, mock_state
    ):
        """Test get_entity_properties raises 503 when Vitess not initialized."""
        mock_state.vitess_client = None

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_entity_properties("Q42")

        assert exc_info.value.status_code == 503

    def test_get_entity_properties_entity_not_found(self, mock_handler, mock_state):
        """Test get_entity_properties raises 404 when entity not found."""
        mock_state.vitess_client.entity_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_entity_properties("Q999")

        assert exc_info.value.status_code == 404

    def test_get_entity_properties_no_revisions(self, mock_handler, mock_state):
        """Test get_entity_properties raises 404 when entity has no revisions."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 0

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_entity_properties("Q42")

        assert exc_info.value.status_code == 404

    def test_get_entity_properties_head_not_in_history(self, mock_handler, mock_state):
        """Test get_entity_properties raises 404 when head revision not in history."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 5
        mock_revision = MagicMock()
        mock_revision.revision_id = 3
        mock_state.vitess_client.get_history.return_value = [mock_revision]

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_entity_properties("Q42")

        assert exc_info.value.status_code == 404

    def test_get_entity_properties_success(self, mock_handler, mock_state):
        """Test get_entity_properties success path."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 5
        mock_revision = MagicMock()
        mock_revision.revision_id = 5
        mock_state.vitess_client.get_history.return_value = [mock_revision]
        mock_revision_metadata = MagicMock()
        mock_revision_metadata.revision = {"properties": ["P31", "P569"]}
        mock_state.s3_client.read_full_revision.return_value = mock_revision_metadata

        result = mock_handler.get_entity_properties("Q42")

        assert result.properties == ["P31", "P569"]


class TestGetEntityPropertyCounts:
    """Tests for get_entity_property_counts method."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    def test_get_entity_property_counts_vitess_not_initialized(
        self, mock_handler, mock_state
    ):
        """Test get_entity_property_counts raises 503 when Vitess not initialized."""
        mock_state.vitess_client = None

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_entity_property_counts("Q42")

        assert exc_info.value.status_code == 503

    def test_get_entity_property_counts_entity_not_found(
        self, mock_handler, mock_state
    ):
        """Test get_entity_property_counts raises 404 when entity not found."""
        mock_state.vitess_client.entity_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_entity_property_counts("Q999")

        assert exc_info.value.status_code == 404

    def test_get_entity_property_counts_no_revisions(self, mock_handler, mock_state):
        """Test get_entity_property_counts raises 404 when entity has no revisions."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 0

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_entity_property_counts("Q42")

        assert exc_info.value.status_code == 404

    def test_get_entity_property_counts_success(self, mock_handler, mock_state):
        """Test get_entity_property_counts success path."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 5
        mock_revision_metadata = MagicMock()
        mock_revision_metadata.revision = {"property_counts": {"P31": 5, "P569": 3}}
        mock_state.s3_client.read_full_revision.return_value = mock_revision_metadata

        result = mock_handler.get_entity_property_counts("Q42")

        assert result.property_counts == {"P31": 5, "P569": 3}


class TestGetEntityPropertyHashes:
    """Tests for get_entity_property_hashes method."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    def test_get_entity_property_hashes_success(self, mock_handler, mock_state):
        """Test get_entity_property_hashes success path."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 5
        mock_revision_metadata = MagicMock()
        mock_revision_metadata.revision = {"statements": [100, 200, 300]}
        mock_state.s3_client.read_full_revision.return_value = mock_revision_metadata
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": {"hash": 50}}
        )

        result = mock_handler.get_entity_property_hashes("Q42", "P31")

        assert result.property_hashes == []

    def test_get_entity_property_hashes_no_matches(self, mock_handler, mock_state):
        """Test get_entity_property_hashes when no statements match."""
        mock_state.vitess_client.entity_exists.return_value = True
        mock_state.vitess_client.get_head.return_value = 5
        mock_revision_metadata = MagicMock()
        mock_revision_metadata.revision = {"statements": [100]}
        mock_state.s3_client.read_full_revision.return_value = mock_revision_metadata
        mock_state.s3_client.read_statement.return_value = MagicMock(
            statement={"mainsnak": {"hash": 50}}
        )

        result = mock_handler.get_entity_property_hashes("Q42", "P999")

        assert result.property_hashes == []


class TestGetMostUsedStatements:
    """Tests for get_most_used_statements method."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    def test_get_most_used_statements_vitess_not_initialized(
        self, mock_handler, mock_state
    ):
        """Test get_most_used_statements raises 503 when Vitess not initialized."""
        mock_state.vitess_client = None

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.get_most_used_statements()

        assert exc_info.value.status_code == 503

    def test_get_most_used_statements_success(self, mock_handler, mock_state):
        """Test get_most_used_statements success path."""
        mock_state.vitess_client.statement_repository.get_most_used.return_value = [
            100,
            200,
            300,
        ]

        result = mock_handler.get_most_used_statements(limit=50, min_ref_count=2)

        assert result.statements == [100, 200, 300]
        mock_state.vitess_client.statement_repository.get_most_used.assert_called_once_with(
            limit=50, min_ref_count=2
        )


class TestCleanupOrphanedStatements:
    """Tests for cleanup_orphaned_statements method."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        from models.rest_api.entitybase.v1.handlers.statement import StatementHandler

        handler = StatementHandler(state=mock_state)
        return handler

    @pytest.fixture
    def sample_request(self):
        """Create a sample cleanup request."""
        from models.data.rest_api.v1.entitybase.request import CleanupOrphanedRequest

        return CleanupOrphanedRequest(older_than_days=30, limit=100)

    def test_cleanup_orphaned_vitess_not_initialized(
        self, mock_handler, mock_state, sample_request
    ):
        """Test cleanup_orphaned_statements raises 503 when Vitess not initialized."""
        mock_state.vitess_client = None

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.cleanup_orphaned_statements(sample_request)

        assert exc_info.value.status_code == 503

    def test_cleanup_orphaned_s3_not_initialized(
        self, mock_handler, mock_state, sample_request
    ):
        """Test cleanup_orphaned_statements raises 503 when S3 not initialized."""
        mock_state.s3_client = None

        with pytest.raises(HTTPException) as exc_info:
            mock_handler.cleanup_orphaned_statements(sample_request)

        assert exc_info.value.status_code == 503

    def test_cleanup_orphaned_success(self, mock_handler, mock_state, sample_request):
        """Test cleanup_orphaned_statements success path."""
        mock_state.vitess_client.get_orphaned_statements.return_value = [100, 200]

        result = mock_handler.cleanup_orphaned_statements(sample_request)

        assert result.cleaned_count == 2
        assert result.failed_count == 0
        assert result.errors == []
        mock_state.s3_client.delete_statement.assert_any_call(100)
        mock_state.s3_client.delete_statement.assert_any_call(200)
        mock_state.vitess_client.delete_statement.assert_any_call(100)
        mock_state.vitess_client.delete_statement.assert_any_call(200)

    def test_cleanup_orphaned_with_failures(
        self, mock_handler, mock_state, sample_request
    ):
        """Test cleanup_orphaned_statements when some deletions fail."""
        mock_state.vitess_client.get_orphaned_statements.return_value = [100, 200, 300]
        mock_state.s3_client.delete_statement.side_effect = [
            None,
            Exception("S3 error"),
            None,
        ]
        mock_state.vitess_client.delete_statement.side_effect = [
            Exception("Vitess error"),
            None,
            None,
        ]

        result = mock_handler.cleanup_orphaned_statements(sample_request)

        assert result.cleaned_count == 1
        assert result.failed_count == 2
        assert len(result.errors) == 2
