import pytest

pytestmark = pytest.mark.unit

from models.infrastructure.unique_id import UniqueIdGenerator


class TestUniqueIdGenerator:
    @pytest.fixture
    def generator(self) -> UniqueIdGenerator:
        return UniqueIdGenerator()

    def test_generate_unique_id_uniqueness(self, generator: UniqueIdGenerator) -> None:
        ids = {generator.generate_unique_id() for _ in range(1000)}
        assert len(ids) == 1000

    def test_generate_unique_id_type(self, generator: UniqueIdGenerator) -> None:
        id_value = generator.generate_unique_id()
        assert isinstance(id_value, int)
        assert id_value > 0

    def test_generate_unique_id_range(self, generator: UniqueIdGenerator) -> None:
        id_value = generator.generate_unique_id()
        assert 0 <= id_value < (1 << 64)

    def test_counter_increment(self, generator: UniqueIdGenerator) -> None:
        id1 = generator.generate_unique_id()
        id2 = generator.generate_unique_id()
        assert id1 != id2
        assert generator._counter == 2
