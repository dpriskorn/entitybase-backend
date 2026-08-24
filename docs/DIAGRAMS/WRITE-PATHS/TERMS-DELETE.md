# Terms DELETE Process

## Term DELETE Path (Removing Labels/Descriptions for Language)

```mermaid
flowchart TD
    A[Receive DELETE Request] --> B[Validate Clients: vitess and s3]
    B --> C[Check Entity Exists]
    C -->|not found| C1[Return 404]
    C --> D[Check Not Deleted]
    D -->|deleted| D1[Return 410]
    D --> E[Check Permissions]
    E -->|denied| E1[Return 403]
    E --> F[Get Current Entity]
    F --> G[Extract Term Type: labels or descriptions]
    G --> H{Term Exists?}
    H -->|No| H1[Return current entity - idempotent]
    H -->|Yes| I[Remove Term from Entity Data]
    I --> J[Calculate New Revision ID]
    J --> K[Prepare Revision Data]
    K --> L[Hash Entity Content]
    L --> M[Process Term Storage Updates]
    M --> N[Write Revision to MariaDB]
    N --> O[Update Vitess Revision Table]
    O --> P[Update Head Pointer]
    P --> Q[Publish Change Event]
    Q --> R[Return EntityResponse]
```

## Term DELETE Validation

```mermaid
flowchart TD
    A[Validate Entity ID] -->|invalid| A1[Return 400]
    A --> B[Validate Language Code]
    B -->|invalid| B1[Return 400]
    B --> C[Validate Term Type]
    C -->|invalid| C1[Return 400]
    C --> D[Check Entity State]
    D --> E[Check User Permissions]
```

## Wikibase API Redirect

```mermaid
flowchart LR
    A[Receive Wikibase DELETE] --> B[Return 307 Redirect to entitybase endpoint]
```

## Error Handling

```
+--> Entity Not Found: 404 Not Found
+--> Entity Deleted: 410 Gone
+--> Entity Locked/Archived: 409 Conflict
+--> Invalid Language Code: 400 Bad Request
+--> Permission Denied: 403 Forbidden
+--> Storage Failure: 500 Internal Server Error
```

## Key Differences from Term PATCH

- **Complete Removal**: Deletes entire language entry vs partial array modification
- **No JSON Patch**: Simple key deletion vs complex operation application
- **Storage Cleanup**: Removes term entries entirely vs updating arrays
- **Idempotent**: Safe to delete non-existent terms
- **Term Type Scope**: Applies to labels/descriptions, not aliases

## Performance Characteristics

- **Read Operations**: 1 entity read, 1 revision fetch from MariaDB
- **Write Operations**: 1 revision write to MariaDB, 1 Vitess term delete (for labels)
- **Hash Calculations**: Full entity re-hash (simpler than PATCH selective updates)
- **Storage Impact**: Complete term removal vs array element modification

## Relationship to Term PATCH

- **Labels/Descriptions**: DELETE removes entire language entry
- **Aliases**: PATCH modifies array contents (no DELETE for aliases)
- **Use Cases**:
| Operation | Labels/Descriptions | Aliases |
|-----------|-------------------|---------|
| Remove Language | DELETE /labels/{lang} | PATCH with remove operations |
| Clear All | DELETE /labels/{lang} | PATCH remove all elements |
| Selective Edit | N/A | PATCH add/remove/replace |

Note: Term DELETE provides complete language-level removal for labels and descriptions, while PATCH handles granular alias modifications. Both follow entity update patterns with selective storage cleanup and full revision history preservation.
