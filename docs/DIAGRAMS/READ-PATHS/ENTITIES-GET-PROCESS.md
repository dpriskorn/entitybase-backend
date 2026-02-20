# Entity Get Process

```
[EntityReadHandler.get_entity - read.py]
+--> Validate Clients: Check vitess_client and s3_client are initialized (503 if not)
+--> Validate Entity: Check entity_exists(entity_id) in Vitess (404 if not)
+--> Get Head Revision: head_revision_id = vitess_client.get_head(entity_id) (404 if 0)
+--> Read Revision: revision = s3_client.read_revision(entity_id, head_revision_id)
+--> Check Deleted: If state.is_deleted is True, return 404
+--> Build Response: EntityResponse with id, rev_id, data, and state flags
+--> Return: EntityResponse
```

## Error Handling
- Vitess/S3 not initialized → 503 Service Unavailable
- Entity not found in Vitess → 404 Not Found
- Head revision 0 → 404 Not Found
- Entity marked as deleted → 404 Not Found
- S3 revision not found (S3NotFoundError) → 404 Not Found
- S3 read failure (other exception) → 500 Internal Server Error