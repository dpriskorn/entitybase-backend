import pytest

pytestmark = pytest.mark.unit

from models.rest_api.entitybase.v1.request.user_activity import UserActivityRequest


class TestUserActivityRequest:
    def test_user_activity_request_creation(self) -> None:
        """Test creating UserActivityRequest."""
        request = UserActivityRequest()
        assert isinstance(request, UserActivityRequest)
