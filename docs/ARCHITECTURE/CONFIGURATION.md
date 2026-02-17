# Configuration Overview

This document describes all configuration options available in wikibase-backend.

Settings are managed through the `Settings` class in `src/models/config/settings.py`.

## Environment Variables

All settings can be overridden using environment variables with the same name.


## Database Settings

### `vitess_host`

- **Type**: `str`
- **Default**: `''`
- **Description**: vitess

### `vitess_port`

- **Type**: `int`
- **Default**: `0`
- **Description**: No description available

### `vitess_database`

- **Type**: `str`
- **Default**: `''`
- **Description**: No description available

### `vitess_user`

- **Type**: `str`
- **Default**: `''`
- **Description**: No description available

### `vitess_password`

- **Type**: `str`
- **Default**: `''`
- **Description**: No description available

### `vitess_pool_size`

- **Type**: `int`
- **Default**: `20`
- **Description**: No description available

### `vitess_max_overflow`

- **Type**: `int`
- **Default**: `20`
- **Description**: No description available

### `vitess_pool_timeout`

- **Type**: `int`
- **Default**: `30`
- **Description**: No description available

## Storage Settings

### `s3_endpoint`

- **Type**: `str`
- **Default**: `'http://minio:9000'`
- **Description**: s3

### `s3_access_key`

- **Type**: `str`
- **Default**: `'fakekey'`
- **Description**: No description available

### `s3_secret_key`

- **Type**: `str`
- **Default**: `'fakesecret'`
- **Description**: No description available

### `s3_references_bucket`

- **Type**: `str`
- **Default**: `'references'`
- **Description**: buckets

### `s3_qualifiers_bucket`

- **Type**: `str`
- **Default**: `'qualifiers'`
- **Description**: No description available

### `s3_sitelinks_bucket`

- **Type**: `str`
- **Default**: `'sitelinks'`
- **Description**: No description available

### `s3_snaks_bucket`

- **Type**: `str`
- **Default**: `'snaks'`
- **Description**: No description available

### `s3_statements_bucket`

- **Type**: `str`
- **Default**: `'statements'`
- **Description**: No description available

### `s3_terms_bucket`

- **Type**: `str`
- **Default**: `'terms'`
- **Description**: No description available

### `s3_revisions_bucket`

- **Type**: `str`
- **Default**: `'revisions'`
- **Description**: No description available

### `s3_snak_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: S3 versions

### `s3_sitelink_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: No description available

### `s3_qualifier_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: No description available

### `s3_reference_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: No description available

### `s3_statement_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: No description available

### `s3_schema_revision_version`

- **Type**: `str`
- **Default**: `'4.0.0'`
- **Description**: No description available

### `s3_dump_bucket`

- **Type**: `str`
- **Default**: `'wikibase-dumps'`
- **Description**: No description available

## API Settings

### `api_prefix`

- **Type**: `str`
- **Default**: `'/v1/entitybase'`
- **Description**: API configuration

## Workers Settings

### `backlink_stats_enabled`

- **Type**: `bool`
- **Default**: `True`
- **Description**: workers

### `backlink_stats_schedule`

- **Type**: `str`
- **Default**: `'0 2 * * *'`
- **Description**: No description available

### `backlink_stats_top_limit`

- **Type**: `int`
- **Default**: `100`
- **Description**: No description available

### `json_dump_parallel_workers`

- **Type**: `int`
- **Default**: `50`
- **Description**: No description available

### `ttl_dump_parallel_workers`

- **Type**: `int`
- **Default**: `50`
- **Description**: No description available

## Development Settings

### `log_level`

- **Type**: `str`
- **Default**: `'INFO'`
- **Description**: logging

### `test_log_http_requests`

- **Type**: `bool`
- **Default**: `False`
- **Description**: test_log_level: str = "INFO"

### `test_show_progress`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

## Other Settings

### `wikibase_repository_name`

- **Type**: `str`
- **Default**: `'wikidata'`
- **Description**: rdf

### `property_registry_path`

- **Type**: `Path`
- **Default**: `Path('properties')`
- **Description**: No description available

### `streaming_enabled`

- **Type**: `bool`
- **Default**: `False`
- **Description**: streaming

### `kafka_bootstrap_servers`

- **Type**: `str`
- **Default**: `''`
- **Description**: No description available

### `kafka_entitychange_json_topic`

- **Type**: `str`
- **Default**: `'entitybase.entity_change'`
- **Description**: No description available

### `kafka_entity_diff_topic`

- **Type**: `str`
- **Default**: `'wikibase.entity_diff'`
- **Description**: No description available

### `streaming_entity_change_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: No description available

### `streaming_endorsechange_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: No description available

### `streaming_newthank_version`

- **Type**: `str`
- **Default**: `'1.0.0'`
- **Description**: No description available

### `streaming_entity_diff_version`

- **Type**: `str`
- **Default**: `'2.0.0'`
- **Description**: No description available

### `entity_version`

- **Type**: `str`
- **Default**: `'2.0.0'`
- **Description**: entity version

### `user_agent`

- **Type**: `str`
- **Default**: `'Entitybase/1.0 User:So9q'`
- **Description**: other

### `user_stats_enabled`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

### `user_stats_schedule`

- **Type**: `str`
- **Default**: `'0 2 * * *'`
- **Description**: No description available

### `general_stats_enabled`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

### `general_stats_schedule`

- **Type**: `str`
- **Default**: `'0 2 * * *'`
- **Description**: No description available

### `json_dump_enabled`

- **Type**: `bool`
- **Default**: `True`
- **Description**: JSON dump worker

### `json_dump_schedule`

- **Type**: `str`
- **Default**: `'0 2 * * 0'`
- **Description**: No description available

### `json_dump_batch_size`

- **Type**: `int`
- **Default**: `1000`
- **Description**: No description available

### `json_dump_generate_checksums`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

### `ttl_dump_enabled`

- **Type**: `bool`
- **Default**: `True`
- **Description**: TTL dump worker

### `ttl_dump_schedule`

- **Type**: `str`
- **Default**: `'0 3 * * 0'`
- **Description**: No description available

### `ttl_dump_batch_size`

- **Type**: `int`
- **Default**: `1000`
- **Description**: No description available

### `ttl_dump_compression`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

### `ttl_dump_generate_checksums`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

## Usage Example

```python
from models.config.settings import settings

# Access a setting
api_port = settings.api_port

# Override via environment
# export VITESS_HOST=my-custom-host
```

## Docker Configuration

Key settings for Docker deployment:


- `VITESS_HOST`: Vitess database host (default: vitess)
- `VITESS_PORT`: Vitess database port (default: 15309)
- `S3_ENDPOINT`: S3-compatible storage endpoint (default: http://minio:9000)
- `KAFKA_BROKERS`: Kafka broker addresses for change streaming

