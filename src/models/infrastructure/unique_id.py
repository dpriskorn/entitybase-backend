import uuid

from pydantic import BaseModel, Field


class UniqueIdGenerator(BaseModel):
    counter: int = Field(default=0)

    def generate_unique_id(self) -> int:
        self.counter += 1
        return (uuid.uuid4().int + self.counter) & ((1 << 64) - 1)
