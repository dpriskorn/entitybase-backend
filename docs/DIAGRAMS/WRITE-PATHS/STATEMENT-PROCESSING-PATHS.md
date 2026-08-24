# Statement Processing Paths

## Statement Addition Path (During Entity Create/Update)

```mermaid
flowchart TD
    A[Extract Claims from entity_data] --> B[Extract Properties]
    B --> C[Compute Property Counts]
    C --> D[For Each Property]
    D --> E[For Each Statement]
    E --> F[Validate Statement]
    F --> G[Hash Statement]
    G --> H[Deduplicate and Store]
    H --> I{Statement exists in Vitess?}
    I -->|Yes| J[Increment ref_count]
    I -->|No| K[Write to MariaDB]
    K --> L[Insert Statement Content in Vitess]
    J --> M[Collect Hash for Entity Revision]
    L --> M
```

## Statement Modification Path (During Entity Update)

```mermaid
flowchart TD
    A[Extract New Claims] --> B[Extract New Properties]
    B --> C[Compute New Property Counts]
    C --> D[Compare with Previous Revision]
    D --> E[For Modified Statements]
    E --> F[Decrement Old Hash ref_count]
    F --> G{ref_count == 0?}
    G -->|Yes| H[Delete from MariaDB]
    G -->|No| I[Hash New Statement]
    H --> I
    I --> J[Deduplicate and Store New]
    J --> K[Store Updated Revision]
```

## Statement Removal Path (During Entity Update)

```mermaid
flowchart TD
    A[Extract New Claims] --> B[Compare with Previous Claims]
    B --> C[For Removed Statements]
    C --> D[Decrement Ref Count]
    D --> E{ref_count == 0?}
    E -->|Yes| F[Delete from MariaDB]
    E -->|No| G[Delete Statement Content from Vitess]
    F --> G
    G --> H[Extract Properties]
    H --> I[Compute Property Counts]
    I --> J[Store Updated Revision]
```

## Shared Deduplication Logic

```mermaid
flowchart TD
    A[For Each Statement Hash] --> B[Validate Statement Schema]
    B --> C{Statement exists in MariaDB?}
    C -->|Yes| D[Increment ref_count in Vitess]
    C -->|No| E[Write to MariaDB]
    E --> F[Insert Statement Content in Vitess]
    D --> G[Collect Hash]
    F --> G
```

Note: All statement operations occur within entity updates. Individual statement CRUD is not supported; statements are managed as part of entity revisions with reference counting for deduplication.
