#!/usr/bin/env python3
import os

# Files to delete (old duplicate files)
files_to_delete = [
    'tests/unit/models/rdf_builder/ontology/test_datatypes.py',
    'tests/unit/models/rest_api/entitybase/v1/endpoints/test_qualifiers.py',
    'tests/unit/models/rest_api/entitybase/v1/endpoints/test_references.py',
    'tests/unit/models/rest_api/entitybase/v1/endpoints/test_statements.py',
    'tests/unit/models/rest_api/entitybase/v1/endpoints/test_watchlist.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/lexeme/test_update.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/property/test_create.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/property/test_update.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/lexeme/test_create.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_create.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_update.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_exceptions.py',
    'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_redirect.py',
    'tests/unit/models/workers/watchlist_consumer/test_main.py',
]

print("FILES TO DELETE (old duplicates):")
print("=" * 60)
for filepath in files_to_delete:
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"DELETED: {filepath}")
    else:
        print(f"NOT FOUND: {filepath}")
