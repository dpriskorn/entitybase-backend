import asyncio
from models.workers.id_generation.id_generator import IdGeneratorWorker


async def main() -> None:
    worker = IdGeneratorWorker()
    health = await worker.health_check()
    exit(0 if health["status"] == "healthy" else 1)


asyncio.run(main())
