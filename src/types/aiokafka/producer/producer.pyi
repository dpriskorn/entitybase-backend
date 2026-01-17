from .message_accumulator import MessageAccumulator as MessageAccumulator
from .sender import Sender as Sender
from .transaction_manager import TransactionManager as TransactionManager
from _typeshed import Incomplete
from aiokafka.client import AIOKafkaClient as AIOKafkaClient
from aiokafka.codec import (
    has_gzip as has_gzip,
    has_lz4 as has_lz4,
    has_snappy as has_snappy,
    has_zstd as has_zstd,
)
from aiokafka.errors import (
    IllegalOperation as IllegalOperation,
    MessageSizeTooLargeError as MessageSizeTooLargeError,
)
from aiokafka.partitioner import DefaultPartitioner as DefaultPartitioner
from aiokafka.record.default_records import (
    DefaultRecordBatch as DefaultRecordBatch,
    DefaultRecordBatchBuilder as DefaultRecordBatchBuilder,
)
from aiokafka.structs import TopicPartition as TopicPartition
from aiokafka.util import (
    INTEGER_MAX_VALUE as INTEGER_MAX_VALUE,
    commit_structure_validate as commit_structure_validate,
    create_task as create_task,
    get_running_loop as get_running_loop,
)

log: Incomplete

class AIOKafkaProducer:
    client: Incomplete
    def __init__(
        self,
        *,
        loop=None,
        bootstrap_servers: str = "localhost",
        client_id=None,
        metadata_max_age_ms: int = 300000,
        request_timeout_ms: int = 40000,
        acks=...,
        key_serializer=None,
        value_serializer=None,
        compression_type=None,
        max_batch_size: int = 16384,
        partitioner=...,
        max_request_size: int = 1048576,
        linger_ms: int = 0,
        retry_backoff_ms: int = 100,
        security_protocol: str = "PLAINTEXT",
        ssl_context=None,
        connections_max_idle_ms: int = 540000,
        enable_idempotence: bool = False,
        transactional_id=None,
        transaction_timeout_ms: int = 60000,
        sasl_mechanism: str = "PLAIN",
        sasl_plain_password=None,
        sasl_plain_username=None,
        sasl_kerberos_service_name: str = "kafka",
        sasl_kerberos_domain_name=None,
        sasl_oauth_token_provider=None,
    ) -> None: ...
    def __del__(self, _warnings=...) -> None: ...
    async def start(self) -> None: ...
    async def flush(self) -> None: ...
    async def stop(self) -> None: ...
    async def partitions_for(self, topic): ...
    async def send(
        self,
        topic,
        value=None,
        key=None,
        partition=None,
        timestamp_ms=None,
        headers=None,
    ): ...
    async def send_and_wait(
        self,
        topic,
        value=None,
        key=None,
        partition=None,
        timestamp_ms=None,
        headers=None,
    ): ...
    def create_batch(self): ...
    async def send_batch(self, batch, topic, *, partition): ...
    async def begin_transaction(self) -> None: ...
    async def commit_transaction(self) -> None: ...
    async def abort_transaction(self) -> None: ...
    def transaction(self): ...
    async def send_offsets_to_transaction(self, offsets, group_id) -> None: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

class TransactionContext:
    def __init__(self, producer) -> None: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...
