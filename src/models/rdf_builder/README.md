# RDF Builder

## Overview

Converts internal Entity models to RDF (Turtle format) following Wikibase RDF mapping rules.

**Parser Status:** ✓ COMPLETE
**RDF Generation Status:** ✅ CORE FEATURES COMPLETE
**Test Coverage:** 🔄 PHASE 2 COMPLETE, PHASE 3 IN PROGRESS

---

## Quick Start

### Basic Entity Conversion

```python
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.loader import load_property_registry
from models.json_parser.entity_parser import parse_entity
from pathlib import Path

# Load property registry
registry = load_property_registry(Path("test_data/properties/"))

# Create converter
converter = EntityConverter(property_registry=registry)

# Parse entity JSON
with open("test_data/json/entities/Q42.json", "r") as f:
    entity_json = json.load(f)
    entity = parse_entity(entity_json)

# Convert to Turtle
ttl = converter.convert_to_string(entity)
print(ttl)
```

### Convert with Referenced Entity Metadata

```python
converter = EntityConverter(
    property_registry=registry,
    entity_metadata_dir=Path("test_data/json/entities")
)

ttl = converter.convert_to_string(entity)
# Now includes wd:Qxxx metadata blocks for referenced entities
```

### Write to File

```python
with open("Q42.ttl", "w") as f:
    converter.convert_to_turtle(entity, f)
```

### Parser Capabilities

- ✓ Entity parsing (Entity model)
- ✓ Labels (72 languages in Q42)
- ✓ Descriptions (116 languages in Q42)
- ✓ Aliases (25 entries in Q42)
- ✓ Statements (332 statements across 293 properties)
- ✓ Qualifiers (nested in statements)
- ✓ References (nested in statements)
- ✓ Sitelinks (129 entries in Q42)
- ✓ All value types (entity, time, string, quantity, etc.)
- ✓ All ranks (normal, preferred, deprecated)
- ✓ All snaktypes (value, novalue, somevalue)

### RDF Generation Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Entity type declaration | ✓ Implemented | `wikibase:Item` |
| Labels | ✓ Implemented | `rdfs:label` triples |
| Descriptions | ✓ Implemented | `schema:description` triples |
| Aliases | ✓ Implemented | `skos:altLabel` triples |
| Statements (basic) | ✓ Implemented | `p:Pxxx`, `ps:Pxxx` triples |
| Statement rank types | ✓ Implemented | BestRank, NormalRank, DeprecatedRank |
| Qualifiers | ✓ Implemented | `pq:Pxxx` triples with values |
| References | ✓ Implemented | `pr:Pxxx` triples with values |
| Sitelinks | ✓ Implemented | `schema:sameAs` triples |
| Dataset metadata | ✓ Implemented | Software version, dateModified, counts |
| Turtle prefixes | ✓ Implemented | 30 prefixes for output |
| **Structural Support** | | |
| Property metadata structure | ✓ Implemented | PropertyShape has labels/descriptions fields |
| Property metadata loading | ✓ Implemented | Loader merges JSON + CSV, with tests |
| **Property Metadata Output** | | |
| Property metadata integration | ✓ Implemented | `EntityConverter._write_property_metadata()` writes all property blocks |
| Property metadata RDF output | ✓ Implemented | `write_property_metadata()` generates wd:Pxxx blocks |
| Property entity metadata | ✓ Implemented | Property metadata block with labels, descriptions |
| Property predicate declarations | ✓ Implemented | `write_property()` generates owl:ObjectProperty |
| Property value predicates | ✓ Implemented | `write_property_metadata()` includes value predicates |
| No value constraints | ✓ Implemented | `write_novalue_class()` generates wdno:Pxxx blocks |
| Direct claim triples | ✓ Implemented | `write_direct_claim()` generates wdt:Pxxx for best-rank |
 | Referenced entity metadata | ✓ Implemented | Collects and writes wd:Qxxx metadata blocks |
 | **Structured Value Nodes** | | |
 | Time value decomposition | ✓ Implemented | `wdv:` nodes with timeValue, timePrecision, timeTimezone, timeCalendarModel |
 | Quantity value decomposition | ✓ Implemented | `wdv:` nodes with quantityAmount, quantityUnit |
 | Quantity value bounds | ✓ Implemented | `wdv:` nodes with optional quantityUpperBound, quantityLowerBound |
 | Globe coordinate decomposition | ✓ Implemented | `wdv:` nodes with geoLatitude, geoLongitude, geoPrecision, geoGlobe |
 | Value node linking | ✓ Implemented | psv:Pxxx, pqv:Pxxx, prv:Pxxx predicates linking to wdv: nodes |
 | Value node URI generation | ✓ Implemented | MD5-based hash for consistent `wdv:` IDs |
 | Qualifier value nodes | ✓ Implemented | pqv:Pxxx predicates link qualifiers to wdv: nodes |
 | Reference value nodes | ✓ Implemented | prv:Pxxx predicates link references to wdv: nodes |

---

## Architecture Overview

Based on `doc/ARCHITECTURE/JSON-RDF-CONVERTER.md`:

```
Entity (internal model)
     ↓
EntityConverter.convert_to_turtle()
     ↓
TripleWriters methods
     ↓
Turtle format RDF
```
Entity JSON (Wikidata API)
          ↓
    parse_entity() → Entity model
          ↓
    EntityConverter(property_registry=registry)
          ↓
    convert_to_turtle(entity, output)
          ↓
    TripleWriters methods:
   - write_entity_type()
   - write_dataset_triples()
   - write_label() (per language)
   - write_statement() (per statement)
     → ValueFormatter.format_value()
          ↓
    Turtle format RDF
```

---

## Components

### converter.py
**Main conversion class** that orchestrates RDF generation.

**Class:** `EntityConverter`
- **Required fields:** `property_registry: PropertyRegistry`
- **Optional fields:** `entity_cache_path: Path` - Path to entity JSON files for referenced entities
- **Methods:**
  - `convert_to_turtle(entity, output: TextIO)` - Write RDF to output stream
  - `convert_to_string(entity) -> str` - Return RDF as string
  - `_write_property_metadata(entity, output)` - Write property metadata blocks for properties used in entity
  - `_collect_referenced_entities(entity)` - Collect unique entity IDs referenced in statement values
  - `_load_referenced_entity(entity_id)` - Load entity from JSON cache
  - `_write_referenced_entity_metadata(entity, output)` - Write metadata blocks for referenced entities

**Usage:**
```python
registry = PropertyRegistry(properties={...})
converter = EntityConverter(property_registry=registry)
ttl = converter.convert_to_string(entity)
```

### writers/triple.py
**Triple writing utilities** for RDF generation.

**Class:** `TripleWriters` (static methods)
- `write_entity_type(output, entity_id)` - Write `a wikibase:Item`
- `write_dataset_triples(output, entity_id)` - Write dataset metadata
- `write_label(output, entity_id, lang, label)` - Write `rdfs:label`
- `write_statement(output, entity_id, statement, shape)` - Write full statement block
- `write_direct_claim(output, entity_id, property_id, value)` - Write direct claim triple (wdt:Pxxx) for best-rank

**Class:** `PropertyOntologyWriter` (static methods)
- `write_property_metadata(output, shape)` - Write full property metadata block with labels, descriptions, predicate links
- `write_property(output, shape)` - Write property predicate declarations (`owl:ObjectProperty`)
- `write_novalue_class(output, property_id)` - Write no-value constraint block with blank node

### property_registry/
**Property metadata** for RDF predicate mappings.

- **registry.py** - `PropertyRegistry` lookup table
- **loader.py** - Load from JSON files (merges labels/descriptions from JSON with datatype from CSV)
- **models.py** - `PropertyShape`, `PropertyPredicates` data models

### ontology/
**Property shape factory** based on datatypes.

- **datatypes.py** - `property_shape(pid, datatype, labels, descriptions)` creates predicate configurations with metadata

### writers/prefixes.py
**Turtle prefix declarations** for RDF output.

**Constant:** `TURTLE_PREFIXES` - 21 standard Wikidata prefixes

### value_formatters.py
**Value formatting** for RDF literals/URIs.

**Class:** `ValueFormatter` (static methods)
- `format_value(value) -> str` - Format any Value object as RDF
- `escape_turtle(value) -> str` - Escape special characters

### uri_generator.py
**URI generation** for entities, statements, references.

**Class:** `URIGenerator`
- `entity_uri(entity_id)` - `http://www.wikidata.org/entity/Q42`
- `data_uri(entity_id)` - Dataset URI with `.ttl` suffix
- `statement_uri(statement_id)` - Statement node URI
- `reference_uri(stmt_uri, idx)` - Reference node URI

---

## Data Flow

```
Entity JSON (Wikidata API)
         ↓
parse_entity() → Entity model
         ↓
EntityToRdfConverter(properties=registry)
         ↓
convert_to_turtle(entity, output)
         ↓
TripleWriters methods:
  - write_entity_type()
  - write_dataset_triples()
  - write_label() (per language)
  - write_statement() (per statement)
    → ValueFormatter.format_value()
         ↓
Turtle format RDF
```

---

## Test Failures Analysis

### test_q17948861_full_roundtrip

**Status:** FAILING - Missing RDF blocks in generated output

**Error:**
```
assert actual_blocks.keys() == golden_blocks.keys()
```

**Actual blocks (3):**
- wd:Q17948861
- data:Q17948861
- wds:Q17948861-FA20AC3A-5627-4EC5-93CA-24F0F00C8AA6

**Golden blocks (13):**
- data:Q17948861
- wd:Q17948861
- wds:Q17948861-FA20AC3A-5627-4EC5-93CA-24F0F00C8AA6
- **wd:Q17633526** (referenced entity - "Wikinews article")
- **wd:P31** (property entity with metadata)
- **p:P31** (predicate declaration)
- **psv:P31** (statement value predicate)
- **pqv:P31** (qualifier value predicate)
- **prv:P31** (reference value predicate)
- **wdt:P31** (direct claim predicate)
- **ps:P31** (statement predicate)
- **pq:P31** (qualifier predicate)
- **pr:P31** (reference predicate)
- **wdno:P31** (no value property)
- **_:0b8bd71b926a65ca3fa72e5d9103e4d6** (blank node constraint)

**Root cause:** Converter only generates entity and statement blocks, missing:
1. Referenced entity metadata blocks
2. Property entity metadata blocks
3. Property predicate declarations (owl:ObjectProperty)
4. Property value predicate declarations
5. No value constraint blocks with blank nodes

**Impact:** Tests fail because Wikidata's RDF dumps include full property ontology and referenced entity descriptions.

**Design decision needed:** Should converter generate:
- Full property ontology (all properties used)?
- Only properties referenced in the entity?
- Option to include/exclude property metadata blocks?

---

## Usage Example

### Basic Entity Conversion

```python
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.loader import load_property_registry
from models.json_parser.entity_parser import parse_entity

# Load property registry
registry = load_property_registry(Path("properties/"))

# Create converter
converter = EntityConverter(property_registry=registry)

# Parse entity JSON
with open("Q42.json", "r") as f:
    entity_json = json.load(f)
    entity = parse_entity(entity_json)

# Convert to Turtle
ttl = converter.convert_to_string(entity)
print(ttl)
```

### Output to File

```python
from io import StringIO

converter = EntityConverter(property_registry=registry)

# Write directly to file
with open("Q42.ttl", "w") as f:
    converter.convert_to_turtle(entity, f)
```

### Minimal Property Registry (for tests)

```python
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.ontology.datatypes import property_shape

# Create minimal registry for specific entity
properties = {
    "P31": property_shape("P31", "wikibase-item"),
    "P17": property_shape("P17", "wikibase-item"),
    # ... add more properties as needed
}
registry = PropertyRegistry(properties=properties)

converter = EntityConverter(property_registry=registry)
```

---

## Testing Strategy

### Test Pyramid

The testing approach follows a pyramid structure with three levels:

```
        Integration Tests (Phase 3)
              ↑↑↑
      Writer/Component Tests (Phase 2)
              ↑↑↑
         Unit Tests (Phase 1)
```

### Phase 1: Unit Tests (Lowest Level) ✅ COMPLETE

**Purpose:** Test individual components in isolation

**Test Files:**
- `test_value_node.py` - Value node URI generation and serialization (7 tests)
- `test_normalization.py` - RDF normalization utilities

**Coverage:**
- `ValueNode.generate_value_node_uri()` - MD5-based URI generation
- `ValueNode._serialize_value()` - Value serialization for hashing
- URI consistency for identical values
- URI differentiation for different properties

### Phase 2: Writer Tests (Mid Level) ✅ COMPLETE

**Purpose:** Test RDF writing components with small inputs

**Test Files:**
- `test_value_node_writer.py` - Structured value node writing (5 tests)
- `test_triple_writer_value_nodes.py` - Value node detection (4 tests)
- `test_property_ontology.py` - Property metadata and predicates (9 tests)
- `test_property.py` - Basic property writing
- `test_property_registry.py` - Property registry loading (8 tests)
- `test_referenced_entities.py` - Referenced entity collection (4 tests)

**Coverage:**
- `ValueNodeWriter.write_time_value_node()` - Time value nodes with all fields
- `ValueNodeWriter.write_quantity_value_node()` - Quantity nodes with bounds
- `ValueNodeWriter.write_globe_value_node()` - Globe coordinate nodes
- `TripleWriters.write_statement()` - Full statement writing
- `TripleWriters.write_direct_claim()` - Direct claim generation
- `PropertyOntologyWriter.write_property_metadata()` - Property metadata blocks
- `PropertyOntologyWriter.write_property()` - Predicate declarations
- `PropertyOntologyWriter.write_novalue_class()` - No-value constraints
- `PropertyRegistry.shape()` - Property shape lookup
- `EntityConverter._collect_referenced_entities()` - Referenced entity collection
- `EntityConverter._write_referenced_entity_metadata()` - Referenced entity metadata

### Phase 3: Integration Tests (Higher Level) 🔄 IN PROGRESS

**Purpose:** Test complete conversion of entities to RDF

**Test Files:**
- `test_q42_conversion.py` - Large entity integration test
- `test_q120248304_conversion.py` - Medium entity with globe coordinates
- `test_ttl_comparison.py` - TTL comparison utilities
- `test_split_blocks.py` - Turtle block splitting

**Coverage:**
- EntityConverter.convert_to_string() - Full entity conversion
- Statement URI generation (wds: prefix with UUID)
- Reference URI generation (wdref: prefix with hash)
- Direct claim generation for best-rank statements
- Value node generation for time, quantity, globe coordinates
- Qualifier and reference value nodes

**Planned Test Suites:**

**Suite 3.1: Basic Entity Features**
- Labels (single and multiple languages)
- Descriptions (single and multiple languages)
- Aliases (multiple per language)
- Sitelinks
- Entity type declaration

**Suite 3.2: Statement Features**
- Entity value statements
- String value statements
- Time value statements
- Quantity value statements
- Globe coordinate statements
- Monolingualtext statements
- External-id statements
- Statement ranks (normal, preferred, deprecated)
- Statement qualifiers (with value nodes)
- Statement references (with value nodes)

**Suite 3.3: Property Metadata**
- Property entity metadata blocks
- Property predicate declarations (p, ps, pq, pr, wdt, psv, pqv, prv)
- No-value constraints with blank nodes
- Multi-language labels and descriptions

**Suite 3.4: Value Nodes**
- Time value nodes (all fields)
- Quantity value nodes (with bounds)
- Globe coordinate value nodes
- Qualifier value nodes
- Reference value nodes

### Phase 4: Roundtrip Tests 🔴 NEEDED

**Purpose:** Compare generated TTL with golden files from Wikidata

**Test Files:**
- **Planned:** `test_roundtrip_q17948861.py` - Small entity roundtrip
- **Planned:** `test_roundtrip_q42.py` - Large entity roundtrip
- **Planned:** `test_roundtrip_q120248304.py` - Medium entity roundtrip

**Coverage:**
- Parse entity JSON
- Generate TTL
- Split TTL into subject blocks
- Compare block-by-block with golden TTL
- Verify all RDF blocks present and correct

**Known Failure:**
- `test_q17948861_full_roundtrip` - Missing 10 of 13 RDF blocks
  - Missing: Referenced entity metadata, property predicate declarations, no-value constraints
  - Root cause: Implementation complete but not fully integrated

---

## Implementation Status

### Recent Changes (Property Metadata Support):

**Structural Changes (COMPLETED):**
- ✓ PropertyShape model - Added `labels` and `descriptions` fields
- ✓ Loader - Merges labels/descriptions from JSON with datatype from CSV
- ✓ property_shape factory - Accepts optional labels/descriptions parameters
- ✓ Tests - Added comprehensive tests in `tests/rdf/test_property_registry.py`

**Property Ontology Writer Tests (tests/rdf/test_property_ontology.py):**
- ✓ `write_property_metadata()` - Generates full property metadata blocks
- ✓ `write_property()` - Generates predicate declarations
- ✓ `write_novalue_class()` - Generates no-value constraints
- ✓ Multi-language support for labels/descriptions
- ✓ Correct handling of time datatypes with value nodes

**Direct Claims Implementation (COMPLETED):**
- ✓ `write_direct_claim()` method - Generates `wdt:Pxxx` triples
- ✓ Integration with `write_statement()` - Only generates for best-rank (truthy) statements
- ✓ Tests - Added `tests/rdf/test_direct_claims.py` with 4 test cases

**Referenced Entity Implementation (COMPLETED):**
- ✓ `_collect_referenced_entities()` - Collects unique entity IDs from statement values
- ✓ `_load_referenced_entity()` - Loads entity metadata from JSON cache
- ✓ `_write_referenced_entity_metadata()` - Writes wd:Qxxx metadata blocks
- ✓ Tests - Added `tests/rdf/test_referenced_entities.py` with 4 test cases

### Feature Implementation Status

**Entity Features (FULLY IMPLEMENTED):**
- ✓ Labels: `rdfs:label` triples (multi-language)
- ✓ Descriptions: `schema:description` triples (multi-language)
- ✓ Aliases: `skos:altLabel` triples (multiple per language)
- ✓ Sitelinks: `schema:sameAs` triples
- ✓ Entity type: `a wikibase:Item`

**Statement Features (FULLY IMPLEMENTED):**
- ✓ Statement blocks: `p:Pxxx` → statement node
- ✓ Statement values: `ps:Pxxx` → value
- ✓ Statement ranks: NormalRank, PreferredRank, DeprecatedRank
- ✓ Qualifiers: `pq:Pxxx` → value (with value nodes for complex types)
- ✓ References: `pr:Pxxx` → value (with value nodes for complex types)
- ✓ Direct claims: `wdt:Pxxx` → value (for best-rank statements)

**Referenced Entity Metadata (FULLY IMPLEMENTED):**
- ✓ Collection: Extract entity IDs from statement values
- ✓ Loading: Load entity JSON from cache directory
- ✓ Metadata: Write wd:Qxxx blocks with labels, descriptions

**Property Metadata (FULLY IMPLEMENTED):**
- ✓ Property entity blocks: wd:Pxxx with labels, descriptions
- ✓ Predicate declarations: owl:ObjectProperty for p, ps, pq, pr, wdt
- ✓ Value predicates: psv, pqv, prv for time/quantity/globe
- ✓ No-value constraints: wdno:Pxxx with blank node restrictions

**Value Nodes (FULLY IMPLEMENTED):**
- ✓ Time value nodes: wikibase:TimeValue with timeValue, timePrecision, timeTimezone, timeCalendarModel
- ✓ Quantity value nodes: wikibase:QuantityValue with quantityAmount, quantityUnit, quantityUpperBound, quantityLowerBound
- ✓ Globe coordinate nodes: wikibase:GlobecoordinateValue with geoLatitude, geoLongitude, geoPrecision, geoGlobe
- ✓ Value node linking: psv:Pxxx, pqv:Pxxx, prv:Pxxx → wdv:xxx
- ✓ URI generation: MD5-based hash for consistent IDs

**Dataset Features (FULLY IMPLEMENTED):**
- ✓ Software version: `schema:softwareVersion "1.0.0"`
- ✓ Entity version: `schema:version`^^xsd:integer
- ✓ Modification date: `schema:dateModified`^^xsd:dateTime
- ✓ Entity counts: `wikibase:statements`, `wikibase:sitelinks`, `wikibase:identifiers`
- ✓ License: `cc:license`
- ✓ Dataset type: `a schema:Dataset`

**Output Features (FULLY IMPLEMENTED):**
- ✓ Turtle prefixes: 30 `@prefix` declarations

---

## Known Issues

### Roundtrip Test Failure

**Test:** `test_q17948861_full_roundtrip` (not yet implemented in test suite)

**Issue:** Generated TTL missing some RDF blocks compared to golden file

**Expected blocks (13):**
- data:Q17948861, wd:Q17948861, wds:Q17948861-*
- wd:Q17633526 (referenced entity)
- wd:P31 (property entity)
- p:P31, ps:P31, psv:P31, pq:P31, pqv:P31, pr:P31, prv:P31, wdt:P31, wdno:P31

**Actual blocks (3):**
- data:Q17948861, wd:Q17948861, wds:Q17948861-*

**Root Cause:** Property metadata and referenced entity metadata not being written by default in EntityConverter

**Resolution:** Enable metadata writing by providing entity_cache_path parameter to EntityConverter

---

## Next Steps

### COMPLETED: Core Features
All major RDF generation features implemented:

- Entity type declaration
- Labels, descriptions, aliases
- Statements with all value types
- Statement ranks (normal, preferred, deprecated)
- Qualifiers with value nodes
- References with value nodes
- Sitelinks
- Dataset metadata
- Property ontology (metadata, predicates, no-value constraints)
- Direct claims for best-rank
- Structured value nodes (time, quantity, globe) with bounds
- Qualifier value nodes
- Reference value nodes
- Referenced entity metadata blocks

### IN PROGRESS: Integration Testing
- Create comprehensive test suites for each feature category
- Fix roundtrip test failures
- Validate all RDF block generation

### PLANNED: Truthy Mode
Mode for generating only best-rank statements (truthy statements):

```turtle
# Only include wdt:Pxxx direct claims for best-rank statements
wd:Q42 wdt:P31 wd:Q5 .
wd:Q42 wdt:P569 "+1952-03-11T00:00:00Z"^^xsd:dateTime .

# Skip deprecated and non-best-rank statements
```

---

## Running Tests

### Run All RDF Tests
```bash
cd /home/dpriskorn/src/python/wikibase-backend
source .venv/bin/activate
pytest tests/rdf/ -v
```

### Run Specific Test Suites
```bash
# Unit tests (Phase 1)
pytest tests/rdf/test_value_node.py -v
pytest tests/rdf/test_normalization.py -v

# Writer tests (Phase 2)
pytest tests/rdf/test_value_node_writer.py -v
pytest tests/rdf/test_triple_writer_value_nodes.py -v
pytest tests/rdf/test_property_ontology.py -v
pytest tests/rdf/test_property_registry.py -v
pytest tests/rdf/test_referenced_entities.py -v

# Integration tests (Phase 3)
pytest tests/rdf/test_q42_conversion.py -v
pytest tests/rdf/test_q120248304_conversion.py -v
pytest tests/rdf/test_ttl_comparison.py -v
pytest tests/rdf/test_split_blocks.py -v
```

### Run Tests with Coverage
```bash
pytest tests/rdf/ --cov=models/rdf_builder --cov-report=html
```

### Run Tests with Detailed Output
```bash
pytest tests/rdf/ -vv -s
```

### Run Specific Test
```bash
pytest tests/rdf/test_value_node.py::test_serialize_time_value -v
```

### Run Tests for Failing Test
```bash
pytest tests/rdf/test_ttl_comparison.py -k roundtrip -v
```

---

## Test Data

### Entity JSON Files
Located in `test_data/json/entities/`:
- Q1.json - Simple entity
- Q2.json - Earth (medium)
- Q3.json, Q4.json, Q5.json - Basic entities
- Q10.json - Small entity
- Q42.json - Douglas Adams (large, 332 statements, 293 properties)
- Q120248304.json - Medium entity with globe coordinates
- Q17633526.json - Wikinews article (referenced entity)
- Q17948861.json - Small entity (for roundtrip testing)
- Q182397.json - Medium entity
- Q51605722.json - Medium entity
- Q53713.json - Large entity
- Q8413.json - Medium entity

### Golden TTL Files
Located in `test_data/rdf/ttl/`:
- Q1.ttl, Q2.ttl, Q3.ttl, Q4.ttl, Q5.ttl - Basic entities
- Q42.ttl - Large entity with all features
- Q120248304.ttl - Medium entity with globe coordinates
- Q17633526.ttl - Referenced entity
- Q17948861.ttl - Small entity for roundtrip testing
- Q182397.ttl, Q51605722.ttl, Q53713.ttl, Q8413.ttl - Medium/large entities

### Property Data
Located in `test_data/properties/`:
- properties.csv - Property metadata cache (downloaded from Wikidata)
- README.md - Property data documentation

### Scripts
- `scripts/download_properties.sh` - Download property metadata from Wikidata
- `scripts/download_properties_sparql.py` - Alternative download method using SPARQL
- `scripts/download_property_metadata.py` - Download property labels/descriptions
- `scripts/download_wikidata_entity.py` - Download entity JSON from Wikidata API
- `scripts/download_missing_entities.py` - Download missing entity JSON files

---

