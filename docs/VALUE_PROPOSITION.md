# Entitybase: Billion-Scale Knowledge Base Backend

## 1. What is Entitybase?
Entitybase is a clean-room, billion-scale Wikibase-compatible backend designed to store and serve the "sum of all knowledge" at unprecedented scale. It provides a complete REST API and RDF export system that can handle 1 billion+ entities and 1 trillion+ statements - a scale where traditional Wikibase (MediaWiki-based) systems cannot operate.

**Core Capability**: Stores every bit of structured knowledge thrown at it, with full JSON/RDF schema compatibility with Wikidata.

---

## 2. How It Differs From Wikibase

| Aspect | Wikibase (MediaWiki) | Entitybase |
|--------|---------------------|------------|
| Architecture | Legacy PHP + MySQL with page-based mutable state | Clean-room Python + S3 + Vitess with immutable snapshots |
| Data Storage | No deduplication - each revision stores full JSON | Massive content deduplication (~90% storage savings) |
| API Compatibility | Wikibase REST API, MediaWiki APIs | Custom API - NOT drop-in compatible |
| Scalability | Struggles beyond 7M entities; exponential storage growth | Linear scaling to 2.84B+ entities over 10 years |
| Philosophy | Mutable revisions, MediaWiki-owned content | Immutable revisions (write once, never change) |
| MediaWiki Dependency | Tightly coupled to MediaWiki | MediaWiki-independent (MediaWiki becomes just a client) |

**Relationship**: Entitybase implements the exact same data model as Wikidata and outputs JSON/RDF in compatible formats, but is a complete architectural rewrite from scratch.

---

## 3. Key Technical Capabilities

### Storage Architecture:
- **Immutable S3 snapshots** - Every revision written once, never modified
- **Vitess indexing** - Lightweight metadata layer (no content storage)
- **Hash-based deduplication** - Statements, references, qualifiers, snaks, terms, sitelinks all deduplicated across revisions
- **93% storage cost reduction** ($2.28M → $152K over 10 years at 1B scale)

### API & Features:
- **89 REST endpoints** for complete CRUD operations
- Entity types: Items (Q), Properties (P), Lexemes (L), Entity Schemas (E)
- Statement management with hash-based storage
- Terms (labels, descriptions, aliases) and sitelinks
- Redirects, watchlists, thanks, endorsements
- Full revision history with immutable audit trail

### RDF Export:
- **Wikibase-compatible RDF generation** (Turtle, RDF XML, NTriples)
- MediaWiki-compatible value node deduplication
- Continuous RDF change streaming (Kafka-based)
- Weekly dump generation

### Performance & Scale:
- **777K+ entities/day** sustained creation rate
- Range-based ID allocation - no write hotspots
- Sub-second read performance via S3 + Vitess
- Horizontal scaling via microservices (API, workers, dump generation)

---

## 4. What Makes Entitybase Unique/Special

### 🏗️ Immutable Revision Architecture
The core innovation: "A revision is an immutable snapshot stored in S3. Once written, it never changes." This eliminates:
- Mutable state complexity
- Revision conflict handling
- Data corruption risks
- Audit trail issues

### 💰 Extreme Storage Efficiency
- ~90% storage reduction vs. Wikibase through aggressive deduplication
- Common content (e.g., "United States" label) stored once, not millions of times
- Reference citations shared across thousands of statements
- Compression (Gzip/zstd) for additional savings

### 📈 Linear Scalability
- O(1) write cost per edit - no write amplification
- No global tables - all operations entity-scoped
- No cascading writes - no fan-out on entity updates
- Designed for decades of growth without re-architecture

### 🔬 Knowledge-Base First Design
Unlike Wikibase (a MediaWiki extension), Entitybase is purpose-built for knowledge bases:
- S3 as system of record - perfect for CDN distribution
- Vitess for metadata only - lightweight indexing layer
- Event streaming - real-time change notifications
- RDF-first - semantic web native, not an afterthought

### 🌐 RDF Compatibility Without MediaWiki
- Complete Wikidata RDF mapping implemented from scratch
- MediaWiki-compatible hash deduplication for value nodes
- Same TTL output as Wikidata (verified against Q42 test data)
- Enables SPARQL integration (e.g., QLever, Blazegraph alternatives)

### 🔐 Data Integrity by Design
- Perfect revision history (immutability guarantees)
- Reference counting prevents orphaned content
- ACID transactions in Vitess
- Hash-based content addressing

---

## Positioning Summary

Entitybase is the world's only billion-scale, Wikidata-compatible knowledge base backend.

It solves the fundamental scaling problem of Wikidata: **how to store the sum of all knowledge when it grows to billions of entities and trillions of statements.** The current MediaWiki-based Wikibase cannot handle this scale due to exponential storage growth and write amplification.

### Target Users:
- Large knowledge base operators needing Wikidata-scale systems
- Organizations wanting Wikidata compatibility without MediaWiki
- Semantic web projects requiring SPARQL+RDF at scale
- Researchers managing massive structured datasets

### Value Proposition:
"Store infinite knowledge at linear cost with complete Wikidata compatibility."
