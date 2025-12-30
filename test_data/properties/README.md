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

### Step 1: Download Property Datatypes

Run the download script to fetch property definitions:

```bash
./scripts/download_properties.sh
```

This creates `properties.csv` with format:
```csv
property_id,datatype
P31,wikibase-item
P21,wikibase-item
P800,external-id
```

### Step 2: Download Property Metadata

Run the metadata downloader to fetch labels and descriptions:

```bash
./scripts/download_property_metadata.py
```

This creates individual JSON files for each property:
```
properties/
    P31.json
    P17.json
    P625.json
    ...
```

Each JSON file contains:
```json
{
  "id": "P31",
  "labels": {
    "en": {
      "language": "en",
      "value": "instance of"
    }
  },
  "descriptions": {
    "en": {
      "language": "en",
      "value": "type to which this subject corresponds..."
    }
  }
}
```

## Regenerating Cache

Delete `properties.csv` and re-run the download script.

## Usage in Tests

Tests use the `full_property_registry` fixture which loads properties from this cache.
