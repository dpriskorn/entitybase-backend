# Lock/Unlock Process

## Entity Lock Process

Locking an entity is performed through the standard ENTITY UPDATE PROCESS by setting is_locked=True in the update request. The process follows the same steps as entity update, with additional validation and state changes:

```
[EntityUpdateHandler - update.py]
+--> Standard Update Validation (existence, protection, etc.)
+--> Check Lock Status: Ensure entity is not already locked (unless overriding)
+--> Set Lock State: request.is_locked = True
+--> Proceed with ENTITY UPDATE PROCESS
+--> Update Revision Data: Include "is_locked": True
+--> Update Entity Head: vitess.update_entity_head(entity_id, is_locked=True)
+--> Publish Event: ChangeType.LOCK_ADDED
+--> Return Success
```

## Entity Unlock Process

Unlocking an entity is performed through the standard ENTITY UPDATE PROCESS by setting is_locked=False in the update request:

```
[EntityUpdateHandler - update.py]
+--> Standard Update Validation (existence, protection, etc.)
+--> Check Lock Status: Ensure entity is currently locked
+--> Set Unlock State: request.is_locked = False
+--> Proceed with ENTITY UPDATE PROCESS
+--> Update Revision Data: Include "is_locked": False
+--> Update Entity Head: vitess.update_entity_head(entity_id, is_locked=False)
+--> Publish Event: ChangeType.LOCK_REMOVED
+--> Return Success
```

Note: Locking/unlocking uses the same underlying ENTITY UPDATE PROCESS infrastructure, with the is_locked flag controlling edit permissions.