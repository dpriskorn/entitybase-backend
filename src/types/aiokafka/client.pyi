from _typeshed import Incomplete
from enum import IntEnum

__all__ = ["AIOKafkaClient"]

class ConnectionGroup(IntEnum):
    DEFAULT = 0
    COORDINATION = 1

class CoordinationType(IntEnum):
    GROUP = 0
    TRANSACTION = 1

class AIOKafkaClient:
    cluster: Incomplete
    def __init__(
        self,
        *,
        loop=None,
        bootstrap_servers: str = "localhost",
        client_id=...,
        metadata_max_age_ms: int = 300000,
        request_timeout_ms: int = 40000,
        retry_backoff_ms: int = 100,
        ssl_context=None,
        security_protocol: str = "PLAINTEXT",
        connections_max_idle_ms: int = 540000,
        sasl_mechanism: str = "PLAIN",
        sasl_plain_username=None,
        sasl_plain_password=None,
        sasl_kerberos_service_name: str = "kafka",
        sasl_kerberos_domain_name=None,
        sasl_oauth_token_provider=None,
    ) -> None: ...
    @property
    def hosts(self): ...
    async def close(self) -> None: ...
    async def bootstrap(self) -> None: ...
    def get_random_node(self): ...
    def force_metadata_update(self): ...
    async def fetch_all_metadata(self): ...
    def add_topic(self, topic): ...
    def set_topics(self, topics): ...
    async def ready(self, node_id, *, group=...): ...
    async def send(self, node_id, request, *, group=...): ...
    async def coordinator_lookup(self, coordinator_type, coordinator_key): ...
