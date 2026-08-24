# Terms PATCH Process

## Term PATCH Path (JSON Patch Operations on Aliases)

```mermaid
flowchart TD
    A[Receive PATCH Request] --> B[Extract patch array]
    B --> C[Validate patch format]
    C --> D[Validate Clients: vitess and s3]
    D --> E[Check Entity Exists]
    E -->|not found| E1[Return 404]
    E --> F[Check Not Deleted]
    F -->|deleted| F1[Return 410]
    F --> G[Check Permissions]
    G -->|denied| G1[Return 403]
    G --> H[Get Current Entity]
    H --> I[Extract Current Aliases]
    I --> J[For Each Patch Operation]
    J --> K{Validate Operation}
    K -->|invalid| K1[Return 400]
    K --> L[Parse Path]
    L --> M[Apply Operation to aliases]
    M --> N[Update Entity Data]
    N --> O[Calculate New Revision ID]
    O --> P[Prepare Revision Data]
    P --> Q[Hash Entity Content]
    Q --> R[Process Term Storage Updates]
    R --> S[Write Revision to MariaDB]
    S --> T[Update Vitess Revision Table]
    T --> U[Update Head Pointer]
    U --> V[Publish Change Event]
    V --> W[Return EntityResponse]
```

## Term PATCH Validation

```mermaid
flowchart TD
    A[Validate Entity ID] -->|invalid| A1[Return 400]
    A --> B[Validate Language Code]
    B -->|invalid| B1[Return 400]
    B --> C[Validate Patch Array]
    C --> D[Validate Each Operation]
    D --> E[Check Required Fields]
    E --> F[Check Array Bounds]
```

## Wikibase API Redirect

```mermaid
flowchart LR
    A[Receive Wikibase PATCH] --> B[Return 307 Redirect to entitybase endpoint]
```

## Error Handling

```
+--> Invalid Patch Format: 400 Bad Request - "Invalid JSON Patch operation"
+--> Entity Not Found: 404 Not Found
+--> Permission Denied: 403 Forbidden
+--> Array Index Out of Bounds: 400 Bad Request - "Invalid array index"
+--> Unsupported Operation: 400 Bad Request - "Unsupported patch operation"
+--> Storage Failure: 500 Internal Server Error
```

## Key Differences from Full Entity Update

- **Targeted Modification**: Only aliases for one language are modified
- **JSON Patch Semantics**: Partial updates vs full replacement
- **Validation Complexity**: Array index validation + operation validation
- **Storage Updates**: Selective term storage updates vs full re-hash
- **Event Type**: TERM_PATCH vs ENTITY_UPDATE

## Performance Characteristics

- **Read Operations**: 1 entity read, 1 revision fetch from MariaDB
- **Write Operations**: 1 revision write to MariaDB, N Vitess term inserts/deletes
- **Hash Calculations**: Only for modified aliases, not entire entity
- **Revision Creation**: Same as entity update but with selective term processing

Note: Term PATCH operations follow entity update patterns but with JSON Patch semantics for precise alias modifications. This provides fine-grained control while maintaining revision history and deduplication benefits.
