from .config_resource import (
    ConfigResource as ConfigResource,
    ConfigResourceType as ConfigResourceType,
)
from .new_partitions import NewPartitions as NewPartitions
from .new_topic import NewTopic as NewTopic
from .records_to_delete import RecordsToDelete as RecordsToDelete
from _typeshed import Incomplete
from aiokafka import __version__ as __version__
from aiokafka.client import AIOKafkaClient as AIOKafkaClient
from aiokafka.errors import (
    LeaderNotAvailableError as LeaderNotAvailableError,
    NotControllerError as NotControllerError,
    NotLeaderForPartitionError as NotLeaderForPartitionError,
    for_code as for_code,
)
from aiokafka.protocol.admin import (
    AlterConfigsRequest as AlterConfigsRequest,
    CreatePartitionsRequest as CreatePartitionsRequest,
    CreateTopicsRequest as CreateTopicsRequest,
    DeleteRecordsRequest as DeleteRecordsRequest,
    DeleteTopicsRequest as DeleteTopicsRequest,
    DescribeConfigsRequest as DescribeConfigsRequest,
    DescribeGroupsRequest as DescribeGroupsRequest,
    ListGroupsRequest as ListGroupsRequest,
)
from aiokafka.protocol.api import Request as Request, Response as Response
from aiokafka.protocol.commit import OffsetFetchRequest as OffsetFetchRequest
from aiokafka.protocol.coordination import (
    FindCoordinatorRequest as FindCoordinatorRequest,
)
from aiokafka.protocol.metadata import MetadataRequest as MetadataRequest
from aiokafka.structs import (
    OffsetAndMetadata as OffsetAndMetadata,
    TopicPartition as TopicPartition,
)
from ssl import SSLContext
from typing import Any

log: Incomplete

class AIOKafkaAdminClient:
    def __init__(
        self,
        *,
        loop=None,
        bootstrap_servers: str | list[str] = "localhost",
        client_id: str = ...,
        request_timeout_ms: int = 40000,
        connections_max_idle_ms: int = 540000,
        retry_backoff_ms: int = 100,
        metadata_max_age_ms: int = 300000,
        security_protocol: str = "PLAINTEXT",
        ssl_context: SSLContext | None = None,
        sasl_mechanism: str = "PLAIN",
        sasl_plain_username: str | None = None,
        sasl_plain_password: str | None = None,
        sasl_kerberos_service_name: str = "kafka",
        sasl_kerberos_domain_name: str | None = None,
        sasl_oauth_token_provider: str | None = None,
    ) -> None: ...
    async def close(self) -> None: ...
    async def start(self) -> None: ...
    async def create_topics(
        self,
        new_topics: list[NewTopic],
        timeout_ms: int | None = None,
        validate_only: bool = False,
    ) -> Response: ...
    async def delete_topics(
        self, topics: list[str], timeout_ms: int | None = None
    ) -> Response: ...
    async def list_topics(self) -> list[str]: ...
    async def describe_topics(self, topics: list[str] | None = None) -> list[Any]: ...
    async def describe_cluster(self) -> dict[str, Any]: ...
    async def describe_configs(
        self, config_resources: list[ConfigResource], include_synonyms: bool = False
    ) -> list[Response]: ...
    async def alter_configs(
        self, config_resources: list[ConfigResource]
    ) -> list[Response]: ...
    async def create_partitions(
        self,
        topic_partitions: dict[str, NewPartitions],
        timeout_ms: int | None = None,
        validate_only: bool = False,
    ) -> Response: ...
    async def describe_consumer_groups(
        self,
        group_ids: list[str],
        group_coordinator_id: int | None = None,
        include_authorized_operations: bool = False,
    ) -> list[Response]: ...
    async def list_consumer_groups(
        self, broker_ids: list[int] | None = None
    ) -> list[tuple[Any, ...]]: ...
    async def find_coordinator(
        self, group_id: str, coordinator_type: int = 0
    ) -> int: ...
    async def list_consumer_group_offsets(
        self,
        group_id: str,
        group_coordinator_id: int | None = None,
        partitions: list[TopicPartition] | None = None,
    ) -> dict[TopicPartition, OffsetAndMetadata]: ...
    async def delete_records(
        self,
        records_to_delete: dict[TopicPartition, RecordsToDelete],
        timeout_ms: int | None = None,
    ) -> dict[TopicPartition, int]: ...
