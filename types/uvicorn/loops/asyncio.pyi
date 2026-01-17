import asyncio
from collections.abc import Callable as Callable

def asyncio_loop_factory(
    use_subprocess: bool = False,
) -> Callable[[], asyncio.AbstractEventLoop]: ...
