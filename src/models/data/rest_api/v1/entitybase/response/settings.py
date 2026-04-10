from typing import Any

from pydantic import BaseModel


class SettingsResponse(BaseModel):
    """Response model for settings endpoint (excludes sensitive values)."""

    model_config = {"extra": "forbid"}

    s3_endpoint: str
    s3_revisions_bucket: str
    s3_snak_version: str
    s3_sitelink_version: str
    s3_qualifier_version: str
    s3_reference_version: str
    s3_statement_version: str
    s3_schema_revision_version: str
    vitess_host: str
    vitess_port: int
    vitess_database: str
    vitess_pool_size: int
    vitess_max_overflow: int
    vitess_pool_timeout: int
    wikibase_repository_name: str
    property_registry_path: str
    log_level: str
    streaming_enabled: bool
    kafka_bootstrap_servers: str
    kafka_entitychange_json_topic: str
    kafka_entity_diff_topic: str
    streaming_entity_change_version: str
    streaming_endorsechange_version: str
    streaming_newthank_version: str
    streaming_entity_diff_version: str
    entity_version: str
    dangling_property_id: str
    api_prefix: str
    user_agent: str
    api_description: str
    backlink_stats_enabled: bool
    backlink_stats_schedule: str
    backlink_stats_top_limit: int
    user_stats_worker_enabled: bool
    user_stats_schedule: str
    general_stats_worker_enabled: bool
    general_stats_schedule: str
    json_worker_enabled: bool
    json_dump_schedule: str
    s3_dump_bucket: str
    json_dump_batch_size: int
    json_dump_parallel_workers: int
    json_dump_generate_checksums: bool
    ttl_worker_enabled: bool
    ttl_dump_schedule: str
    ttl_dump_batch_size: int
    ttl_dump_parallel_workers: int
    ttl_dump_compression: bool
    ttl_dump_generate_checksums: bool
    id_worker_enabled: bool
    purge_worker_enabled: bool
    elasticsearch_enabled: bool
    meilisearch_enabled: bool


def settings_to_response(settings: Any) -> SettingsResponse:
    """Convert Settings object to SettingsResponse, excluding sensitive fields."""
    exclude = {"s3_access_key", "s3_secret_key", "vitess_password", "vitess_user"}
    data = settings.model_dump(exclude=exclude)
    data["property_registry_path"] = str(data["property_registry_path"])
    return SettingsResponse(**data)
