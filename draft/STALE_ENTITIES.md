# Stale Knowledge

## Summary

This document defines the concept of "stale knowledge" in the Entitybase Backend system, specifying time thresholds after which entities are considered unmaintained.

---

## Definition

An entity is considered **stale** when it has not been edited for a defined period:

| Entity Type | ID Prefix | Stale Threshold |
|-------------|-----------|------------------|
| Item        | Q         | 1 month          |
| Lexeme      | L         | 6 months         |

### Items (Q)
Items are considered stale after **1 month** (30 days) without any edit. This shorter threshold reflects the higher activity rate and importance of items in the Wikidata ecosystem.

### Lexemes (L)
Lexemes are considered stale after **6 months** (180 days) without any edit. Lexemes typically require less frequent maintenance than items, hence the longer threshold.

---

## Use Cases

- **Weekly RDF Dump Filtering**: Exclude stale entities from weekly RDF dumps for consumers that require actively maintained knowledge
- **WikiProject Health Monitoring**: Identify dangling items that may need adoption by active WikiProjects
- **Archival Recommendations**: Flag stale entities for potential archival review by WikiProject maintainers

---

## Implementation

Staleness is determined by comparing the entity's last revision timestamp against the current time:

```python
from datetime import datetime, timedelta

ITEM_STALE_THRESHOLD = timedelta(days=30)
LEXEME_STALE_THRESHOLD = timedelta(days=180)

def is_stale(entity_type: str, last_edit_timestamp: datetime) -> bool:
    threshold = ITEM_STALE_THRESHOLD if entity_type == "item" else LEXEME_STALE_THRESHOLD
    return datetime.utcnow() - last_edit_timestamp > threshold
```

---

## Related Concepts

- **Archived Entity**: An entity that has been explicitly locked from edits. Archived entities are distinct from stale entities.
- **Dangling Item**: An item with no [maintained by (P6104)](https://www.wikidata.org/wiki/Property:P6104) statement. May be stale or actively maintained.
- **Healthy WikiProject**: A WikiProject that maintains its items within acceptable staleness thresholds.
