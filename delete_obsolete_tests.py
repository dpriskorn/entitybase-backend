#!/usr/bin/env python3
"""Script to delete obsolete test files causing pytest import conflicts."""
import os

files_to_delete = [
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/infrastructure/test_client.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/infrastructure/test_client_old.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/infrastructure/vitess/test_client.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_update.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/rest_api/entitybase/v1/handlers/entity/test_update_old.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/rest_api/entitybase/v1/handlers/entity/items/test_update.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/rest_api/entitybase/v1/handlers/entity/items/test_update_old.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/workers/test_watchlist_consumer.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/workers/test_watchlist_consumer_old.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/workers/watchlist_consumer/test_watchlist_consumer.py',
    '/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/workers/watchlist_consumer/test_watchlist_consumer_old.py',
]

for f in files_to_delete:
    if os.path.exists(f):
        os.remove(f)
        print(f'Deleted: {f}')
    else:
        print(f'Not found: {f}')
print('Done!')
