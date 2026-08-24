# Terms PUT Process

## Term PUT Path (Setting Labels/Descriptions for Language)

```mermaid
flowchart TD
    A[Receive PUT Request] --> B[Extract term data]
    B --> C[Validate Clients: vitess and s3]
    C --> D[Check Entity Exists]
    D -->|not found| D1[Return 404]
    D --> E[Check Not Deleted]
    E -->|deleted| E1[Return 410]
    E --> F[Check Permissions]
    F -->|denied| F1[Return 403]
    F --> G[Get Current Entity]
    G --> H[Extract Term Type: labels or descriptions]
    H --> I[Validate Term Data]
    I --> J[Update Entity Data]
    J --> K[Calculate New Revision ID]
    K --> L[Prepare Revision Data]
    L --> M[Hash Entity Content]
    M --> N[Process Term Storage Updates]
    N --> O[Write Revision to MariaDB]
    O --> P[Update Vitess Revision Table]
    P --> Q[Update Head Pointer]
    Q --> R[Publish Change Event]
    R --> S[Return EntityResponse]
```

## Term PUT Validation

```mermaid
flowchart TD
    A[Validate Entity ID] -->|invalid| A1[Return 400]
    A --> B[Validate Language Code]
    B -->|invalid| B1[Return 400]
    B --> C[Validate Term Type]
    C -->|invalid| C1[Return 400]
    C --> D[Validate Request Body]
    D --> E[Check Entity State]
    E --> F[Check User Permissions]
```

## Wikibase API Redirect

```mermaid
flowchart LR
    A[Receive Wikibase PUT] --> B[Return 307 Redirect to entitybase endpoint]
```

## Request Format Examples

### Labels PUT
```json
{
  "value": "English mathematician and writer",
  "tags": [],
  "bot": false,
  "comment": "set English label"
}
```

### Descriptions PUT (Wikibase format)
```json
{
  "description": "the subject is a concrete object (instance) of this class, category, or object group",
  "tags": [],
  "bot": false,
  "comment": "set English description"
}
```

## Error Handling

```
+--> Entity Not Found: 404 Not Found
+--> Entity Deleted: 410 Gone
+--> Entity Locked/Archived: 409 Conflict
+--> Invalid Request Format: 400 Bad Request
+--> Term Value Too Long: 400 Bad Request
+--> Permission Denied: 403 Forbidden
+--> Storage Failure: 500 Internal Server Error
```

## Key Differences from PATCH Operations

- **Complete Replacement**: PUT replaces entire term value vs PATCH partial modifications
- **Simple Validation**: Direct value validation vs JSON Patch operation validation
- **Storage Updates**: Full term replacement in storage vs selective updates
- **Use Cases**:
| Operation | Labels/Descriptions | Aliases |
|-----------|-------------------|---------|
| Set/Replace | PUT /labels/{lang} | PATCH add/replace operations |
| Partial Edit | N/A | PATCH operations |
| Language Add | PUT (creates if missing) | PATCH add operations |

## Performance Characteristics

- **Read Operations**: 1 entity read, 1 revision fetch from MariaDB
- **Write Operations**: 1 revision write to MariaDB, 1 Vitess term insert (for labels)
- **Hash Calculations**: Full entity re-hash + individual term hash
- **Storage Impact**: New term storage + updated revision metadata

## Relationship to Other Term Operations

- **GET**: Retrieve term value
- **PUT**: Set/replace entire term value
- **PATCH**: Apply partial modifications (aliases only)
- **DELETE**: Remove term entirely

Note: Term PUT provides complete value replacement for labels and descriptions, following entity update patterns with selective term storage management and full revision history preservation.
