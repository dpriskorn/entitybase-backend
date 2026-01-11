# TERM PATCH WRITE PATH

## Term PATCH Path (JSON Patch Operations on Aliases)

[Entitybase PATCH /entities/{type}/{id}/aliases/{lang} - entitybase/v1/*.py]
+--> Receive PATCH Request with JSON Patch payload
|    +--> Extract patch: request["patch"] array
|    +--> Validate patch format and operations
+--> Validate Clients: vitess and s3 initialized
+--> Check Entity Exists: vitess.entity_exists(entity_id) == True
+--> Check Not Deleted: vitess.is_entity_deleted(entity_id) == False
+--> Check Permissions: not archived/locked/mass_edit_protected
+--> Get Current Entity: EntityReadHandler.get_entity(entity_id, vitess, s3)
+--> Extract Current Aliases: entity_data["aliases"].get(language_code, [])
+--> For Each Patch Operation in patch array:
|    +--> Validate Operation: op in ["add", "remove", "replace"]
|    +--> Parse Path: path (e.g., "/-", "/0", "/1")
|    +--> Validate Path Format: "/" + (index | "-")
|    +--> Apply Operation to aliases array:
|    |    +--> If op == "add":
|    |    |    +--> If path == "/-": aliases.append(value)
|    |    |    +--> Else: aliases.insert(int(path[1:]), value)
|    |    +--> If op == "remove":
|    |    |    +--> index = int(path[1:])
|    |    |    +--> If 0 <= index < len(aliases): aliases.pop(index)
|    |    +--> If op == "replace":
|    |    |    +--> index = int(path[1:])
|    |    |    +--> If 0 <= index < len(aliases): aliases[index] = value
+--> Update Entity Data: entity_data["aliases"][language_code] = aliases
+--> Calculate New Revision ID: head_revision_id + 1
+--> Prepare Revision Data: copy entity_data, set edit_type="term_patch"
+--> Hash Entity Content: MetadataExtractor.hash_entity(entity_data)
+--> Process Term Storage Updates:
|    +--> For Labels: No change (read-only in this operation)
|    +--> For Descriptions: No change (read-only in this operation)
|    +--> For Aliases: Update Vitess entity_terms table
|    |    +--> For Added/Replaced Aliases: hash_string(alias) → insert_term(hash, alias, "alias")
|    |    +--> For Removed Aliases: Query existing hashes → remove from entity_terms if ref_count == 0
|    |    +--> Update revision aliases_hashes: {language_code: [hash1, hash2, ...]}
+--> Write Revision to S3: s3.write_revision(entity_id, new_revision_id, revision_data)
+--> Update Vitess Revision Table: vitess.create_revision(entity_id, new_revision_id, revision_data)
+--> Update Head Pointer: vitess.update_head_revision(entity_id, new_revision_id)
+--> Publish Change Event: stream_producer.publish_change(TERM_PATCH event)
+--> Return EntityResponse with updated entity data

## Term PATCH Validation

[Entitybase PATCH endpoint validation]
+--> Validate Entity ID: matches /^[A-Z]\d+$/
+--> Validate Language Code: matches /^[a-z-]+$/
+--> Validate Patch Array: list of dicts
+--> Validate Each Operation:
|    +--> Required: "op", "path"
|    +--> Conditional: "value" for add/replace operations
|    +--> op: in ["add", "remove", "replace"]
|    +--> path: matches /^\/(\d+|-)$/
+--> Check Array Bounds: for index-based operations, 0 <= index < len(current_aliases)

## Wikibase API Redirect

[Wikibase PATCH /entities/{type}/{id}/aliases/{lang} - wikibase/v1/*.py]
+--> Receive Wikibase-format PATCH request
+--> Return 307 Redirect to: /entitybase/v1/entities/{type}/{id}/aliases/{lang}
+--> Preserve request body and method

## Error Handling

+--> Invalid Patch Format: 400 Bad Request - "Invalid JSON Patch operation"
+--> Entity Not Found: 404 Not Found
+--> Permission Denied: 403 Forbidden
+--> Array Index Out of Bounds: 400 Bad Request - "Invalid array index"
+--> Unsupported Operation: 400 Bad Request - "Unsupported patch operation"
+--> Storage Failure: 500 Internal Server Error

## Key Differences from Full Entity Update

- **Targeted Modification**: Only aliases for one language are modified
- **JSON Patch Semantics**: Partial updates vs full replacement
- **Validation Complexity**: Array index validation + operation validation
- **Storage Updates**: Selective term storage updates vs full re-hash
- **Event Type**: TERM_PATCH vs ENTITY_UPDATE

## Performance Characteristics

- **Read Operations**: 1 entity read, 1 S3 revision fetch
- **Write Operations**: 1 S3 revision write, N Vitess term inserts/deletes
- **Hash Calculations**: Only for modified aliases, not entire entity
- **Revision Creation**: Same as entity update but with selective term processing

Note: Term PATCH operations follow entity update patterns but with JSON Patch semantics for precise alias modifications. This provides fine-grained control while maintaining revision history and deduplication benefits.