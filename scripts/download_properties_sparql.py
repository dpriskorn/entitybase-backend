#!/usr/bin/env python3
"""
Download all Wikidata property datatypes via SPARQL and save to CSV.

Usage:
    python scripts/download_properties_sparql.py
"""

import requests
import csv
from pathlib import Path

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"


def fetch_all_properties():
    """Fetch all properties from Wikidata SPARQL"""
    
    query = """
    SELECT ?property ?datatype WHERE {
      ?property a wikibase:Property .
      ?property wikibase:propertyType ?datatype .
    }
    """
    
    print("Fetching properties from SPARQL endpoint...")
    
    response = requests.get(
        SPARQL_ENDPOINT,
        params={"query": query, "format": "json"},
        timeout=30
    )
    response.raise_for_status()
    
    data = response.json()
    return data["results"]["bindings"]


def extract_property_id(uri: str) -> str:
    """Extract property ID from full URI"""
    # http://www.wikidata.org/entity/P31 -> P31
    return uri.rsplit("/", 1)[-1]


def save_to_csv(properties, output_path: Path):
    """Save properties to CSV"""
    print(f"Saving {len(properties)} properties to {output_path}...")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["property_id", "datatype"])
        
        for prop in properties:
            prop_id = extract_property_id(prop["property"]["value"])
            datatype_uri = prop["datatype"]["value"]
            
            # Extract datatype from URI
            # http://wikiba.se/ontology#WikibaseItem -> wikibase-item
            datatype = datatype_uri.rsplit("#", 1)[-1]
            # Normalize: WikibaseItem -> wikibase-item
            datatype = datatype.replace("Wikibase", "wikibase").lower()
            
            writer.writerow([prop_id, datatype])
    
    print(f"✅ Saved to {output_path}")


def main():
    """Main function"""
    
    # Fetch all properties from SPARQL
    all_properties = fetch_all_properties()
    
    # Save all properties to CSV
    output_dir = Path(__file__).parent.parent / "test_data" / "properties"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "properties.csv"
    save_to_csv(all_properties, output_path)
    
    print("\n✅ Done!")
    print(f"   Properties: {len(all_properties)}")
    print(f"   Output: {output_path}")


if __name__ == "__main__":
    main()
