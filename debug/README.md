# Documentation

- doc/WIKIDATA/RDF-DATA-MODEL.md
- mediawiki-extensions-Wikibase/repo/includes/Rdf/README.md
- mediawiki-extensions-Wikibase/repo/includes/Rdf/Values/README.md
- doc/ARCHITECTURE/RDF-BUILDER-IMPLEMENTATION.md
- doc/ARCHITECTURE/JSON-RDF-CONVERTER.md

# Test Entities (chosen to increase in size)

```
-rw-r--r-- 1 dpriskorn dpriskorn  23K Dec 28 22:37 Q120248304.json
-rw-r--r-- 1 dpriskorn dpriskorn  29K Dec 31 08:56 Q17633526.json
-rw-r--r-- 1 dpriskorn dpriskorn  50K Dec 30 15:17 Q51605722.json
-rw-r--r-- 1 dpriskorn dpriskorn 272K Dec 30 15:20 Q182397.json
-rw-r--r-- 1 dpriskorn dpriskorn 404K Dec 30 15:23 Q1.json
-rw-r--r-- 1 dpriskorn dpriskorn 427K Dec 30 15:21 Q8413.json
-rw-r--r-- 1 dpriskorn dpriskorn 525K Dec 30 15:22 Q53713.json
-rw-r--r-- 1 dpriskorn dpriskorn 662K Dec 28 22:34 Q42.json
```

## debug.py

Generic script for converting Wikidata entities from JSON to RDF Turtle format and comparing against golden files.

### Usage

```bash
source .venv/bin/activate
python debug/debug.py <entity_id>
```

### Arguments

- `entity_id`: Wikidata entity ID (e.g., Q42, Q17948861, Q120248304)

### What It Does

1. Loads entity JSON from `test_data/json/entities/{entity_id}.json`
2. Parses entity using JSON parser
3. Loads property registry from `test_data/properties/`
4. Converts entity to TTL RDF format
5. Compares generated TTL against golden file in `test_data/rdf/ttl/{entity_id}.ttl`
6. Outputs comparison results and full TTL file

### Output Files

Creates two files in `debug/` directory:

1. `debug_{entity_id}_comparison.txt` - Block-by-block comparison showing missing/extra blocks
2. `debug_{entity_id}_generated.ttl` - Full generated RDF Turtle output

### Examples

```bash
# Test Douglas Adams entity (large, 5280 blocks)
python debug/debug.py Q42

# Test small entity (15 blocks, perfect for quick testing)
python debug/debug.py Q17948861

# Test entity with globe coordinates and time values (167 blocks)
python debug/debug.py Q120248304
```

### Exit Codes

- `0` - Success (generated TTL matches golden file exactly)
- `1` - Mismatch (missing or extra blocks detected)

### Requirements

- Virtual environment must be activated: `source .venv/bin/activate`
- Entity JSON file must exist in `test_data/json/entities/`
- Golden TTL file must exist in `test_data/rdf/ttl/`
- Property metadata must be available in `test_data/properties/`

