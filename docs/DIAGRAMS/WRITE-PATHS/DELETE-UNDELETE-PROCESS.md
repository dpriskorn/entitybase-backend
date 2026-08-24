# Delete/Undelete Process

## Entity Delete Process

```mermaid
flowchart TD
    A[EntityDeleteHandler] --> B[Validate Clients]
    B --> C[Check Entity Exists]
    C -->|not found| C1[Return 404]
    C --> D[Check Not Already Deleted]
    D -->|already deleted| D1[Return 410]
    D --> E[Get Head Revision]
    E --> F[Check Protection]
    F -->|archived or locked| F1[Return 409]
    F --> G[Calculate New Revision]
    G --> H[Read Current Revision from MariaDB]
    H -->|revision not found| H1[Return 404]
    H --> I[Prepare Delete Revision Data]
    I --> J{Hard Delete?}
    J -->|Yes| K[Decrement ref_count for all statements]
    J -->|No| L[Write Delete Revision to MariaDB]
    K --> L
    L --> M[Update Head Pointer]
    M --> N[Publish Event]
    N --> O[Return EntityDeleteResponse]
```

## Entity Undelete Process

Undelete is not implemented as a separate operation in the current codebase. Soft-deleted entities can be "undeleted" by performing an update operation that sets is_deleted=False in the revision data, effectively restoring the entity to an active state. This would follow the standard ENTITY UPDATE PROCESS.
