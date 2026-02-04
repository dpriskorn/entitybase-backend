import shutil
import os

files_to_rename = [
    ('tests/unit/models/rdf_builder/ontology/test_datatypes.py', 'tests/unit/models/rdf_builder/ontology/test_ontology_datatypes.py'),
    ('tests/unit/models/rest_api/entitybase/v1/endpoints/test_qualifiers.py', 'tests/unit/models/rest_api/entitybase/v1/endpoints/test_lexeme_qualifiers.py'),
    ('tests/unit/models/rest_api/entitybase/v1/endpoints/test_references.py', 'tests/unit/models/rest_api/entitybase/v1/endpoints/test_lexeme_references.py'),
    ('tests/unit/models/rest_api/entitybase/v1/endpoints/test_statements.py', 'tests/unit/models/rest_api/entitybase/v1/endpoints/test_lexeme_statements.py'),
    ('tests/unit/models/rest_api/entitybase/v1/endpoints/test_watchlist.py', 'tests/unit/models/rest_api/entitybase/v1/endpoints/test_entity_watchlist.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/lexeme/test_update.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/lexeme/test_lexeme_update.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/property/test_create.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/property/test_property_create.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/property/test_update.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/property/test_property_update.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/lexeme/test_create.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/lexeme/test_lexeme_create.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_create.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_entity_create.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_update.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_entity_update.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_exceptions.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_entity_exceptions.py'),
    ('tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_redirect.py', 'tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_entity_redirect.py'),
    ('tests/unit/models/workers/watchlist_consumer/test_main.py', 'tests/unit/models/workers/watchlist_consumer/test_watchlist_consumer.py'),
]

for old, new in files_to_rename:
    if os.path.exists(old):
        shutil.move(old, new)
        print(f'Moved: {old} -> {new}')
    else:
        print(f'Not found: {old}')
