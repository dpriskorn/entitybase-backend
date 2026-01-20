# EntityChange Event Schema

This schema defines the structure for entity change events published to the event stream.

## Mock Example

```yaml
entity_id: "Q42"
revision_id: 12345
change_type: "edit"
from_revision_id: 12344
changed_at: "2023-01-01T12:00:00Z"
edit_summary: "Updated description"
```