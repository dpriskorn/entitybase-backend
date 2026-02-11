# Tree
```
src/
└── models
    ├── config
    ├── data
    │   ├── config
    │   ├── infrastructure
    │   │   ├── s3
    │   │   │   └── hashes
    │   │   ├── stream
    │   │   └── vitess
    │   │       └── records
    │   ├── rest_api
    │   │   └── v1
    │   │       └── entitybase
    │   │           ├── request
    │   │           │   └── entity
    │   │           └── response
    │   │               └── entity
    │   └── workers
    ├── infrastructure
    │   ├── s3
    │   │   ├── revision
    │   │   └── storage
    │   ├── stream
    │   └── vitess
    │       └── repositories
    ├── internal_representation
    │   └── values
    ├── json_parser
    │   └── values
    ├── rdf_builder
    │   ├── hashing
    │   ├── models
    │   ├── ontology
    │   ├── property_registry
    │   └── writers
    ├── rest_api
    │   └── entitybase
    │       ├── handlers
    │       │   └── entity
    │       │       ├── items
    │       │       ├── lexeme
    │       │       └── property
    │       ├── request
    │       │   └── entity
    │       ├── response
    │       │   └── entity
    │       ├── routes
    │       ├── services
    │       ├── v1
    │       │   ├── endpoints
    │       │   ├── handlers
    │       │   │   └── entity
    │       │   │       ├── lexeme
    │       │   │       └── property
    │       │   ├── routes
    │       │   ├── services
    │       │   └── utils
    │       └── versions
    │           └── v1
    ├── services
    ├── validation
    └── workers
        ├── backlink_statistics
        ├── dev
        ├── entity_diff
        ├── general_stats
        ├── id_generation
        ├── notification_cleanup
        ├── user_stats
        └── watchlist_consumer

71 directories
```
