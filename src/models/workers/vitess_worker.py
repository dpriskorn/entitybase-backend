from typing import Any

from models.workers.worker import Worker


class VitessWorker(Worker):
    vitess_client: Any = None
