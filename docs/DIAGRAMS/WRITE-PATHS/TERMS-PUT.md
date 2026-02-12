# TERM PUT WRITE PATH

## Term PUT Path (Setting Labels/Descriptions for Language)

[Entitybase PUT /entities/{type}/{id}/labels/{lang} or /descriptions/{lang} - entitybase/v1/*.py]
+--> Receive PUT Request with term data payload
|    +--> For Labels: Extract "value" field from request
|    +--> For Descriptions: Extract "description" field from Wikibase format
+--> Validate Clients: vitess and s3 initialized
+--> Check Entity Exists: vitess.entity_exists(entity_id) == True
+--> Check Not Deleted: vitess.is_entity_deleted(entity_id) == False
+--> Check Permissions: not archived/locked/mass_edit_protected
+--> Get Current Entity: EntityReadHandler.get_entity(entity_id, vitess, s3)
+--> Extract Term Type: labels or descriptions from URL path
+--> Validate Term Data: check required fields and format
+--> Update Entity Data: entity_data[term_type][language_code] = new_term_value
+--> Calculate New Revision ID: head_revision_id + 1
+--> Prepare Revision Data: copy entity_data, set edit_type="term_put"
+--> Hash Entity Content: MetadataExtractor.hash_entity(entity_data)
+--> Process Term Storage Updates:
|    +--> For Labels: Update Vitess entity_terms table
|    |    +--> Hash new label: hash_string(new_label_value)
|    |    +--> Insert/update in entity_terms: INSERT ... ON DUPLICATE KEY
|    |    +--> Update revision labels_hashes: {language_code: new_hash}
|    +--> For Descriptions: Update S3 metadata storage
|    |    +--> Hash new description: hash_string(new_description_value)
|    |    +--> Store in S3: s3.write_metadata("descriptions", hash, description_value)
|    |    +--> Update revision descriptions_hashes: {language_code: new_hash}
+--> Write Revision to S3: s3.write_revision(entity_id, new_revision_id, revision_data)
+--> Update Vitess Revision Table: vitess.create_revision(entity_id, new_revision_id, revision_data)
+--> Update Head Pointer: vitess.update_head_revision(entity_id, new_revision_id)
+--> Publish Change Event: stream_producer.publish_change(TERM_PUT event)
+--> Return EntityResponse with updated entity data

## Term PUT Validation

[Entitybase PUT endpoint validation]
+--> Validate Entity ID: matches /^[A-Z]\d+$/
+--> Validate Language Code: matches /^[a-z-]+$/
+--> Validate Term Type: in ['labels', 'descriptions']
+--> Validate Request Body:
|    +--> For Labels: {"value": "string"} (1-250 chars)
|    +--> For Descriptions: {"description": "string", "tags": [...], "bot": bool, "comment": "string"} (1-500 chars)
+--> Check Entity State: not deleted, not locked/archived
+--> Check User Permissions: can modify entity

## Wikibase API Redirect

[Wikibase PUT /entities/{type}/{id}/labels/{lang} or /descriptions/{lang} - wikibase/v1/*.py]
+--> Receive Wikibase PUT request with full payload
+--> Return 307 Redirect to: /entitybase/v1/entities/{type}/{id}/{term_type}/{lang}
+--> Preserve request body and PUT method

## Request Format Examples

### Labels PUT
```json
{
  "value": "English mathematician and writer",
  "tags": [],
  "bot": false,
  "comment": "set English label"
}
```

### Descriptions PUT (Wikibase format)
```json
{
  "description": "the subject is a concrete object (instance) of this class, category, or object group",
  "tags": [],
  "bot": false,
  "comment": "set English description"
}
```

## Error Handling

+--> Entity Not Found: 404 Not Found
+--> Entity Deleted: 410 Gone
+--> Entity Locked/Archived: 409 Conflict
+--> Invalid Request Format: 400 Bad Request
+--> Term Value Too Long: 400 Bad Request
+--> Permission Denied: 403 Forbidden
+--> Storage Failure: 500 Internal Server Error

## Key Differences from PATCH Operations

- **Complete Replacement**: PUT replaces entire term value vs PATCH partial modifications
- **Simple Validation**: Direct value validation vs JSON Patch operation validation
- **Storage Updates**: Full term replacement in storage vs selective updates
- **Use Cases**:
| Operation | Labels/Descriptions | Aliases |
|-----------|-------------------|---------|
| Set/Replace | PUT /labels/{lang} | PATCH add/replace operations |
| Partial Edit | N/A | PATCH operations |
| Language Add | PUT (creates if missing) | PATCH add operations |

## Performance Characteristics

- **Read Operations**: 1 entity read, 1 S3 revision fetch
- **Write Operations**: 1 S3 revision write, 1 Vitess term insert (for labels)
- **Hash Calculations**: Full entity re-hash + individual term hash
- **Storage Impact**: New term storage + updated revision metadata

## Relationship to Other Term Operations

- **GET**: Retrieve term value
- **PUT**: Set/replace entire term value
- **PATCH**: Apply partial modifications (aliases only)
- **DELETE**: Remove term entirely

Note: Term PUT provides complete value replacement for labels and descriptions, following entity update patterns with selective term storage management and full revision history preservation.