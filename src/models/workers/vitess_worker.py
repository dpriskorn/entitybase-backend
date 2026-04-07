import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from pydantic import Field

from models.config.settings import settings
from models.infrastructure.vitess.client import VitessClient
from models.workers.worker import Worker

logger = logging.getLogger(__name__)


class VitessWorker(Worker, ABC):
    """Base worker that provides Vitess client connectivity."""

    vitess_client: Any | None = Field(default=None)
    worker_id: str = Field(
        default_factory=lambda: os.getenv("WORKER_ID", f"vitess-{os.getpid()}")
    )
    running: bool = Field(default=False)

    def model_post_init(self, context: Any) -> None:
        """Skip validation at init time - clients are created in start() method."""
        if self.get_enabled_setting():
            self.running = True

    async def start(self) -> None:
        """Start the vitess worker."""
        if not self.get_enabled_setting():
            logger.info(f"{self.__class__.__name__} disabled")
            return

        logger.info(f"Starting {self.__class__.__name__} {self.worker_id}")

        vitess_config = settings.get_vitess_config
        self.vitess_client = VitessClient(config=vitess_config)

        self.running = True

    @abstractmethod
    def get_enabled_setting(self) -> bool:
        """Check if the worker is enabled."""
        pass
