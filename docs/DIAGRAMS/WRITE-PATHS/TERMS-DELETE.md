# TERM DELETE WRITE PATH

## Term DELETE Path (Removing Labels/Descriptions for Language)

[Entitybase DELETE /entities/{type}/{id}/labels/{lang} or /descriptions/{lang} - entitybase/v1/*.py]
+--> Receive DELETE Request for specific term type and language
+--> Validate Clients: vitess and s3 initialized
+--> Check Entity Exists: vitess.entity_exists(entity_id) == True
+--> Check Not Deleted: vitess.is_entity_deleted(entity_id) == False
+--> Check Permissions: not archived/locked/mass_edit_protected
+--> Get Current Entity: EntityReadHandler.get_entity(entity_id, vitess, s3)
+--> Extract Term Type: labels or descriptions from URL path
+--> Check Term Exists: entity_data[term_type].get(language_code) is not None
|    +--> If Term Doesn't Exist: Return current entity (idempotent success)
|    +--> If Term Exists: Continue deletion
+--> Remove Term from Entity Data: del entity_data[term_type][language_code]
+--> Calculate New Revision ID: head_revision_id + 1
+--> Prepare Revision Data: copy entity_data, set edit_type="term_delete"
+--> Hash Entity Content: MetadataExtractor.hash_entity(entity_data)
+--> Process Term Storage Updates:
|    +--> For Labels: Remove from Vitess entity_terms table
|    |    +--> Query existing hash for language: SELECT hash FROM entity_terms
|    |    |                                      WHERE term_type='label' AND language=?
|    |    +--> Delete from entity_terms: DELETE FROM entity_terms WHERE hash = ?
|    |    +--> Remove from revision labels_hashes: del revision_data["labels_hashes"][language_code]
|    +--> For Descriptions: Remove from S3 metadata storage
|    |    +--> Load current description metadata from S3
|    |    +--> Remove language entry: del metadata[language_code]
|    |    +--> Write updated metadata back to S3
|    |    +--> Remove from revision descriptions_hashes: del revision_data["descriptions_hashes"][language_code]
+--> Write Revision to S3: s3.write_revision(entity_id, new_revision_id, revision_data)
+--> Update Vitess Revision Table: vitess.create_revision(entity_id, new_revision_id, revision_data)
+--> Update Head Pointer: vitess.update_head_revision(entity_id, new_revision_id)
+--> Publish Change Event: stream_producer.publish_change(TERM_DELETE event)
+--> Return EntityResponse with updated entity data

## Term DELETE Validation

[Entitybase DELETE endpoint validation]
+--> Validate Entity ID: matches /^[A-Z]\d+$/
+--> Validate Language Code: matches /^[a-z-]+$/
+--> Validate Term Type: in ['labels', 'descriptions']
+--> Check Entity State: not deleted, not locked/archived
+--> Check User Permissions: can modify entity

## Wikibase API Redirect

[Wikibase DELETE /entities/{type}/{id}/labels/{lang} or /descriptions/{lang} - wikibase/v1/*.py]
+--> Receive Wikibase DELETE request
+--> Return 307 Redirect to: /entitybase/v1/entities/{type}/{id}/{term_type}/{lang}
+--> Preserve DELETE method

## Error Handling

+--> Entity Not Found: 404 Not Found
+--> Entity Deleted: 410 Gone
+--> Entity Locked/Archived: 409 Conflict
+--> Invalid Language Code: 400 Bad Request
+--> Permission Denied: 403 Forbidden
+--> Storage Failure: 500 Internal Server Error

## Key Differences from Term PATCH

- **Complete Removal**: Deletes entire language entry vs partial array modification
- **No JSON Patch**: Simple key deletion vs complex operation application
- **Storage Cleanup**: Removes term entries entirely vs updating arrays
- **Idempotent**: Safe to delete non-existent terms
- **Term Type Scope**: Applies to labels/descriptions, not aliases

## Performance Characteristics

- **Read Operations**: 1 entity read, 1 S3 revision fetch
- **Write Operations**: 1 S3 revision write, 1 Vitess term delete (for labels)
- **Hash Calculations**: Full entity re-hash (simpler than PATCH selective updates)
- **Storage Impact**: Complete term removal vs array element modification

## Relationship to Term PATCH

- **Labels/Descriptions**: DELETE removes entire language entry
- **Aliases**: PATCH modifies array contents (no DELETE for aliases)
- **Use Cases**:
| Operation | Labels/Descriptions | Aliases |
|-----------|-------------------|---------|
| Remove Language | DELETE /labels/{lang} | PATCH with remove operations |
| Clear All | DELETE /labels/{lang} | PATCH remove all elements |
| Selective Edit | N/A | PATCH add/remove/replace |

Note: Term DELETE provides complete language-level removal for labels and descriptions, while PATCH handles granular alias modifications. Both follow entity update patterns with selective storage cleanup and full revision history preservation.