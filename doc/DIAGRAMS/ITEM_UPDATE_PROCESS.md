# ITEM UPDATE PROCESS

[EntityUpdateHandler - update.py]
+--> Check Entity Exists: vitess_client.entity_exists(entity_id) -> Fail if False (404)
+--> Check Deletion Status: vitess_client.is_entity_deleted(entity_id) -> Fail if True (410)
+--> Check Lock Status: vitess_client.is_entity_locked(entity_id) -> Fail if True (423)
+--> Validate JSON: Pydantic on EntityUpdateRequest
+--> Create Transaction: tx = UpdateTransaction()
+--> Try:
|    +--> Get Head: head_revision_id = vitess_client.get_head(entity_id)
|    +--> Prepare Data: request_data["id"] = entity_id
|    +--> Process Statements: tx.process_statements(entity_id, request_data, vitess_client, s3_client)
|    +--> Create Revision: tx.create_revision(entity_id, new_revision_id=head+1, ..., is_creation=False) [CAS protected]
|    +--> Publish Event: tx.publish_event(entity_id, stream_producer)
|    +--> Commit: tx.commit()
+--> Except (Any Failure):
|    +--> Rollback: tx.rollback()  // Undo statements, revision
|    +--> Raise HTTP 500
+--> Return: EntityResponse