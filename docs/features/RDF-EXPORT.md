# RDF Export

Export entities as RDF Turtle format for semantic web integration.

## Overview

Entitybase can export entity data as RDF (Resource Description Framework) in Turtle format. This enables integration with semantic web applications, knowledge graphs, and linked data systems.

## Formats

### Turtle (TTL)
RDF Triple format — human-readable and widely supported.

```turtle
@prefix wd: <http://www.wikidata.org/entity/> .
@prefix wdt: <http://www.wikidata.org/prop/direct/> .

wd:Q1 wdt:P31 wd:Q5 .
wd:Q1 rdfs:label "Pizza"@en .
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET `/entities/{type}/{id}.ttl` | Get entity as Turtle |
| GET `/rdf/entities.ttl` | Get all entities as Turtle |

## Features

- Full entity serialization (labels, descriptions, statements)
- Reference embedding
- Qualifier support
- Redirect handling (owl:sameAs)

## Status

- **Alpha** — Under active development
- RDF/XML and NTriples not planned

See also: [RDF Builder](../ARCHITECTURE/RDF-BUILDER/RDF-BUILDER-IMPLEMENTATION.md)
