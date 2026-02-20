# Lexeme Update Process

```
[EntityUpdateHandler - update_lexeme()]
+--> Validate Lexeme ID: re.match(r"^L\d+$", entity_id) -> Fail if invalid (400)
+--> Check Entity Exists: vitess_client.entity_exists(entity_id) -> Fail if False (404)
+--> Check Deletion Status: vitess_client.is_entity_deleted(entity_id) -> Fail if True (410)
+--> Check Lock Status: vitess_client.is_entity_locked(entity_id) -> Fail if True (423)
+--> Create Transaction: tx = UpdateTransaction()
+--> Try:
|    +--> Get Head: head_revision_id = vitess_client.get_head(entity_id)
|    +--> Prepare Data: request_data["id"] = entity_id
|    +--> Process Lexeme Terms: tx.process_lexeme_terms(forms, senses)
|    |    +--> Extract Forms: request.data.get("forms", [])
|    |    +--> Extract Senses: request.data.get("senses", [])
|    |    +--> Hash Form Representations:
|    |    |    +--> For each form.representations[lang].value:
|    |    |    |    +--> Compute hash: MetadataExtractor.hash_string(text)
|    |    |    |    +--> Store to S3: s3_client.store_form_representation(text, hash_val)
|    |    |    |    +--> Register rollback: tx.lexeme_term_operations.append(lambda: rollback_form(hash))
|    |    +--> Hash Sense Glosses:
|    |    |    +--> For each sense.glosses[lang].value:
|    |    |    |    +--> Compute hash: MetadataExtractor.hash_string(text)
|    |    |    |    +--> Store to S3: s3_client.store_sense_gloss(text, hash_val)
|    |    |    |    +--> Register rollback: tx.lexeme_term_operations.append(lambda: rollback_gloss(hash))
|    |    +--> Update request_data with hashes: request_data["forms"] = forms, request_data["senses"] = senses
|    +--> Process Statements: tx.process_statements(entity_id, request_data, vitess_client, s3_client)
|    |    +--> Extract Properties: StatementExtractor.extract_properties_from_claims(claims)
|    |    +--> Compute Property Counts: StatementExtractor.compute_property_counts_from_claims(claims)
|    |    +--> Hash Statements: StatementHasher.compute_hash(statement) for each statement
|    |    +--> Deduplicate and Store: deduplicate_and_store_statements(hash_result, vitess_client, s3_client)
|    +--> Create Revision: tx.create_revision(entity_id, new_revision_id=head+1, ..., is_creation=False) [CAS protected]
|    +--> Publish Event: tx.publish_event(entity_id, stream_producer)
|    +--> Commit: tx.commit()
+--> Except (Any Failure):
|    +--> Rollback: tx.rollback()
|    |    +--> Rollback Lexeme Terms (reversed order): for op in reversed(tx.lexeme_term_operations): op()
|    |    |    +--> Delete form representations: s3_client._delete_metadata(FORM_REPRESENTATIONS, hash)
|    |    |    +--> Delete sense glosses: s3_client._delete_metadata(SENSE_GLOSSES, hash)
|    |    +--> Rollback Statements (reversed order): for op in reversed(tx.operations): op()
|    |    |    +--> Decrement ref_count: vitess_client.decrement_ref_count(hash)
|    |    |    +--> Delete from S3 if orphaned: s3_client.delete_statement(hash) when ref_count == 0
|    |    +--> Rollback Revision: vitess_client.delete_revision(entity_id, revision_id)
|    +--> Raise HTTP 500
+--> Return: EntityResponse
```
