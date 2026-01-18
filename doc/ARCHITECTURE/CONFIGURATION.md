# Configuration Overview

This document describes all configuration options available in wikibase-backend.

Settings are managed through the `Settings` class in `src/models/config/settings.py`.

## Environment Variables

All settings can be overridden using environment variables with the same name.


## Database Settings

### `vitess_host`

- **Type**: `str`
- **Default**: `'vitess'`
- **Description**: No description available

### `vitess_port`

- **Type**: `int`
- **Default**: `15309`
- **Description**: No description available

### `vitess_database`

- **Type**: `str`
- **Default**: `'entitybase'`
- **Description**: No description available

### `vitess_user`

- **Type**: `str`
- **Default**: `'root'`
- **Description**: No description available

### `vitess_password`

- **Type**: `str`
- **Default**: `''`
- **Description**: No description available

## Storage Settings

### `s3_endpoint`

- **Type**: `str`
- **Default**: `'http://minio:9000'`
- **Description**: No description available

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
- **Default**: `'testbucket-references'`
- **Description**: No description available

### `s3_qualifiers_bucket`

- **Type**: `str`
- **Default**: `'testbucket-qualifiers'`
- **Description**: No description available

### `s3_sitelinks_bucket`

- **Type**: `str`
- **Default**: `'testbucket-sitelinks'`
- **Description**: No description available

### `s3_statements_bucket`

- **Type**: `str`
- **Default**: `'testbucket-statements'`
- **Description**: No description available

### `s3_terms_bucket`

- **Type**: `str`
- **Default**: `'testbucket-terms'`
- **Description**: No description available

### `s3_revisions_bucket`

- **Type**: `str`
- **Default**: `'testbucket-revisions'`
- **Description**: No description available

### `s3_schema_revision_version`

- **Type**: `str`
- **Default**: `'latest'`
- **Description**: No description available

### `s3_statement_version`

- **Type**: `str`
- **Default**: `'latest'`
- **Description**: No description available

## Workers Settings

### `backlink_stats_enabled`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

### `backlink_stats_schedule`

- **Type**: `str`
- **Default**: `'0 2 * * *'`
- **Description**: No description available

### `backlink_stats_top_limit`

- **Type**: `int`
- **Default**: `100`
- **Description**: No description available

## RDF Settings

### `kafka_entitychange_rdf_topic`

- **Type**: `str`
- **Default**: `'entitybase.entity_ttl_diff'`
- **Description**: No description available

## Development Settings

### `log_level`

- **Type**: `str`
- **Default**: `'INFO'`
- **Description**: No description available

### `test_log_level`

- **Type**: `str`
- **Default**: `'INFO'`
- **Description**: No description available

### `test_log_http_requests`

- **Type**: `bool`
- **Default**: `False`
- **Description**: No description available

### `test_show_progress`

- **Type**: `bool`
- **Default**: `True`
- **Description**: No description available

## Other Settings

### `wmf_recentchange_version`

- **Type**: `str`
- **Default**: `'latest'`
- **Description**: No description available

### `wikibase_repository_name`

- **Type**: `str`
- **Default**: `'wikidata'`
- **Description**: No description available

### `property_registry_path`

- **Type**: `str`
- **Default**: `'properties'`
- **Description**: No description available

### `expose_original_exceptions`

- **Type**: `bool`
- **Default**: `False`
- **Description**: No description available

### `enable_streaming`

- **Type**: `bool`
- **Default**: `False`
- **Description**: No description available

### `kafka_brokers`

- **Type**: `str`
- **Default**: `''`
- **Description**: No description available

### `kafka_entitychange_json_topic`

- **Type**: `str`
- **Default**: `'entitybase.entity_change'`
- **Description**: No description available

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

