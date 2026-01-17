import asyncio
from asyncio import iscoroutinefunction as iscoroutinefunction

__all__ = ["asyncio_run", "iscoroutinefunction"]

asyncio_run = asyncio.run
