# Entity Create Process

```
[ItemCreateHandler - types.py]
+--> Validate JSON
+--> Create Transaction: tx = CreationTransaction()
+--> Try:
|    +--> Allocate ID: entity_id = enumeration_service.get_next_entity_id("item")
|    +--> Register Entity: tx.register_entity(vitess_client, entity_id)
|    +--> Prepare Data
|    +--> Process Statements: tx.process_statements(entity_id, request_data, vitess_client, s3_client)
    |    |    +--> Extract Properties: StatementExtractor.extract_properties_from_claims(claims)
    |    |    +--> Compute Property Counts: StatementExtractor.compute_property_counts_from_claims(claims)
    |    |    +--> Hash Statements: StatementHasher.compute_hash(statement) for each statement
    |    |    +--> Deduplicate and Store: deduplicate_and_store_statements(hash_result, vitess_client, s3_client)
|    +--> Create Revision: tx.create_revision(entity_id, revision_data, vitess_client, s3_client) [CAS protected]
|    +--> Publish Event: tx.publish_event(entity_id, stream_producer)
|    +--> Commit: tx.commit()  // Mark success, confirm ID usage
+--> Except (Any Failure):
|    +--> Rollback: tx.rollback()  // Undo all operations
|    +--> Raise HTTP 500
+--> Return: EntityResponse
```