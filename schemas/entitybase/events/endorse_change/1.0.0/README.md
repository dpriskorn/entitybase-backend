# EndorseChange Event Schema

This schema defines the structure for endorsement change events published to the event stream.

## Mock Example

```yaml
statement_hash: "hash123"
user_id: "user456"
action: "endorse"
timestamp: "2023-01-01T12:00:00Z"
```

Note: The `action` field uses enum values: "endorse" or "withdraw".