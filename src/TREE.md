src/
├── models
│   ├── config
│   ├── infrastructure
│   │   ├── s3
│   │   │   ├── hashes
│   │   │   ├── revision
│   │   │   └── storage
│   │   ├── stream
│   │   └── vitess
│   │       ├── records
│   │       └── repositories
│   ├── internal_representation
│   │   └── values
│   ├── json_parser
│   │   └── values
│   ├── rdf_builder
│   │   ├── hashing
│   │   ├── models
│   │   ├── ontology
│   │   ├── property_registry
│   │   └── writers
│   ├── rest_api
│   │   └── entitybase
│   │       ├── handlers
│   │       │   └── entity
│   │       │       ├── items
│   │       │       ├── lexeme
│   │       │       └── property
│   │       ├── request
│   │       │   └── entity
│   │       ├── response
│   │       │   └── entity
│   │       ├── routes
│   │       ├── services
│   │       └── versions
│   │           └── v1
│   ├── services
│   ├── validation
│   └── workers
│       ├── backlink_statistics
│       ├── dev
│       ├── general_stats
│       ├── id_generation
│       ├── notification_cleanup
│       ├── user_stats
│       └── watchlist_consumer
└── schemas
    ├── entitybase
    │   ├── entities
    │   │   ├── 1.0.0
    │   │   └── latest
    │   ├── entity
    │   │   ├── 1.0.0
    │   │   └── latest
    │   ├── events
    │   │   ├── endorsechange
    │   │   │   ├── 1.0.0
    │   │   │   └── latest
    │   │   ├── entitychange
    │   │   │   ├── 1.0.0
    │   │   │   └── latest
    │   │   ├── entitypropertychange
    │   │   │   ├── 1.0.0
    │   │   │   └── latest
    │   │   └── newthank
    │   │       ├── 1.0.0
    │   │       └── latest
    │   └── s3
    │       ├── revision
    │       │   ├── 1.0.0
    │       │   ├── 1.1.0
    │       │   ├── 1.2.0
    │       │   ├── 2.0.0
    │       │   ├── 2.1.0
    │       │   ├── 3.0.0
    │       │   └── latest
    │       └── statement
    │           ├── 1.0.0
    │           └── latest
    └── wikibase
        └── entity
            ├── 1.0.0
            └── latest

84 directories
