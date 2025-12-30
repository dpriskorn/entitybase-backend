# Properties Cache

This directory contains property definitions downloaded from Wikidata.

## Format

Properties are stored in `properties.csv` with format:

```csv
property_id,datatype
P31,wikibase-item
P21,wikibase-item
P800,external-id
```

## Downloading Properties

Run the download script to fetch property definitions:

```bash
python scripts/download_properties.py
```

## Regenerating Cache

Delete `properties.csv` and re-run the download script.

## Usage in Tests

Tests use the `full_property_registry` fixture which loads properties from this cache.
