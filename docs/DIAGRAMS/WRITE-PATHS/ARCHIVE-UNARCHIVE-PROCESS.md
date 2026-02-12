# ENTITY ARCHIVE PROCESS

Archiving an entity is performed through the standard ENTITY UPDATE PROCESS by setting is_archived=True in the update request. This blocks all future edits to the entity:

[EntityUpdateHandler - update.py]
+--> Standard Update Validation (existence, etc.)
+--> Check Archive Status: Ensure entity is not already archived
+--> Set Archive State: request.is_archived = True
+--> Proceed with ENTITY UPDATE PROCESS
+--> Update Revision Data: Include "is_archived": True
+--> Update Entity Head: vitess.update_entity_head(entity_id, is_archived=True)
+--> Publish Event: Appropriate change event
+--> Return Success

# ENTITY UNARCHIVE PROCESS

Unarchiving an entity is performed through the standard ENTITY UPDATE PROCESS by setting is_archived=False in the update request. This allows edits again:

[EntityUpdateHandler - update.py]
+--> Standard Update Validation (existence, etc.)
+--> Check Archive Status: Ensure entity is currently archived
+--> Set Unarchive State: request.is_archived = False
+--> Proceed with ENTITY UPDATE PROCESS
+--> Update Revision Data: Include "is_archived": False
+--> Update Entity Head: vitess.update_entity_head(entity_id, is_archived=False)
+--> Publish Event: Appropriate change event
+--> Return Success

Note: Archiving/unarchiving uses the same underlying ENTITY UPDATE PROCESS infrastructure, with the is_archived flag controlling edit permissions. Archived entities cannot be edited until unarchived.