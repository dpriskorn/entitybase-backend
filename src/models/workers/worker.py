import os
from abc import ABC

from pydantic import BaseModel, Field


class Worker(BaseModel, ABC):
    worker_id: str = Field(
        default_factory=lambda: os.getenv("WORKER_ID", f"worker-{os.getpid()}")
    )
    running: bool = False
