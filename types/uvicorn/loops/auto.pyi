import asyncio
from collections.abc import Callable as Callable

def auto_loop_factory(
    use_subprocess: bool = False,
) -> Callable[[], asyncio.AbstractEventLoop]: ...
