import uuid


class UniqueIdGenerator:
    def __init__(self) -> None:
        self._counter = 0

    def generate_unique_id(self) -> int:
        self._counter += 1
        return (uuid.uuid4().int + self._counter) & ((1 << 64) - 1)
