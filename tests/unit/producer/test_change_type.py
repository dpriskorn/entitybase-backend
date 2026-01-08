import sys

sys.path.insert(0, "src")

from models.infrastructure.stream.producer import ChangeType


class TestChangeTypeEnum:
    """Tests for ChangeType enum values and behavior"""

    def test_all_ten_change_types_defined(self) -> None:
        """Verify all 10 change types are defined correctly"""
        expected_types = {
            "creation",
            "edit",
            "redirect",
            "unredirect",
            "archival",
            "unarchival",
            "lock",
            "unlock",
            "soft_delete",
            "hard_delete",
        }
        actual_types = {ct.value for ct in ChangeType}
        assert actual_types == expected_types

    def test_change_type_enum_count(self) -> None:
        """Verify exactly 10 change types exist"""
        assert len(ChangeType) == 10

    def test_change_type_enum_uniqueness(self) -> None:
        """All enum values are unique"""
        values = [ct.value for ct in ChangeType]
        assert len(values) == len(set(values))

    def test_change_type_string_inheritance(self) -> None:
        """ChangeType inherits from str for string operations"""
        assert isinstance(ChangeType.CREATION, str)
        assert ChangeType.CREATION == "creation"

    def test_change_type_individual_values(self) -> None:
        """Test individual change type values"""
        assert ChangeType.CREATION == "creation"
        assert ChangeType.EDIT == "edit"
        assert ChangeType.REDIRECT == "redirect"
        assert ChangeType.UNREDIRECT == "unredirect"
        assert ChangeType.ARCHIVAL == "archival"
        assert ChangeType.UNARCHIVAL == "unarchival"
        assert ChangeType.LOCK == "lock"
        assert ChangeType.UNLOCK == "unlock"
        assert ChangeType.SOFT_DELETE == "soft_delete"
        assert ChangeType.HARD_DELETE == "hard_delete"
