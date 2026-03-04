from typing import Any, Dict

from pydantic import BaseModel


class SettingsResponse(BaseModel):
    """Response model for settings endpoint (excludes sensitive values)."""

    model_config = {"extra": "forbid"}

    s3_endpoint: str
    s3_references_bucket: str
    s3_qualifiers_bucket: str
    s3_sitelinks_bucket: str
    s3_snaks_bucket: str
    s3_statements_bucket: str
    s3_terms_bucket: str
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
    user_stats_enabled: bool
    user_stats_schedule: str
    general_stats_enabled: bool
    general_stats_schedule: str
    json_dump_enabled: bool
    json_dump_schedule: str
    s3_dump_bucket: str
    json_dump_batch_size: int
    json_dump_parallel_workers: int
    json_dump_generate_checksums: bool
    ttl_dump_enabled: bool
    ttl_dump_schedule: str
    ttl_dump_batch_size: int
    ttl_dump_parallel_workers: int
    ttl_dump_compression: bool
    ttl_dump_generate_checksums: bool


def settings_to_response(settings: Any) -> Dict[str, Any]:
    """Convert Settings object to response dict, excluding sensitive fields."""
    exclude = {"s3_access_key", "s3_secret_key", "vitess_password", "vitess_user"}
    return settings.model_dump(exclude=exclude)
