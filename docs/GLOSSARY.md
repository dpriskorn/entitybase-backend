# Glossary 📖

> Domain terms explained in plain English. No jargon without explanation!

---

## Core Concepts

### Entity 🏷️

An **entity** is a thing in the database — like an item (Q1), property (P1), or lexeme (L1). It's identified by a unique ID but has no intrinsic state on its own.

**Think of it like:** A library book card with a call number, but no actual book content on it yet.

**Examples:**
- Q1 = "Pizza" (item)
- P1 = "has ingredient" (property)  
- L1 = "cat" (lexeme)

---

### Revision 📦

A **revision** is a complete snapshot of an entity at a specific point in time. Once created, it can **never be changed** — it's immutable.

**Think of it like:** Git commits. Each commit is a frozen snapshot of your code.

**Why it matters:**
- Full audit trail (who changed what, when)
- Easy rollbacks (just point to an old revision)
- No data loss (old versions are never deleted)

---

### Head Pointer 🎯

The **head** is the "latest" revision of an entity — the one you get by default when you query it.

**Think of it like:** The `main` branch in Git — it's a pointer to the most recent commit.

---

## Entity Types

### Item (Q) 📚

An **item** represents a thing — a concept, object, person, place, etc. Items are the bread and butter of Wikibase.

**Examples:** 
- Q42 = "Douglas Adams"
- Q5 = "human"
- Q11573 = "pizza"

---

### Property (P) 🏗️

A **property** defines what kind of statement you can make. It's the "attribute name" in a key-value pair.

**Think of it like:** The column name in a spreadsheet.

**Examples:**
- P31 = "instance of" (what kind of thing is it?)
- P569 = "date of birth" (when was it born?)
- P279 = "subclass of" (what category does it belong to?)

Properties have **data types**:
- `item` — Points to another item
- `string` — Plain text
- `time` — Dates/times
- `quantity` — Numbers with units
- `monolingualtext` — Text in one language
- And more...

---

### Lexeme (L) 📖

A **lexeme** represents a word or phrase in a language — the lexical entry itself (not just the meaning).

**Think of it like:** A dictionary entry.

**Parts of a lexeme:**
- **Lemma** — The base form (e.g., "run")
- **Lexical category** — Noun, verb, adjective, etc.
- **Form** — Specific variations (e.g., "running", "ran")
- **Sense** — Meanings (e.g., "run fast" vs "run for office")

---

## Statement Parts

### Statement 📝

A **statement** is a piece of information about an entity — like "Pizza has ingredient cheese."

A statement consists of:
1. **Property** (P1 = "has ingredient")
2. **Value** (the thing it points to)
3. Optionally: references, qualifiers, rank

---

### Value 💎

A **value** is the content of a statement — what the property points to.

**Types:**
- **Item value** — Points to another entity (Q123)
- **String value** — Plain text ("hello")
- **Time value** — A date or timestamp
- **Quantity value** — A number with optional unit
- **Monolingual text** — Text + language ("pizza"@en)
- **Coordinate value** — Lat/long coordinates
- **Wikibase item** — Internal link to another Wikibase entity
- **URL** — Web address
- **Math formula** — Mathematical notation

---

### Reference 📚

A **reference** is where a statement's information came from — the source.

**Think of it like:** A citation in an academic paper.

**Example:**
```
Statement: "Earth is round"
  └── Reference: "NASA.gov, 2024"
```

---

### Qualifier ➕

A **qualifier** adds extra information to a statement, like when it applies or under what conditions.

**Example:**
```
Statement: "Population: 8.9 billion"
  └── Qualifier: "as of: 2024"
  └── Qualifier: "source: UN estimate"
```

---

### Rank 📊

A **rank** indicates the preferred value when multiple statements exist for the same property:

- **Preferred** — Best/current value
- **Normal** — Regular value
- **Deprecated** — Discouraged (still valid but not recommended)

---

### Snak 🔀

A **snak** is the atomic unit of statement data — the property-value pair. The term comes from Wikidata's history (it's "SNak" vs "RNak" — Statement NoAKnowledge / Reference NoAKnowledge).

**Think of it like:** A single cell in a spreadsheet — the intersection of a row (property) and column (value).

---

## Storage Concepts

### Statement Deduplication 🔁

Entitybase stores each unique statement only **once**, then references it by hash. This can reduce storage by 50%+ for typical datasets.

**Example:**
```
Q1 "pizza" --has ingredient--> Q2 "cheese"  (stored once! 🗃️)
Q3 "burger" --has ingredient--> Q2 "cheese" (reuses existing!)
```

---

### Immutable Snapshot 📸

An **immutable snapshot** is data that, once written, can never be changed or deleted. This is the core principle of Entitybase.

**Contrast with mutable data:**
```
Mutable (traditional DB):    Immutable (Entitybase):
┌─────────────┐              Rev 1: Q1 ──▶ S3
│    Q1       │              Rev 2: Q1 ──▶ S3  
│  (current)  │              Rev 3: Q1 ──▶ S3
└─────────────┘              (all preserved!)
  (overwrites!)
```

---

## API Terms

### Entity ID 🎫

The unique identifier for an entity:

- **Q-ids** — Items (Q1, Q2, Q3...)
- **P-ids** — Properties (P1, P2, P3...)
- **L-ids** — Lexemes (L1, L2, L3...)
- **E-ids** — Entity Schemas (E1, E2, E3...)

---

### Revision ID 🔢

A unique identifier for a specific revision, usually a timestamp-based number like `1700000000000001`.

---

### Edit Summary 📝

A short message describing what changed in an edit. Stored with the revision for auditability.

**Example:** `"Added ingredient statement"`, `"Fixed typo in description"`

---

## Protection Types

### Lock 🔒

Prevents all edits to an entity. Only admins can unlock.

---

### Semi-Protect ⚠️

Allows only established users to edit (configurable threshold).

---

### Archive 📁

Marks an entity as archived — hidden from normal views but restorable.

---

### Mass-Edit Protect 🚫

Prevents bulk edits through the API while allowing single edits.

---

## Other Terms

### Sitlink 🔗

A **sitelink** connects an entity to a page on another Wikimedia site.

**Example:**
```
Q123 (Wikidata item) --sitelink--> enwiki: "Pizza"
                          --sitelink--> itwiki: "Pizza"
                          --sitelink--> dewiki: "Pizza"
```

---

### Entity Schema (E) 📐

An **entity schema** defines a structure for entities — like a schema for structured data validation.

---

## See Also

- [Architecture](ARCHITECTURE/ARCHITECTURE.md) — How it all fits together
- [Tutorial](TUTORIAL.md) — Hands-on walkthrough
- [Quick Reference](QUICKREF.md) — Command reference
- [Features](features/ENDPOINTS.md) — All API endpoints
