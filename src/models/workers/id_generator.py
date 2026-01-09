import asyncio
import logging
import os
import signal
from typing import Any, Optional

from pydantic import BaseModel

from models.infrastructure.vitess_client import VitessClient
from models.rest_api.services.enumeration_service import EnumerationService

logger = logging.getLogger(__name__)


class IdGeneratorWorker(BaseModel):
    """Worker service for generating entity IDs using range-based allocation."""

    def __init__(self, worker_id: Optional[str] = None):
        self.worker_id = worker_id or os.getenv("WORKER_ID", f"worker-{os.getpid()}")
        self.vitess_client = None
        self.enumeration_service = None
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def start(self) -> None:
        """Start the ID generation worker."""
        logger.info(f"Starting ID Generator Worker {self.worker_id}")

        try:
            # Initialize Vitess client with default config
            from models.vitess_models import VitessConfig

            vitess_config = VitessConfig(
                host=os.getenv("VITESS_HOST", "vitess"),
                port=int(os.getenv("VITESS_PORT", "15309")),
                database=os.getenv("VITESS_DATABASE", "page"),
                user=os.getenv("VITESS_USER", "root"),
                password=os.getenv("VITESS_PASSWORD", ""),
            )
            self.vitess_client = VitessClient(config=vitess_config)

            # Initialize enumeration service
            self.enumeration_service = EnumerationService(
                vitess_client=self.vitess_client, worker_id=self.worker_id
            )

            logger.info("ID Generator Worker initialized successfully")
            self.running = True

            # Main worker loop - for now, just keep alive and handle range allocation
            while self.running:
                try:
                    # Check range status periodically
                    if self.enumeration_service:
                        status = self.enumeration_service.get_range_status()
                        logger.debug(f"Range status: {status}")
                    else:
                        logger.warning("Enumeration service not initialized")

                    # Sleep for a reasonable interval
                    await asyncio.sleep(60)  # Check every minute

                except Exception as e:
                    logger.error(f"Error in worker loop: {e}")
                    await asyncio.sleep(10)  # Wait before retrying

        except Exception as e:
            logger.error(f"Failed to start worker: {e}")
            raise
        finally:
            await self._shutdown()

    async def _shutdown(self) -> None:
        """Clean shutdown of worker resources."""
        logger.info("Shutting down ID Generator Worker")

        if self.vitess_client:
            # Close database connections
            pass

        logger.info("ID Generator Worker shutdown complete")

    async def health_check(self) -> dict:
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy" if self.running else "unhealthy",
            "worker_id": self.worker_id,
            "range_status": self.enumeration_service.get_range_status()
            if self.enumeration_service is not None
            else {},
        }

    def get_next_id(self, entity_type: str) -> str:
        """Get next ID for entity type (synchronous wrapper)."""
        if not self.enumeration_service:
            raise RuntimeError("Worker not initialized")

        return self.enumeration_service.get_next_entity_id(entity_type)


async def main() -> None:
    """Main entry point for the worker."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create and start worker
    worker = IdGeneratorWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
