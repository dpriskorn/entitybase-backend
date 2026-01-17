from _typeshed import Incomplete
from aiokafka.errors import IllegalArgumentError as IllegalArgumentError

class NewTopic:
    name: Incomplete
    num_partitions: Incomplete
    replication_factor: Incomplete
    replica_assignments: Incomplete
    topic_configs: Incomplete
    def __init__(
        self,
        name,
        num_partitions,
        replication_factor,
        replica_assignments=None,
        topic_configs=None,
    ) -> None: ...
