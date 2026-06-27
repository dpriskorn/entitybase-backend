import sys
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler


class TestUserActivityHandler:
    """Unit tests for UserActivityHandler"""

    @pytest.fixture
    def mock_mysql_client(self) -> MagicMock:
        """Mock Sql client"""
        client = MagicMock()
        client.user_repository = MagicMock()
        return client

    @pytest.fixture
    def handler(self, mock_mysql_client: MagicMock) -> UserActivityHandler:
        """Create handler instance"""
        state = MagicMock()
        state.mysql_client = mock_mysql_client
        return UserActivityHandler(state=state)
