# Plan: Build RDF Generation from Internal Representation

## Overview

The parser is **COMPLETE** — it can read all Q42 data into internal models correctly.  
We now need to implement RDF generation from these internal models following **Wikibase RDF mapping rules**.

**Parser Status:** ✓ COMPLETE

### Verified capabilities

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

---

## RDF Generation: NOT IMPLEMENTED

- **Current state:** No RDF generation code exists
- **Target:** Generate Turtle format RDF from internal `Entity` model

---

## Architecture Overview

Based on `doc/ARCHITECTURE/JSON-RDF-CONVERTER.md`:

Entity (internal model)
↓
RDF Generator
↓
Triples (Turtle format)


---

## Implementation Plan

---

## Phase 1: Core RDF Structure

### 1.1 Create RDF Service Directory Structure

src/services/shared/rdf_generator/
├── init.py
├── converter.py # Main conversion logic
├── triple_writers.py # Triple writing utilities
├── uri_generator.py # URI generation for entities, statements, references
├── value_formatters.py # Format values as RDF literals/URIs
└── turtle_writer.py # Buffered Turtle output writer


---

### 1.2 Implement Core Models and Constants

**File:** `src/services/shared/rdf_generator/__init__.py`

```python
from .converter import EntityToRdfConverter

__all__ = ["EntityToRdfConverter"]

class URIGenerator:
    """Generate URIs for entities, statements, references"""
    
    BASE_URI = "http://acme.test"  # From test data
    DATA_URI = "http://data.acme.test"
    
    @staticmethod
    def entity_uri(entity_id: str) -> str:
        return f"{URIGenerator.BASE_URI}/{entity_id}"
    
    @staticmethod
    def data_uri(entity_id: str) -> str:
        return f"{URIGenerator.DATA_URI}/{entity_id}"
    
    @staticmethod
    def statement_uri(statement_id: str) -> str:
        return f"{URIGenerator.BASE_URI}/statement/{statement_id}"
    
    @staticmethod
    def reference_uri(statement_uri: str, ref_index: int) -> str:
        return f"{statement_uri}-{ref_index:09d}#ref"
