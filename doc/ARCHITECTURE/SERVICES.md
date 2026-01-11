# Services Overview

## BacklinkStatisticsService

**Location**: `models/rest_api/services/backlink_statistics_service.py`
**Purpose**: Service for computing backlink statistics.

**Methods**:

- `compute_daily_stats(vitess_client)`
  - Compute comprehensive backlink statistics for current date.

- `get_total_backlinks(vitess_client)`
  - Count total backlink relationships.

- `get_entities_with_backlinks(vitess_client)`
  - Count entities that have incoming backlinks.

- `get_top_entities_by_backlinks(vitess_client, limit)`
  - Get top entities ranked by backlink count.

**Dependencies**:

- `models.infrastructure.vitess_client.VitessClient`
- `models.rest_api.response.misc.BacklinkStatisticsData`
- `models.rest_api.response.misc.TopEntityByBacklinks`

## EnumerationService

**Location**: `models/rest_api/services/enumeration_service.py`
**Purpose**: Service for managing entity ID enumeration across different entity types.

**Methods**:

- `get_next_entity_id(entity_type)`
  - Get the next available entity ID for the given entity type.

- `get_range_status()`
  - Get status of ID ranges for monitoring.

- `confirm_id_usage(entity_id)`
  - Confirm that an ID has been successfully used (handshake with worker).

**Dependencies**:

- `models.infrastructure.vitess_client.VitessClient`

## RedirectService

**Location**: `models/rest_api/services/redirects.py`
**Purpose**: Service for managing entity redirects

**Dependencies**:

- `models.infrastructure.stream.producer.ChangeType`
- `models.infrastructure.stream.producer.EntityChangeEvent`
- `models.infrastructure.stream.producer.StreamProducerClient`
- `models.rest_api.misc.EditType`
- `models.rest_api.request.entity.EntityRedirectRequest`
- `models.rest_api.response.entity.EntityRedirectResponse`
- `models.rest_api.response.entity.EntityResponse`
- `models.validation.utils.raise_validation_error`
- `models.infrastructure.s3.s3_client.S3Client`
- `models.infrastructure.vitess_client.VitessClient`

