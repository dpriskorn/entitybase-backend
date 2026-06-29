# EntitybaseBase Implementation Plan

## Summary
Create a shared `EntitybaseBase` Pydantic base class with `extra="forbid"` that replaces direct inheritance from `BaseModel` for all **root** model classes. Subclasses that inherit from other models in the codebase will automatically inherit the config through the parent chain.

---

## Current State

| Metric | Count |
|--------|-------|
| Root BaseModel classes (direct `BaseModel` inheritance) | ~60 |
| Files with root BaseModel imports | ~40 |
| Classes already with `extra="forbid"` | 23 |
| Existing model_config overrides (frozen, arbitrary_types_allowed, etc) | ~40 |

---

## Key Insight

In Pydantic v2, `model_config` **inherits and overrides** from parent:
- Parent: `extra="forbid"`
- Child with `frozen=True`: gets `frozen=True` (forbid still applies unless overridden)

Thus only **root** classes need modification (~60 classes). Subclasses automatically inherit.

---

## Root Classes to Modify

These are classes that directly inherit from `BaseModel` (not from another custom class in this codebase):

### 1. Core Entity Models (~15 classes)
| File | Classes |
|------|---------|
| `src/models/data/rest_api/v1/entitybase/response/entity/entitybase.py` | EntityLabelsResponse, EntityDescriptionsResponse, EntityAliasesResponse, EntityStatementsResponse, EntitySitelinksResponse, EntityHistoryEntry, EntityResponse, EntityDeleteResponse, EntityRedirectResponse, EntityListItem, EntityListResponse, EntityMetadataResponse, EntityMetadataBatchResponse, ProtectionResponse, EntityJsonImportResponse |
| `src/models/data/rest_api/v1/entitybase/response/entity/revision_read_response.py` | RevisionReadResponse |

### 2. Lexeme Responses (~13 classes)
| File | Classes |
|------|---------|
| `src/models/data/rest_api/v1/entitybase/response/lexemes.py` | RepresentationData, LemmaResponse, LemmasResponse, FormResponse, SenseResponse, FormsResponse, SensesResponse, FormRepresentationResponse, FormRepresentationsResponse, SenseGlossesResponse, SenseGlossResponse, LexemeLanguageResponse, LexemeLexicalCategoryResponse |

### 3. Request Models (~25 classes)
| File | Classes |
|------|---------|
| `src/models/data/rest_api/v1/entitybase/request/entity/sitelink.py` | SitelinkData |
| `src/models/data/rest_api/v1/entitybase/request/entity/context.py` | EventPublishContext, TermUpdateContext, GeneralStatisticsContext, StatementWriteContext, ProcessEntityRevisionContext, CreationTransactionContext, SitelinkUpdateContext, RevisionContext |
| `src/models/data/rest_api/v1/entitybase/request/entity/patch.py` | JsonPatchOperation, BasePatchRequest |
| `src/models/data/rest_api/v1/entitybase/request/entity/misc.py` | EntityRedirectRequest, EntityJsonImportRequest |
| `src/models/data/rest_api/v1/entitybase/request/entity/entity_delete_request.py` | EntityDeleteRequest |
| `src/models/data/rest_api/v1/entitybase/request/entity/entity_request_base.py` | EntityRequestBase |
| `src/models/data/rest_api/v1/entitybase/request/entity/revision.py` | CreateRevisionRequest |

### 4. Response Models (~20 classes)
| File | Classes |
|------|---------|
| `src/models/data/rest_api/v1/entitybase/response/user.py` | UserResponse, UserCreateResponse, WatchlistToggleResponse, MessageResponse, NotificationResponse |
| `src/models/data/rest_api/v1/entitybase/response/watchlist.py` | WatchlistEntryResponse, WatchlistResponse |
| `src/models/data/rest_api/v1/entitybase/response/events.py` | RDFChangeEvent |
| `src/models/data/rest_api/v1/entitybase/response/entity/backlinks.py` | BacklinkResponse, BacklinksResponse |
| `src/models/data/rest_api/v1/entitybase/response/entity_data.py` | PropertiesResponse, EntitiesResponse, EntityJsonResponse, TurtleResponse, TopEntityByBacklinks, ElasticsearchDocumentResponse, MeilisearchDocumentResponse |

### 5. Infrastructure Records (~15 classes)
| File | Classes |
|------|---------|
| `src/models/data/infrastructure/vitess/records/revision.py` | RevisionRecord, HistoryRevisionItemRecord |
| `src/models/data/infrastructure/vitess/records/history.py` | HistoryRecord |
| `src/models/data/infrastructure/vitess/records/small_objects.py` | StatementRecord, QualifierRecord, ReferenceRecord, SnakRecord |
| `src/models/data/infrastructure/meilisearch/__init__.py` | FlattenedClaims, MeilisearchDocument, MeilisearchDocumentResponse |
| `src/models/data/infrastructure/s3/hashes/hash_maps.py` | HashMaps |

### 6. Service Classes (~10 classes)
| File | Classes |
|------|---------|
| `src/models/services/meilisearch/client.py` | MeilisearchClient |
| `src/models/rest_api/entitybase/v1/services/statement_service.py` | StatementProcessingContext |
| `src/models/rest_api/entitybase/v1/services/id_range_manager.py` | IdRange, IdRangeManager |
| `src/models/rest_api/entitybase/v1/services/enumeration_service.py` | EnumerationService |
| `src/models/rest_api/entitybase/v1/utils/lexeme_term_processor.py` | TermProcessingConfig, LexemeTermProcessorConfig |
| `src/models/rest_api/entitybase/v1/services/status_service.py` | RevisionParams |

### 7. Config & Settings (~1 class)
| File | Classes |
|------|---------|
| `src/models/config/settings.py` | Settings (keep `extra="ignore"`) |

### 8. Worker/Utility Classes (~30 classes)
| File | Classes |
|------|---------|
| `src/models/workers/create/*.py` | CreateTopics, CreateTables, CreateBuckets |
| `src/models/workers/incremental_rdf/rdf_change_builder.py` | RDFDataField, RDFChangeEvent, EventConfig |
| `src/models/workers/dump_types.py` | EntityDumpRecord, DumpMetadata |
| `src/models/workers/entity_diff/*.py` | RDFSerializer, RDFCanonicalizer, EntityDiffResponse, EntityDiffRequest |
| `src/models/validation/json_schema_validator.py` | JsonSchemaValidator |
| `src/models/services/wikidata_import_service.py` | WikidataImportService |
| `src/models/rest_api/entitybase/v1/routes/users.py` | UserActivityQuery |
| `src/models/rest_api/entitybase/v1/result.py` | RevisionResult |
| `src/models/rest_api/entitybase/v1/handlers/state.py` | StateHandler |
| `src/models/rest_api/entitybase/v1/handlers/entity/update_terms.py` | TermTransactionContext |

---

## Implementation

### Step 1: Create EntitybaseBase in `src/models/__init__.py`

```python
from pydantic import ConfigDict

class EntitybaseBase(ConfigDict):
    """Base class for all Entitybase Pydantic models.
    
    Provides default strict validation by forbidding extra fields.
    Subclasses can override model_config for specific needs.
    """
    
    model_config = ConfigDict(extra="forbid")
```

### Step 2: Migrate root classes (Pattern: Replace BaseModel with EntitybaseBase)

**Before:**
```python
from pydantic import BaseModel, Field

class Foo(BaseModel):
    name: str
```

**After:**
```python
from models import EntitybaseBase

class Foo(EntitybaseBase):
    name: str
```

### Step 3: Handle existing model_config overrides

Classes with existing `model_config` will override base - no changes needed:

```python
# This already works - child's config overrides parent
class Bar(EntitybaseBase):
    model_config = ConfigDict(frozen=True)  # frozen preserved, extra still "forbid"
```

**Exception:** `Settings` class should keep `extra="ignore"`:
```python
class Settings(EntitybaseBase):
    model_config = {"extra": "ignore"}  # Override to keep existing behavior
```

---

## Quality Gates

1. `make ruff` - Linter
2. `make mypy` - Type checker  
3. `make test-unit` - Unit tests
4. `make test-e2e` - E2E tests
5. `make test-integration` - Integration tests

---

## Risk Assessment

**Low Risk:**
- Only ~60 root classes need modification (not all 290)
- Pydantic v2 allows config override from parent
- Existing model_config preserved

**Medium Risk:**
- Some classes may rely on extra fields being ignored
- Need to verify test pass rate

**Mitigation:**
- Run full test suite after migration
- Check for ValidationError in test output