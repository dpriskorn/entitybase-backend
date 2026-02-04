#!/usr/bin/env python3
"""
Generate PlantUML diagram for complete data flow from entity creation to RDF change event.
Shows only internal components of the Wikibase Backend codebase.
"""

from pathlib import Path


def generate_plantuml() -> str:
    """Generate PlantUML diagram as string."""
    return """@startuml detailed_data_flow

title Complete Data Flow: Entity Creation → RDF Change Event
note right
  Generated from Wikibase Backend codebase
  Shows only internal components
end note

' Entry Points
package "REST API Layer" #LightBlue {
    component [Entity Endpoints\\n/entities/{id}] as API
    note right of API: POST, PATCH, DELETE\\nsrc/models/rest_api/entitybase/v1/endpoints/entities.py
}

' Processing
package "Entity Processing" #LightGreen {
    component [Request Validation\\n_validate_revision_request] as VALIDATE
    component [Idempotency Check\\n_check_idempotency_new] as IDEMPOTENT
    component [Entity Processing\\n_process_entity_data_new] as PROCESS
    component [Hashing & Dedup\\nEntityHashingService] as HASH
}

' Storage
package "Storage Layer" #LightYellow {
    database "Vitess Repository\\n(Revision Metadata)" as DB
    note right of DB: src/models/infrastructure/vitess/repositories/revision.py

    storage "S3 Client\\n(Full Snapshots)" as S3
    note right of S3: src/models/infrastructure/s3/client.py
}

' Event Publishing Step 1
queue "Kafka/Redpanda\\nentitybase.entity_change" as KAFKA1
note right of KAFKA1: EntityChangeEvent\\nsrc/models/infrastructure/stream/event.py

' Entity Diff Worker
package "Entity Diff Worker" #Lavender {
    component [Entity Diff Worker] as WORKER
    note right of WORKER: src/models/workers/entity_diff/entity_diff_worker.py

    component [RDF Serializer] as RDF_CONV
    note right of RDF_CONV: entity_data_to_rdf()

    component [RDF Canonicalizer\\nURDNA2015] as CANONICAL
    note right of CANONICAL: src/models/workers/entity_diff/rdf_cannonicalizer.py

    component [Diff Computation\\nAdded/Removed Triples] as DIFF
}

' Event Publishing Step 2
queue "Kafka/Redpanda\\nwikibase.entity_diff" as KAFKA2
note right of KAFKA2: RDFChangeEvent\\nadded_triples, removed_triples

' Internal Consumer
package "Internal Consumers" #Coral {
    component [Watchlist Consumer] as WATCHLIST
    note right of WATCHLIST: src/models/workers/watchlist_consumer/main.py
}

' Data Flow Connections
API --> VALIDATE : 1. HTTP Request
VALIDATE --> IDEMPOTENT : 2. Validated
IDEMPOTENT --> PROCESS : 3. Unique request
PROCESS --> HASH : 4. Processed data
HASH --> DB : 5a. Revision metadata
HASH --> S3 : 5b. Full snapshot

DB --> KAFKA1 : 6a. Trigger
S3 --> KAFKA1 : 6b. Trigger

KAFKA1 --> WORKER : 7. EntityChangeEvent
WORKER --> RDF_CONV : 8. JSON → Turtle
RDF_CONV --> CANONICAL : 9. Canonicalize
CANONICAL --> DIFF : 10. Normalized triples
DIFF --> KAFKA2 : 11. RDFChangeEvent

KAFKA1 --> WATCHLIST : 12. EntityChangeEvent

note bottom of KAFKA2
  External consumers (not in this codebase):
  • QLever
  • Search indexers
  • Analytics pipelines
  • Mirror services
end note

@enduml
"""


def main():
    """Main entry point."""
    output_dir = Path(__file__).parent.parent.parent / "doc" / "DIAGRAMS"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "detailed_data_flow.puml"
    
    plantuml_content = generate_plantuml()
    
    output_file.write_text(plantuml_content, encoding="utf-8")
    
    print(f"Generated PlantUML diagram: {output_file}")
    print(f"To render, use: plantuml {output_file}")


if __name__ == "__main__":
    main()
