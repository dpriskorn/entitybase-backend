"""Unit tests for UserRole enum."""

from models.data.common.roles import UserRole


class TestUserRole:
    """Tests for UserRole enum."""

    def test_admin_value(self) -> None:
        """Test ADMIN role value."""
        assert UserRole.ADMIN.value == "admin"

    def test_default_value(self) -> None:
        """Test DEFAULT role value."""
        assert UserRole.DEFAULT.value == "default"

    def test_values_classmethod(self) -> None:
        """Test values() returns all role strings."""
        assert UserRole.values() == ["admin", "default"]

    def test_enum_membership(self) -> None:
        """Test enum membership check."""
        assert UserRole("admin") == UserRole.ADMIN
        assert UserRole("default") == UserRole.DEFAULT

    def test_invalid_role_raises(self) -> None:
        """Test invalid role string raises ValueError."""
        try:
            UserRole("superadmin")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
