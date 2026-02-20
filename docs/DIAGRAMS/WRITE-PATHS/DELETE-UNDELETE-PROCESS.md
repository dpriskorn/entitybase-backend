# Delete/Undelete Process

## Entity Delete Process

```
[EntityDeleteHandler - delete.py]
+--> Validate Clients: vitess and s3 initialized
+--> Check Entity Exists: vitess.entity_exists(entity_id) == True
+--> Check Not Already Deleted: vitess.is_entity_deleted(entity_id) == False
+--> Get Head Revision: head_revision_id = vitess.get_head(entity_id)
+--> Check Protection: not archived or locked
+--> Calculate New Revision: new_revision_id = head_revision_id + 1
+--> Read Current Revision: current_revision = s3.read_revision(entity_id, head_revision_id)
+--> Prepare Delete Revision Data: copy entity data, set is_deleted=True, edit_type="soft_delete" or "hard_delete"
+--> For Hard Delete: Decrement ref_count for all statements
+--> Write Delete Revision: s3.write_revision(entity_id, new_revision_id, revision_data)
+--> Update Head Pointer: vitess.create_revision(entity_id, new_revision_id, revision_data, head_revision_id)
+--> Publish Event: stream_producer.publish_change(EntityChangeEvent with SOFT_DELETE or HARD_DELETE)
+--> Return EntityDeleteResponse
```

## Entity Undelete Process

Undelete is not implemented as a separate operation in the current codebase. Soft-deleted entities can be "undeleted" by performing an update operation that sets is_deleted=False in the revision data, effectively restoring the entity to an active state. This would follow the standard ENTITY UPDATE PROCESS.