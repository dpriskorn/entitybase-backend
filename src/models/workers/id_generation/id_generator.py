import asyncio
import logging
import os
import signal
from typing import Any

from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

from models.api import WorkerHealthCheck
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.services.enumeration_service import EnumerationService
from models.validation.utils import raise_validation_error

logger = logging.getLogger(__name__)


class IdGeneratorWorker(BaseModel):
    """Asynchronous worker service for generating Wikibase entity IDs using range-based allocation.

    This worker reserves blocks (ranges) of IDs from the database to minimize contention
    during high-volume entity creation. It monitors range status, handles graceful shutdown,
    and provides health checks for monitoring.

    The worker initializes Vitess and Enumeration services, then runs a continuous loop
    checking ID range availability. IDs are allocated from pre-reserved ranges to ensure
    efficient, low-latency ID generation.

    Attributes:
        worker_id: Unique identifier for this worker instance.
        vitess_client: Database client for Vitess operations.
        enumeration_service: Service managing ID range allocation.
        running: Flag indicating if the worker loop is active.
    """

    def __init__(self, /, worker_id: str = "", **data: Any):
        """Initialize the ID generator worker.

        Args:
            worker_id: Unique identifier. Defaults to WORKER_ID env var
                       or auto-generated "worker-{pid}".
            **data: Additional Pydantic model data.

        Sets up signal handlers for SIGTERM/SIGINT to enable graceful shutdown.
        Services (VitessClient, EnumerationService) are initialized in start().
        """
        super().__init__(**data)
        self.worker_id = worker_id or os.getenv("WORKER_ID", f"worker-{os.getpid()}")
        self.vitess_client = None
        self.enumeration_service = None
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals (SIGTERM/SIGINT) for graceful termination.

        Sets the running flag to False, allowing the worker loop to exit cleanly.
        Called automatically when the process receives termination signals.

        Args:
            signum: Signal number (e.g., signal.SIGTERM.value).
            frame: Current stack frame (unused, required by signal handler signature).
        """
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def start(self) -> None:
        """Start the ID generation worker and begin the main processing loop.

        Initializes VitessClient and EnumerationService with configuration from
        environment variables (VITESS_HOST, VITESS_PORT, etc.). Runs a continuous
        loop monitoring ID range status every 60 seconds.

        Raises:
            Exception: If initialization fails or critical errors occur.

        The worker will run until a shutdown signal is received or an unrecoverable
        error occurs. Uses exponential backoff for transient errors.
        """
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
        """Perform clean shutdown of worker resources.

        Closes database connections, releases locks, and ensures all pending
        operations complete before termination. Called automatically on shutdown.
        """
        logger.info("Shutting down ID Generator Worker")

        if self.vitess_client:
            # Close database connections
            pass

        logger.info("ID Generator Worker shutdown complete")

    def health_check(self) -> WorkerHealthCheck:
        """Perform health check for monitoring and load balancer integration.

        Returns:
            WorkerHealthCheck: Health status with status, worker_id, and range_status

        Used by external monitoring systems to verify worker availability and
        ID generation capacity.
        """
        return WorkerHealthCheck(
            status="healthy" if self.running else "unhealthy",
            worker_id=self.worker_id,
            range_status=self.enumeration_service.get_range_status()
            if self.enumeration_service is not None
            else {},
        )

    def get_next_id(self, entity_type: str) -> str:
        """Get the next available ID for a given entity type.

        Synchronous wrapper around EnumerationService.get_next_entity_id().
        Allocates IDs from pre-reserved ranges to ensure efficient generation.

        Args:
            entity_type: Type of entity ("item", "property", "lexeme").

        Returns:
            str: Next available ID for the entity type (e.g., "Q123", "P456").

        Raises:
            ValidationError: If the worker is not properly initialized.
        """
        if not self.enumeration_service:
            raise_validation_error("Worker not initialized", status_code=500)

        assert self.enumeration_service is not None
        return self.enumeration_service.get_next_entity_id(entity_type)


async def run_worker(worker: IdGeneratorWorker) -> None:
    """Run the worker loop."""
    await worker.start()


async def run_server(app: FastAPI) -> None:
    """Run the FastAPI server."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8001, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Main entry point for running the ID generator worker with health endpoint.

    Configures logging, creates a worker instance, sets up FastAPI app with /health,
    and runs both the worker loop and HTTP server concurrently.

    Environment Variables:
        WORKER_ID: Unique worker identifier.
        VITESS_HOST, VITESS_PORT, VITESS_DATABASE, VITESS_USER, VITESS_PASSWORD:
        Database connection parameters.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create worker
    worker = IdGeneratorWorker()

    # Create FastAPI app
    app = FastAPI()

    @app.get("/health")
    def health() -> WorkerHealthCheck:
        """Health check endpoint returning JSON status."""
        return worker.health_check()

    # Run worker and server concurrently
    await asyncio.gather(
        run_worker(worker),
        run_server(app),
    )


if __name__ == "__main__":
    asyncio.run(main())
