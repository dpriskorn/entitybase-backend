# Statement Processing Paths

## Statement Addition Path (During Entity Create/Update)

```
[Process Statements - update.py / statement_service.py]
+--> Extract Claims: entity_data["claims"]
+--> Extract Properties: StatementExtractor.extract_properties_from_claims(claims)
+--> Compute Property Counts: StatementExtractor.compute_property_counts_from_claims(claims)
+--> For Each Property in Claims:
|    +--> For Each Statement in Property:
|    |    +--> Validate Statement (if validator provided)
|    |    +--> Hash Statement: StatementHasher.compute_hash(statement)
|    |    +--> Deduplicate and Store: deduplicate_and_store_statements()
|    |    |    +--> Check Existence: vitess.statement_exists(hash)
|    |    |    +--> If Not Exists: s3.write_statement(hash, statement_data)
|    |    |    +--> vitess.insert_statement_content(hash, ref_count=1)
|    |    |    +--> Else: vitess.increment_ref_count(hash)
|    |    +--> Collect Hash for Entity Revision
+--> Store in Revision: properties, property_counts, statements (hashes)
```

## Statement Modification Path (During Entity Update)

```
[Process Statements - update.py / statement_service.py]
+--> Extract New Claims: entity_data["claims"]
+--> Extract New Properties: StatementExtractor.extract_properties_from_claims(claims)
+--> Compute New Property Counts: StatementExtractor.compute_property_counts_from_claims(claims)
+--> Compare with Previous Revision
+--> For Modified Statements:
|    +--> Treat as Removal + Addition
|    +--> Decrement Old Hash: vitess.decrement_ref_count(old_hash)
|    +--> If ref_count == 0: s3.delete_statement(old_hash)
|    +--> Hash New Statement: StatementHasher.compute_hash(new_statement)
|    +--> Deduplicate and Store New: deduplicate_and_store_statements()
+--> Store Updated Revision: new properties, property_counts, statements
```

## Statement Removal Path (During Entity Update)

```
[Process Statements - update.py / statement_service.py]
+--> Extract New Claims: entity_data["claims"] (potentially with removed statements)
+--> Compare with Previous Claims
+--> For Removed Statements:
|    +--> Decrement Ref Count: vitess.decrement_ref_count(hash)
|    +--> If ref_count == 0: s3.delete_statement(hash)
|    +--> vitess.delete_statement_content(hash)
+--> Extract Properties: StatementExtractor.extract_properties_from_claims(claims)
+--> Compute Property Counts: StatementExtractor.compute_property_counts_from_claims(claims)
+--> Store Updated Revision: properties, property_counts, statements
```

## Shared Deduplication Logic

```
[deduplicate_and_store_statements - statement_service.py]
+--> For Each Statement Hash:
|    +--> Validate Statement Schema (if validator)
|    +--> Check S3 Existence: s3.statement_exists(hash)
|    +--> If Not in S3: s3.write_statement(hash, statement_data)
|    +--> Check Vitess Existence: vitess.statement_exists(hash)
|    +--> If Not in Vitess: vitess.insert_statement_content(hash, ref_count=1)
|    +--> Else: vitess.increment_ref_count(hash)
```

Note: All statement operations occur within entity updates. Individual statement CRUD is not supported; statements are managed as part of entity revisions with reference counting for deduplication.