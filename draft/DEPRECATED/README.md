# Deprecated Documentation

This directory contains documentation that has been superseded by newer, auto-generated documentation.

## DATA-FLOW.puml

**Deprecated**: 2026-01-XX
**Replaced by**:
- `doc/DIAGRAMS/system_architecture.puml` - Current system architecture diagram
- `doc/DIAGRAMS/data_flow.puml` - Current data flow diagram
- `doc/DIAGRAMS/component_relationships.puml` - Component relationships diagram

**Reason for Deprecation**:
The original `DATA-FLOW.puml` diagram was created early in the project and doesn't reflect the current architecture that includes:
- Background workers (ID generation, backlink statistics)
- Service layer architecture
- Updated component relationships
- Current data flow patterns

**Historical Context**:
This diagram represented the original architectural vision with MediaWiki integration patterns, RDF generation services, and change detection workflows that have since evolved into the current worker-based architecture.

**Migration**:
Use the auto-generated PlantUML diagrams in `doc/DIAGRAMS/` which are kept current through the `scripts/generate_architecture_diagrams.py` script and updated via `update-docs.sh`.

---

*This file is preserved for historical reference. For current architecture documentation, see the main `doc/ARCHITECTURE/` directory.*