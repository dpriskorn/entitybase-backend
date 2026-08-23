from typing import Any

from models.workers.worker import Worker


class DbWorker(Worker):
    db_client: Any = None


# Backward compatibility alias
VitessWorker = DbWorker
