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
    │       ├── repositories
    │       └── storage
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
    │       └── v1
    │           ├── endpoints
    │           ├── handlers
    │           │   └── entity
    │           │       ├── lexeme
    │           │       └── property
    │           ├── routes
    │           ├── services
    │           └── utils
    ├── services
    ├── utils
    ├── validation
    └── workers
        ├── backlink_statistics
        ├── dev
        ├── entity_diff
        ├── general_stats
        ├── id_generation
        ├── incremental_rdf
        ├── json_dumps
        ├── notification_cleanup
        ├── ttl_dumps
        ├── user_stats
        └── watchlist_consumer

63 directories
```
