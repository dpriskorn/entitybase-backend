import uuid

from pydantic import BaseModel, Field


class UniqueIdGenerator(BaseModel):
    _counter: int = Field(default=0)

    def generate_unique_id(self) -> int:
        self._counter += 1
        return (uuid.uuid4().int + self._counter) & ((1 << 64) - 1)
